# إعدادات الاتصال بقاعدة بيانات MongoDB
import os
from pathlib import Path

# تحميل متغيرات البيئة من .env.local تلقائيًا عند التشغيل المحلي
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env.local'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # لو مكتبتش python-dotenv، تجاهل بدون خطأ

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'cadoz')
COLLECTION_NAME = os.environ.get('COLLECTION_NAME', 'products')
