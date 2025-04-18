from pydantic import BaseModel
from typing import List

class ProductSuggestionRequest(BaseModel):
    question: str
    top_k: int = 3
    session_id: str = None  # لدعم تتبع الجلسة

class ProductSuggestionResponse(BaseModel):
    name: str
    description: str
    price: float
    image: str
    score: float
    tags: list = []
    occasion: list = []
    season: list = []
    seasons: list = []
    category: str = ''
    subCategory: str = ''
    brand: str = ''

class ProductSuggestionFullResponse(BaseModel):
    message: str
    products: List[ProductSuggestionResponse]
