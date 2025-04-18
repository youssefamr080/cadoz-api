"""
session.py - مدير جلسات متقدم لتطبيقات الويب وبوتات الدردشة

هذا الملف يوفر نظام إدارة جلسات قوي ومرن يمكنه:
- إنشاء وإدارة جلسات المستخدمين (sessions) بشكل آمن وفعال
- دعم تخزين بيانات السياق المتقدمة (context data)
- السماح بالتبديل السهل بين خيارات التخزين المختلفة (ذاكرة، قاعدة بيانات، Redis)
- توفير واجهة استخدام بسيطة ومتسقة وآمنة

مناسب للاستخدام في بيئات الإنتاج وتطبيقات متعددة المستخدمين.
"""

import uuid
import time
import threading
import logging
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from abc import ABC, abstractmethod

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("session_manager")

class SessionStorageBackend(ABC):
    """
    واجهة مجردة لخلفيات تخزين الجلسات. يجب تنفيذ هذه الواجهة لأي آلية تخزين جديدة.
    """
    
    @abstractmethod
    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """استرجاع بيانات الجلسة المحفوظة"""
        pass
    
    @abstractmethod
    def save(self, session_id: str, data: Dict[str, Any]) -> bool:
        """حفظ بيانات الجلسة"""
        pass
    
    @abstractmethod
    def delete(self, session_id: str) -> bool:
        """حذف جلسة"""
        pass
    
    @abstractmethod
    def list_all(self) -> List[str]:
        """إرجاع قائمة بجميع معرفات الجلسات النشطة"""
        pass
    
    @abstractmethod
    def clean_expired(self, max_age_seconds: int) -> int:
        """حذف الجلسات منتهية الصلاحية"""
        pass

class InMemorySessionStorage(SessionStorageBackend):
    """
    تخزين الجلسات في الذاكرة باستخدام dictionary.
    سريع للغاية ولكنه غير دائم - البيانات تُفقد عند إعادة تشغيل الخادم.
    """
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()  # استخدام RLock للتعامل مع العمليات المتداخلة
    
    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        استرجاع بيانات الجلسة من الذاكرة
        
        Args:
            session_id: معرف الجلسة الفريد
            
        Returns:
            بيانات الجلسة أو None إذا لم تكن موجودة
        """
        with self._lock:
            return self._sessions.get(session_id, None)
    
    def save(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        حفظ بيانات الجلسة في الذاكرة
        
        Args:
            session_id: معرف الجلسة الفريد
            data: بيانات الجلسة للحفظ
            
        Returns:
            True في حالة النجاح
        """
        with self._lock:
            self._sessions[session_id] = data
            return True
    
    def delete(self, session_id: str) -> bool:
        """
        حذف جلسة من الذاكرة
        
        Args:
            session_id: معرف الجلسة الفريد
            
        Returns:
            True إذا تم الحذف، False إذا لم تكن الجلسة موجودة
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False
    
    def list_all(self) -> List[str]:
        """
        إرجاع قائمة بجميع معرفات الجلسات النشطة
        
        Returns:
            قائمة بمعرفات الجلسات
        """
        with self._lock:
            return list(self._sessions.keys())
    
    def clean_expired(self, max_age_seconds: int) -> int:
        """
        حذف الجلسات منتهية الصلاحية
        
        Args:
            max_age_seconds: العمر الأقصى للجلسة بالثواني
            
        Returns:
            عدد الجلسات التي تم حذفها
        """
        current_time = time.time()
        expired_sessions = []
        
        with self._lock:
            for session_id, data in self._sessions.items():
                last_accessed = data.get('last_accessed', 0)
                if current_time - last_accessed > max_age_seconds:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self._sessions[session_id]
        
        if expired_sessions:
            logger.info(f"تم حذف {len(expired_sessions)} جلسة منتهية الصلاحية")
        
        return len(expired_sessions)

class SessionManager:
    """
    مدير جلسات متقدم يوفر واجهة موحدة لإنشاء وإدارة الجلسات.
    
    يدعم:
    - توليد معرفات جلسات فريدة وآمنة
    - تخزين بيانات سياق المحادثة
    - التعامل مع تفضيلات المستخدم
    - التبديل بين آليات التخزين المختلفة
    """
    
    DEFAULT_EXPIRY = 86400  # انتهاء الصلاحية الافتراضي: يوم واحد بالثواني
    CLEANUP_INTERVAL = 3600  # فاصل التنظيف: ساعة واحدة بالثواني
    
    def __init__(self, storage_backend: Optional[SessionStorageBackend] = None):
        """
        تهيئة مدير الجلسات
        
        Args:
            storage_backend: خلفية التخزين المستخدمة (InMemorySessionStorage افتراضيًا)
        """
        self.storage = storage_backend or InMemorySessionStorage()
        self.last_cleanup = time.time()
        self._lock = threading.RLock()
    
    def _generate_session_id(self) -> str:
        """
        توليد معرف جلسة فريد وآمن
        
        Returns:
            معرف الجلسة الفريد كسلسلة نصية
        """
        return str(uuid.uuid4())
    
    def _maybe_cleanup_expired(self) -> None:
        """تنظيف الجلسات منتهية الصلاحية إذا مر وقت كافٍ منذ آخر تنظيف"""
        current_time = time.time()
        with self._lock:
            if current_time - self.last_cleanup > self.CLEANUP_INTERVAL:
                self.storage.clean_expired(self.DEFAULT_EXPIRY)
                self.last_cleanup = current_time
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        إنشاء جلسة جديدة
        
        Args:
            user_id: معرف المستخدم (اختياري)
            
        Returns:
            معرف الجلسة الجديد
            
        Example:
            >>> session_manager = SessionManager()
            >>> session_id = session_manager.create_session("user123")
            >>> print(session_id)
            '3f7c8e9a-2b5d-4f1c-a6b0-9e8d7c6b5a4f'
        """
        session_id = self._generate_session_id()
        
        # بيانات الجلسة الأساسية
        session_data = {
            'created_at': time.time(),
            'last_accessed': time.time(),
            'user_id': user_id,
            'context': {
                'last_message': None,
                'preferences': {},
                'history': []
            },
            'metadata': {
                'user_agent': None,
                'ip_address': None,
                'session_count': 1
            }
        }
        
        self.storage.save(session_id, session_data)
        logger.info(f"تم إنشاء جلسة جديدة: {session_id}" + (f" للمستخدم: {user_id}" if user_id else ""))
        
        # تنظيف الجلسات المنتهية إذا لزم الأمر
        self._maybe_cleanup_expired()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        استرجاع بيانات الجلسة
        
        Args:
            session_id: معرف الجلسة
            
        Returns:
            بيانات الجلسة أو None إذا لم تكن موجودة
            
        Example:
            >>> session_manager = SessionManager()
            >>> session_id = session_manager.create_session()
            >>> session = session_manager.get_session(session_id)
            >>> print(session['created_at'] > 0)
            True
        """
        session_data = self.storage.get(session_id)
        
        if session_data:
            # تحديث وقت آخر وصول
            session_data['last_accessed'] = time.time()
            self.storage.save(session_id, session_data)
            return session_data
        
        logger.warning(f"محاولة الوصول إلى جلسة غير موجودة: {session_id}")
        return None
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        تحديث بيانات الجلسة
        
        Args:
            session_id: معرف الجلسة
            data: البيانات الجديدة للدمج مع البيانات الحالية
            
        Returns:
            True إذا تم التحديث بنجاح، False إذا لم تكن الجلسة موجودة
            
        Example:
            >>> session_manager = SessionManager()
            >>> session_id = session_manager.create_session()
            >>> success = session_manager.update_session(session_id, {
            ...     'context': {'last_message': 'مرحبا'}
            ... })
            >>> print(success)
            True
        """
        session_data = self.storage.get(session_id)
        
        if not session_data:
            logger.warning(f"محاولة تحديث جلسة غير موجودة: {session_id}")
            return False
        
        # تحديث البيانات بشكل تدريجي للمحافظة على البنية
        def update_nested_dict(original, updates):
            for key, value in updates.items():
                if key in original and isinstance(original[key], dict) and isinstance(value, dict):
                    update_nested_dict(original[key], value)
                else:
                    original[key] = value
        
        update_nested_dict(session_data, data)
        session_data['last_accessed'] = time.time()
        
        self.storage.save(session_id, session_data)
        return True
    
    def update_context(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        """
        تحديث بيانات السياق للجلسة
        
        Args:
            session_id: معرف الجلسة
            context_updates: تحديثات السياق
            
        Returns:
            True إذا تم التحديث بنجاح، False إذا لم تكن الجلسة موجودة
            
        Example:
            >>> session_manager = SessionManager()
            >>> session_id = session_manager.create_session()
            >>> session_manager.update_context(session_id, {
            ...     'last_message': 'مرحبا',
            ...     'preferences': {'language': 'ar'}
            ... })
        """
        return self.update_session(session_id, {'context': context_updates})
    
    def add_message_to_history(self, session_id: str, message: Dict[str, Any]) -> bool:
        """
        إضافة رسالة إلى سجل المحادثة
        
        Args:
            session_id: معرف الجلسة
            message: الرسالة (dict مع 'role', 'content', وغيرها)
            
        Returns:
            True إذا تمت الإضافة بنجاح، False إذا لم تكن الجلسة موجودة
            
        Example:
            >>> session_manager = SessionManager()
            >>> session_id = session_manager.create_session()
            >>> session_manager.add_message_to_history(session_id, {
            ...     'role': 'user',
            ...     'content': 'كيف يمكنني العثور على هدية مناسبة؟',
            ...     'timestamp': time.time()
            ... })
        """
        session_data = self.storage.get(session_id)
        
        if not session_data:
            logger.warning(f"محاولة إضافة رسالة لجلسة غير موجودة: {session_id}")
            return False
        
        # التأكد من وجود التاريخ وأنه قائمة
        if 'history' not in session_data['context']:
            session_data['context']['history'] = []
        
        # إضافة الرسالة إلى السجل
        if 'timestamp' not in message:
            message['timestamp'] = time.time()
        
        session_data['context']['history'].append(message)
        session_data['context']['last_message'] = message
        session_data['last_accessed'] = time.time()
        
        self.storage.save(session_id, session_data)
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        حذف جلسة
        
        Args:
            session_id: معرف الجلسة
            
        Returns:
            True إذا تم الحذف بنجاح، False إذا لم تكن الجلسة موجودة
            
        Example:
            >>> session_manager = SessionManager()
            >>> session_id = session_manager.create_session()
            >>> session_manager.delete_session(session_id)
            True
        """
        result = self.storage.delete(session_id)
        if result:
            logger.info(f"تم حذف الجلسة: {session_id}")
        else:
            logger.warning(f"محاولة حذف جلسة غير موجودة: {session_id}")
        return result
    
    def list_active_sessions(self) -> List[str]:
        """
        قائمة بجميع الجلسات النشطة
        
        Returns:
            قائمة بمعرفات الجلسات النشطة
            
        Example:
            >>> session_manager = SessionManager()
            >>> session_manager.create_session()
            >>> session_manager.create_session()
            >>> len(session_manager.list_active_sessions())
            2
        """
        return self.storage.list_all()
    
    def session_exists(self, session_id: str) -> bool:
        """
        التحقق من وجود جلسة
        
        Args:
            session_id: معرف الجلسة
            
        Returns:
            True إذا كانت الجلسة موجودة، False إذا لم تكن موجودة
        """
        return self.storage.get(session_id) is not None
    
    def export_session(self, session_id: str) -> Optional[str]:
        """
        تصدير بيانات الجلسة كـ JSON
        
        Args:
            session_id: معرف الجلسة
            
        Returns:
            سلسلة JSON أو None إذا لم تكن الجلسة موجودة
            
        Example:
            >>> session_manager = SessionManager()
            >>> session_id = session_manager.create_session()
            >>> json_data = session_manager.export_session(session_id)
            >>> isinstance(json_data, str)
            True
        """
        session_data = self.storage.get(session_id)
        if not session_data:
            return None
        
        # تحويل الطوابع الزمنية إلى صيغة مقروءة
        json_data = {}
        for key, value in session_data.items():
            if key in ['created_at', 'last_accessed']:
                json_data[key] = datetime.fromtimestamp(value).isoformat()
            else:
                json_data[key] = value
        
        return json.dumps(json_data, ensure_ascii=False, indent=2)


# ================== أمثلة للاستخدام ==================

def usage_example():
    """مثال بسيط لاستخدام مدير الجلسات"""
    # إنشاء مدير الجلسات
    session_manager = SessionManager()
    
    # إنشاء جلسة جديدة
    session_id = session_manager.create_session(user_id="user123")
    print(f"تم إنشاء جلسة جديدة: {session_id}")
    
    # تحديث سياق الجلسة
    session_manager.update_context(session_id, {
        'preferences': {
            'language': 'ar',
            'price_range': {'min': 100, 'max': 500},
            'interests': ['تكنولوجيا', 'كتب']
        }
    })
    
    # إضافة رسالة للمحادثة
    session_manager.add_message_to_history(session_id, {
        'role': 'user',
        'content': 'أبحث عن هدية لصديق يحب التكنولوجيا'
    })
    
    # استرجاع الجلسة
    session = session_manager.get_session(session_id)
    print(f"تفضيلات المستخدم: {session['context']['preferences']}")
    print(f"آخر رسالة: {session['context']['last_message']['content']}")
    
    # تصدير الجلسة كـ JSON
    json_data = session_manager.export_session(session_id)
    print(f"بيانات الجلسة: {json_data[:100]}...")
    
    # حذف الجلسة
    session_manager.delete_session(session_id)
    print(f"تم حذف الجلسة: {session_id}")


# تشغيل مثال الاستخدام عند تنفيذ الملف مباشرةً
if __name__ == "__main__":
    usage_example()