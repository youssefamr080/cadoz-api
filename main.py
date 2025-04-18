from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models import ProductSuggestionRequest, ProductSuggestionFullResponse
from logic import suggest_products_logic
from understanding import extract_context
from responses import generate_response

from db import products_collection
import traceback

# إعداد تطبيق FastAPI مع وصف شامل
app = FastAPI(
    title="Cadoz Smart Shopping Assistant",
    description="API لتوفير توصيات منتجات مخصصة بناءً على استفسارات المستخدمين.",
    version="1.0.0",
)

# إعداد CORS للسماح للواجهة الأمامية بالوصول للـ API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://www.elhoda-center.store"],  # يمكنك وضع رابط موقعك فقط هنا لزيادة الأمان
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# نموذج لفحص صحة السيرفر
class HealthCheck(BaseModel):
    status: str

# معالج الأخطاء العام
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "حدث خطأ داخلي. يرجى المحاولة لاحقًا.", "detail": str(exc)},
    )

# Endpoint لفحص صحة السيرفر
@app.get("/health", response_model=HealthCheck, summary="فحص صحة السيرفر")
def health_check():
    """فحص حالة السيرفر للتأكد من أنه يعمل بشكل صحيح."""
    return {"status": "healthy"}

# Endpoint للحصول على توصيات المنتجات
@app.post("/suggest", response_model=ProductSuggestionFullResponse, summary="الحصول على توصيات المنتجات")
def suggest_products(req: ProductSuggestionRequest):
    """
    يستقبل استفسار المستخدم ويعيد توصيات منتجات مخصصة بناءً على السياق المستخرج.
    
    Args:
        req: طلب يحتوي على استفسار المستخدم ومعرف الجلسة (اختياري).
    
    Returns:
        رد يحتوي على رسالة ودية وقائمة بالمنتجات المقترحة.
    """
    try:
        # استخراج السياق من السؤال
        context = extract_context(req.question)
        
        # الحصول على التوصيات باستخدام السياق
        suggestions = suggest_products_logic(
            req.question,
            top_k=req.top_k,
            session_id=req.session_id
        )
        
        # توليد الرد الودي
        response_message = generate_response(context, suggestions)
        
        # تسجيل الجلسة
        session_id = req.session_id if hasattr(req, 'session_id') else None
        
        # معالجة حالات الإرجاع غير المتوقعة من suggest_products_logic
        if isinstance(suggestions, dict):
            msg = suggestions.get('message', 'حصل مشكلة أثناء جلب المنتجات. جرب تاني!')
            products = suggestions.get('products', [])
            return ProductSuggestionFullResponse(
                message=msg,
                products=products
            )
        # إرجاع الرد الكامل
        return ProductSuggestionFullResponse(
            message=response_message,
            products=suggestions
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        tb = traceback.format_exc()
        print(f"خطأ في suggest_products: {e}\n{tb}")
        raise HTTPException(status_code=500, detail="حدث خطأ داخلي أثناء معالجة الطلب.")

# Endpoint الرئيسي
@app.get("/", summary="الصفحة الرئيسية")
def root():
    """يعيد رسالة ترحيبية بسيطة للمستخدم."""
    return {"message": "مرحبًا بك في وكيل متجر Cadoz الذكي!"}