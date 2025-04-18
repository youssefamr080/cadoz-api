"""
Logic module for Cadoz gift recommendation system
Enhanced version with improved context handling, personalization and response generation
"""
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from db import products_collection
from understanding import extract_context, extract_entities, analyze_sentiment
from responses import friendly_message, generate_response
from session import SessionManager
import numpy as np
import re
from functools import lru_cache
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('cadoz_recommender')

# Cache model loading to improve performance
@lru_cache(maxsize=1)
def get_embedding_model():
    """Load and cache the embedding model for semantic similarity"""
    logger.info("Loading embedding model")
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Fields to use for semantic similarity calculation
CONTENT_FIELDS = [
    'name', 'description', 'tags', 'occasion', 'season', 
    'seasons', 'category', 'subCategory', 'brand',
    'targetGender', 'ageGroup', 'interests'
]

# Weight factors for different fields to emphasize importance
FIELD_WEIGHTS = {
    'tags': 1.5,
    'occasion': 2.0,
    'category': 1.3,
    'subCategory': 1.2,
    'targetGender': 1.8,
    'ageGroup': 1.5,
    'interests': 1.7,
    'description': 1.0,
    'name': 0.8,
    'season': 1.3,
    'seasons': 1.3,
    'brand': 0.7
}

def join_fields(prod, fields, field_weights=None):
    """
    Join product fields with optional weighting for more important fields
    
    Args:
        prod: Product dictionary from database
        fields: List of fields to include
        field_weights: Optional dictionary of field weight multipliers
        
    Returns:
        String representation of product with weighted fields
    """
    result = []
    
    for field in fields:
        val = prod.get(field, '')
        if not val:
            continue
            
        # Apply field weighting by repeating important fields
        weight = 1
        if field_weights and field in field_weights:
            weight = int(field_weights[field])
            
        # Handle list fields (tags, occasions, etc.)
        if isinstance(val, list):
            field_values = [str(v) for v in val if v]
            # Repeat based on weight
            for _ in range(weight):
                result.extend(field_values)
        else:
            # Repeat based on weight
            for _ in range(weight):
                result.append(str(val))
                
    return ' '.join(result)

def is_meaningful_content(text):
    """
    Check if content is meaningful and not gibberish
    
    Args:
        text: Text to analyze
        
    Returns:
        Boolean indicating if content is valid and meaningful
    """
    if not text or len(text.strip()) < 3:
        return False
        
    # Text should have some reasonable word count
    if len(text.split()) < 2:
        return False
        
    # Avoid repeated characters (like "aaaaaaaa")
    if re.search(r'(.)\1{3,}', text):
        return False
        
    # Avoid purely numerical content
    if re.match(r'^[\d\s\.\-\,]+$', text):
        return False
        
    return True

def get_current_season():
    """Get current season based on date in Egypt"""
    month = datetime.now().month
    if 3 <= month <= 5:
        return "spring"
    elif 6 <= month <= 8:
        return "summer"
    elif 9 <= month <= 11:
        return "fall"
    else:
        return "winter"

def get_upcoming_occasions(days_ahead=30):
    """
    Get upcoming occasions within the specified days
    
    TODO: Implement with actual calendar of holidays and occasions in Egypt
    For now, hardcoded for demonstration
    """
    today = datetime.now()
    month = today.month
    
    upcoming = []
    # Example hardcoded occasions - replace with actual calendar lookup
    if month == 1:
        upcoming.append("new year")
    elif month == 2:
        upcoming.append("valentine")
    elif month == 3:
        upcoming.append("mother's day")
    elif month == 4:
        upcoming = ["ramadan", "eid"] if datetime.now().year % 3 == 0 else []
    elif month == 12:
        upcoming.append("christmas")
        
    return upcoming

def build_conversation_context(current_question, session_context, max_history=3):
    """
    Build an enhanced conversation context from session history
    
    Args:
        current_question: Current user question
        session_context: Session data dictionary
        max_history: Maximum number of previous interactions to include
        
    Returns:
        Enriched question text with conversation history
    """
    if not session_context:
        return current_question
        
    # Get conversation history
    history = session_context.get('question_history', [])
    
    # Add relevant previous context while limiting total length
    context_parts = []
    
    # Add user preferences if available
    user_prefs = session_context.get('user_preferences', {})
    if user_prefs:
        pref_strings = []
        if 'interested_in' in user_prefs:
            pref_strings.append(f"يحب/تحب: {', '.join(user_prefs['interested_in'])}")
        if 'occasions' in user_prefs:
            pref_strings.append(f"مناسبات: {', '.join(user_prefs['occasions'])}")
        if 'recipient_info' in user_prefs:
            pref_strings.append(f"معلومات عن المستلم: {user_prefs['recipient_info']}")
            
        if pref_strings:
            context_parts.append("[معلومات المستخدم: " + "; ".join(pref_strings) + "]")
    
    # Debug logging for history
    try:
        logger.info(f"[context] history: {history}, max_history: {max_history}")
        recent_history = history[-max_history:] if history else []
        logger.info(f"[context] recent_history: {recent_history}")
    except Exception as e:
        logger.error(f"Error slicing history: {e}, history={history}, max_history={max_history}")
        recent_history = []
    if recent_history:
        context_parts.append("[أسئلة سابقة: " + " ... ".join(recent_history) + "]")
    
    # Add current question
    context_parts.append(current_question)
    
    return " ".join(context_parts)

def extract_user_preferences(question, context=None):
    """
    Extract user preferences from the question
    
    Args:
        question: User question text
        context: Optional previous context
        
    Returns:
        Dictionary of extracted preferences
    """
    preferences = {}
    
    # Extract gender information
    if re.search(r'بنت|ست|زوج[تة]ي|أم|أخت|صاحبت|صديقت|خطيبت', question, re.IGNORECASE):
        preferences['gender'] = 'female'
    elif re.search(r'ولد|راجل|زوجي|أب|أخ|صاحب|صديق|خطيب', question, re.IGNORECASE):
        preferences['gender'] = 'male'
    
    # Extract age group (يدعم أيضًا السن بالأرقام)
    age_match = re.search(r'(\d+)', question)
    if re.search(r'طفل|بيبي|رضيع|أطفال', question, re.IGNORECASE):
        preferences['age_group'] = 'children'
    elif age_match and int(age_match.group(1)) < 14:
        preferences['age_group'] = 'children'
    elif re.search(r'مراهق|تين|المدرس[ةه]', question, re.IGNORECASE):
        preferences['age_group'] = 'teen'
    elif re.search(r'شاب|[ةه] الجامع[ةه]|تخرج', question, re.IGNORECASE):
        preferences['age_group'] = 'young_adult'
    elif re.search(r'كبير|مسن|عجوز', question, re.IGNORECASE):
        preferences['age_group'] = 'elderly'
    
    # Extract occasion
    occasions_mapping = {
        'عيد الأم': 'mothers_day',
        'عيد ميلاد': 'birthday',
        'زفاف|فرح|خطوب[ةه]': 'wedding',
        'رمضان': 'ramadan',
        'العيد|عيد الفطر|عيد الأضحى': 'eid',
        'تخرج': 'graduation',
        'فلانتين|الحب': 'valentine',
        'كريسماس': 'christmas',
        'السن[ةه] الجديد[ةه]': 'new_year'
    }
    
    for pattern, occasion in occasions_mapping.items():
        if re.search(pattern, question, re.IGNORECASE):
            preferences['occasion'] = occasion
            break
    
    # Extract interests
    interests_mapping = {
    'عطر|عطور|ريحة|perfume': 'perfumes',
    'محفظ[ةه]|wallet|فلوس': 'wallets',
    'ساعة|ساعات|watch': 'watches',
    'نظارة|نضارة|شمس': 'sunglasses',
    'اكسسوار|مجوهرات|خاتم|سلسلة|حلقة|bracelet': 'accessories',
    'شنطة|شنط|bag|شنط يد': 'bags',
    'أطفال|لعبة|لعب|طفل|دبدوب|دمية': 'kids',
    'هدية|هدايا|مناسبة|مفاجأة': 'gifts',
    'رجالي|راجل|رجال': 'men',
    'حريمي|بنات|نسائي|حريم': 'women'
    }

    
    extracted_interests = []
    for pattern, interest in interests_mapping.items():
        if re.search(pattern, question, re.IGNORECASE):
            extracted_interests.append(interest)
    
    if extracted_interests:
        preferences['interests'] = extracted_interests
    
    # Extract price range
    if re.search(r'رخيص[ةه]?|مش غالي|بسعر معقول|اقتصادي[ةه]?', question, re.IGNORECASE):
        preferences['price_range'] = 'budget'
    elif re.search(r'غالي[ةه]?|فخم[ةه]?|هاي كلاس|راقي[ةه]?', question, re.IGNORECASE):
        preferences['price_range'] = 'premium'
    
    return preferences

def filter_products_by_preferences(products, preferences):
    """
    Filter products by extracted user preferences
    
    Args:
        products: List of product dictionaries
        preferences: Dictionary of user preferences
        
    Returns:
        Filtered list of products
    """
    if not preferences:
        return products
        
    filtered = []
    for prod in products:
        score = 0  # Preference match score
        
        # Match gender
        if 'gender' in preferences:
            target_gender = prod.get('targetGender', '').lower()
            if target_gender == preferences['gender'] or target_gender == 'unisex':
                score += 3
            else:
                # Skip products specifically for the wrong gender
                if target_gender and target_gender != 'unisex':
                    continue
        
        # Match age group
        if 'age_group' in preferences and prod.get('ageGroup'):
            # إذا طلب أطفال، لا تقترح إلا منتجات ageGroup=children/kids
            if preferences['age_group'] == 'children':
                if 'children' in prod.get('ageGroup', '').lower() or 'kids' in prod.get('ageGroup', '').lower():
                    score += 3
                else:
                    continue  # استبعد المنتجات غير المخصصة للأطفال
            elif preferences['age_group'] in prod.get('ageGroup', '').lower():
                score += 2
        
        # Match occasion
        if 'occasion' in preferences:
            product_occasions = []
            if isinstance(prod.get('occasion'), list):
                product_occasions = [o.lower() for o in prod.get('occasion', [])]
            elif prod.get('occasion'):
                product_occasions = [prod.get('occasion', '').lower()]
                
            if preferences['occasion'] in product_occasions:
                score += 4
        
        # Match interests
        if 'interests' in preferences and isinstance(preferences['interests'], list):
            product_tags = []
            if isinstance(prod.get('tags'), list):
                product_tags = [t.lower() for t in prod.get('tags', [])]
            elif prod.get('tags'):
                product_tags = [prod.get('tags', '').lower()]
                
            for interest in preferences['interests']:
                if interest in product_tags:
                    score += 2
                    
        # Match price range
        if 'price_range' in preferences:
            price = float(prod.get('price', 0))
            if preferences['price_range'] == 'budget' and price <= 300:
                score += 2
            elif preferences['price_range'] == 'premium' and price >= 500:
                score += 2
                
        # Only include products with some preference match
        if score > 0:
            # Add preference match score to product data
            prod_copy = prod.copy()
            prod_copy['preference_score'] = score
            filtered.append(prod_copy)
        
    # If we filtered out everything, return original products
    return filtered if filtered else products

# --- Normalization for seasons & occasions ---
SEASON_OCCASION_MAP = {
    # مواسم شائعة وتهجئات متنوعة
    'رمضان': 'ramadan', 'ramadan': 'ramadan', 'رمضان كريم': 'ramadan', 'ramdan': 'ramadan', 'رمضان2025': 'ramadan',
    'عيد الفطر': 'eid-al-fitr', 'عيد الفطر المبارك': 'eid-al-fitr', 'eid_al_fitr': 'eid-al-fitr', 'eid-al-fitr': 'eid-al-fitr', 'eid': 'eid-al-fitr', 'el3id': 'eid-al-fitr', 'العيد الصغير': 'eid-al-fitr', 'العيد': 'eid-al-fitr',
    'عيد الأضحى': 'eid-al-adha', 'عيد الاضحى': 'eid-al-adha', 'eid_al_adha': 'eid-al-adha', 'eid-al-adha': 'eid-al-adha', 'العيد الكبير': 'eid-al-adha', 'el3id elkbeer': 'eid-al-adha',
    'المولد النبوي': 'mawlid', 'mawlid': 'mawlid', 'المولد': 'mawlid', 'elmawlid': 'mawlid',
    'شم النسيم': 'sham-el-nessim', 'sham-el-nessim': 'sham-el-nessim', 'sham el nessim': 'sham-el-nessim', 'sham': 'sham-el-nessim',
    'عيد الحب': 'valentine', 'valentine': 'valentine', 'فالنتين': 'valentine', 'فالنتاين': 'valentine', 'valantine': 'valentine', 'عيد العشاق': 'valentine', 'val': 'valentine',
    'عيد الأم': 'mothers-day', 'عيد الام': 'mothers-day', 'mothers_day': 'mothers-day', 'mothers-day': 'mothers-day', 'عيد الامهات': 'mothers-day', 'عيد الامهات': 'mothers-day', 'عيد الامهات': 'mothers-day', 'عيد الامهات': 'mothers-day', 'عيد الامهات': 'mothers-day', 'عيد الامهات': 'mothers-day',
    'رأس السنة': 'new-year', 'رأس السنه': 'new-year', 'new_year': 'new-year', 'new-year': 'new-year', 'راس السنه': 'new-year', 'راس السنة': 'new-year', 'راس السنه الميلاديه': 'new-year', 'راس السنة الميلادية': 'new-year', 'ny': 'new-year',
    'الكريسماس': 'christmas', 'christmas': 'christmas', 'xmas': 'christmas', 'كريسماس': 'christmas', 'عيد الكريسماس': 'christmas',
    # مناسبات شائعة وتهجئات متنوعة
    'الكل': 'all', 'all': 'all', 'كل المناسبات': 'all', 'اي مناسبة': 'all',
    'عيد الزواج': 'wedding', 'wedding': 'wedding', 'anniversary': 'wedding', 'anniv': 'wedding', 'عيد جواز': 'wedding', 'عيد زواج': 'wedding',
    'عيد ميلاد': 'birthday', 'عيد الميلاد': 'birthday', 'birthday': 'birthday', 'bday': 'birthday', 'عيد ميلادي': 'birthday', 'عيد ميلاد سعيد': 'birthday',
}


def normalize_season_or_occasion(val):
    if not val:
        return ''
    val = str(val).strip().lower().replace('_', '-').replace('–', '-')
    return SEASON_OCCASION_MAP.get(val, val)

def re_rank_products(products, question_embedding, preferences=None):
    """
    Re-rank products using both semantic similarity and preference matching
    
    Args:
        products: List of product dictionaries with scores
        question_embedding: Embedding vector of the user question
        preferences: Optional user preferences dictionary
        
    Returns:
        Re-ranked list of products
    """
    if not products:
        return []
        
    # Weights for different ranking factors
    embedding_weight = 0.7
    preference_weight = 0.3
    
    for prod in products:
        # Start with embedding similarity score
        final_score = prod.get('score', 0) * embedding_weight
        
        # Add preference score if available
        if preferences and 'preference_score' in prod:
            # Normalize preference score (assuming max could be around 10)
            norm_pref_score = min(prod['preference_score'] / 10.0, 1.0)
            final_score += norm_pref_score * preference_weight
            
        # Apply seasonal boost if product matches current season
        current_season = normalize_season_or_occasion(get_current_season())
        product_seasons = []
        if isinstance(prod.get('seasons'), list):
            product_seasons = [normalize_season_or_occasion(s) for s in prod.get('seasons', [])]
        elif prod.get('season'):
            if isinstance(prod.get('season'), list):
                product_seasons = [normalize_season_or_occasion(s) for s in prod.get('season', [])]
            else:
                product_seasons = [normalize_season_or_occasion(prod.get('season', ''))]
        if current_season in product_seasons:
            final_score += 0.1
            
        # Apply occasion boost for upcoming occasions
        upcoming = [normalize_season_or_occasion(o) for o in get_upcoming_occasions()]
        product_occasions = []
        if isinstance(prod.get('occasion'), list):
            product_occasions = [normalize_season_or_occasion(o) for o in prod.get('occasion', [])]
        elif prod.get('occasion'):
            product_occasions = [normalize_season_or_occasion(prod.get('occasion', ''))]
        for occasion in upcoming:
            if occasion in product_occasions:
                final_score += 0.15
                break
        
        # Update score
        prod['final_score'] = final_score
        
    # Sort by final score
    return sorted(products, key=lambda x: x.get('final_score', 0), reverse=True)

def suggest_products_logic(question, top_k=5, session_id=None, detailed_response=True):
    # تأكد أن top_k عدد صحيح
    try:
        if isinstance(top_k, slice):
            logger.error(f"top_k is slice: {top_k}, converting to int 5")
            top_k = 5
        else:
            top_k = int(top_k)
    except Exception as e:
        logger.error(f"Error converting top_k to int: {e}, value={top_k}")
        top_k = 5
    """
    Enhanced product suggestion logic with contextual understanding and personalization
    
    Args:
        question: User question text (in Arabic/Egyptian)
        top_k: Number of products to return
        session_id: Optional session ID for conversation context
        detailed_response: Whether to include detailed explanation in response
        
    Returns:
        Dictionary with message and product recommendations
    """
    try:
        # Begin tracking execution time
        start_time = datetime.now()
        logger.info(f"Processing query: {question[:50]}...")
        
        # Get embedding model
        model = get_embedding_model()
        
        # Handle session context
        session_context = {}
        session_manager = SessionManager()
        if session_id:
            session_context = session_manager.get_session(session_id)
            if session_context is None:
                session_context = {}
            # Update question history
            history = session_context.get('question_history', [])
            history.append(question)
            # Keep only the most recent 5 questions
            history = history[-5:] if len(history) > 5 else history
            session_context['question_history'] = history
            
        # Build enhanced conversation context
        conversation_context = build_conversation_context(question, session_context)
        
        # Extract user preferences
        preferences = extract_user_preferences(question)
        
        # Merge with session preferences if available
        if session_context.get('user_preferences'):
            # For lists, combine
            for key, value in session_context['user_preferences'].items():
                if key not in preferences:
                    preferences[key] = value
                elif isinstance(value, list) and isinstance(preferences.get(key), list):
                    # Combine lists without duplicates
                    preferences[key] = list(set(preferences[key] + value))
        
        # Update session with merged preferences
        if session_id:
            session_context['user_preferences'] = preferences
            session_manager.update_session(session_id, session_context)
        
        # Retrieve and prepare products
        products = list(products_collection.find())
        if not products:
            return {
                "message": "مفيش منتجات متاحة دلوقتي، جرب تسألني بعدين!",
                "products": [],
                "context": preferences
            }
        
        # Generate embeddings for the conversation context
        question_embedding = model.encode([conversation_context])[0]
        
        # Process each product
        results = []
        for prod in products:
            # Join relevant fields with weighting
            full_text = join_fields(prod, CONTENT_FIELDS, FIELD_WEIGHTS).strip()
            
            # Skip products with insufficient information
            if not is_meaningful_content(full_text):
                continue
                
            try:
                # Generate embedding and calculate similarity
                prod_embedding = model.encode([full_text])[0]
                similarity = 1 - cosine(question_embedding, prod_embedding)
                
                # Only include products with reasonable similarity (more tolerant)
                if similarity < 0.15:
                    continue
                    
                # Create product result with necessary details
                results.append({
                    'id': str(prod.get('_id', '')),
                    'name': prod.get('name', ''),
                    'description': prod.get('description', ''),
                    'price': prod.get('price', 0.0),
                    'image': prod.get('image', ''),
                    'score': float(similarity),
                    'tags': prod.get('tags', []),
                    'occasion': prod.get('occasion', []),
                    'season': prod.get('season', []),
                    'seasons': prod.get('seasons', []),
                    'category': prod.get('category', ''),
                    'subCategory': prod.get('subCategory', ''),
                    'brand': prod.get('brand', ''),
                    'targetGender': prod.get('targetGender', ''),
                    'ageGroup': prod.get('ageGroup', ''),
                    'url': prod.get('url', '')
                })
            except Exception as e:
                logger.error(f"Error processing product {prod.get('name')}: {str(e)}")
                continue
        
        # Filter products by preferences
        filtered_results = filter_products_by_preferences(results, preferences)
        
        # Quality check on products - filter out low quality entries
        quality_filtered = []
        for r in filtered_results:
            name = (r.get('name') or '').strip()
            desc = (r.get('description') or '').strip()
            
            if not is_meaningful_content(name) or not is_meaningful_content(desc):
                continue
                
            quality_filtered.append(r)
            
        # Re-rank products considering all factors
        ranked_results = re_rank_products(quality_filtered, question_embedding, preferences)
        
        # Get top-k results
        top_results = ranked_results[:top_k]
        
        # Extract entities and context from the question
        context_data = extract_context(conversation_context)
        
        # Enhance context with our extracted preferences
        context_data.update(preferences)
        
        # Generate personalized response
        msg = friendly_message(context_data, top_results, dialect='egy')
        
        # Log execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Query processed in {execution_time:.2f} seconds, returned {len(top_results)} products")
        
        return {
            "message": msg,
            "products": top_results,
            "context": context_data,
            "execution_time": execution_time
        }
        
    except Exception as e:
        logger.error(f"Error in suggest_products_logic: {str(e)}")
        return {
            "message": "حصل مشكلة في النظام، ممكن تحاول تاني؟",
            "products": [],
            "error": str(e)
        }

# For FastAPI integration
async def suggest_products_api(question: str, top_k: int = 5, session_id: str = None):
    """
    API endpoint wrapper for product suggestions
    
    Args:
        question: User question text
        top_k: Number of products to return
        session_id: Optional session ID
        
    Returns:
        API response with message and products
    """
    return suggest_products_logic(question, top_k, session_id)