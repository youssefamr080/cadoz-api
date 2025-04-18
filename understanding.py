import re
import typing
from typing import Optional, Dict, List, Any, Tuple, Union

# --- Configuration: Keywords & Patterns ---
# It's better to load these from a config file (JSON/YAML) in a real application
# for even easier modification without touching the code.

# Normalize common variations (simple approach)
def _preprocess_text(text: str) -> str:
    """Normalizes text for better matching."""
    text = text.lower()
    # Remove diacritics (optional, might affect meaning sometimes)
    # text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    # Normalize alef variants
    text = re.sub(r'[أإآ]', 'ا', text)
    # Normalize taa marbuta
    text = re.sub(r'ة', 'ه', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# --- Keyword Dictionaries ---

# للمناسبات
OCCASIONS_KEYWORDS: Dict[str, List[str]] = {
    "عيد ميلاد": ["عيد ميلاد", "عيد الميلاد", "ميلاد", "بيرث داي", "بيرثداي", "عيد ميلاده", "عيد ميلادها"],
    "عيد الأم": ["عيد الام", "عيد الأم", "عيد الامهات", "عيد ماما", "يوم الام"],
    "عيد الأب": ["عيد الاب", "عيد الأب", "عيد بابا", "يوم الاب"],
    "عيد الفطر": ["عيد الفطر", "فطر", "العيد الصغير"],
    "عيد الأضحى": ["عيد الاضحى", "عيد الأضحى", "اضحى", "العيد الكبير"],
    "رمضان": ["رمضان", "رمضان كريم"],
    "تخرج": ["تخرج", "تخرجت", "تخرجه", "تخرجها", "حفله تخرج", "حفلة تخرج"],
    "زواج": ["زواج", "عرس", "فرح", "جواز", "زفاف", "كتب كتاب"],
    "خطوبة": ["خطوبة", "خطوبه", "مخطوبه", "مخطوبة", "خطيبها", "خطيبته"],
    "نجاح": ["نجاح", "نجحت", "نجح"],
    "ترقية": ["ترقيه", "ترقية", "اترقيت", "اترقا"],
    "منزل جديد": ["بيت جديد", "منزل جديد", "شقه جديده", "شقة جديدة"],
    "شفاء": ["سلامتك", "شفا", "حمدلله ع السلامه", "الف سلامه"],
    "مولود جديد": ["سبوع", "مولود", "بيبي جديد", "ولاده"],
    "فالنتاين": ["فالنتاين", "فلانتين", "عيد الحب"],
    "بدون مناسبة": ["اي حاجه", "اي شي", "هديه وخلاص", "بدون مناسبه"] # Catch-all for generic requests
}

# لنوع الشخص
RECIPIENT_TYPES_KEYWORDS: Dict[str, List[str]] = {
    "بنت": ["بنت", "فتاه", "انثى", "انسة", "بنوته", "بنوتة", "للبنت", "لبنت", "لبنتي", "لبنتى"],
    "ولد": ["ولد", "شاب", "رجل", "رجالي", "لولد", "لشاب", "لابني", "لابنى"],
    "أم": ["ام", "أم", "والدتي", "ماما", "امي", "ست الحبايب"],
    "أب": ["اب", "أب", "والدي", "بابا", "ابويا", "ابي"],
    "زوجة": ["زوجه", "زوجة", "مراتي", "زوجتي", "المدام", "ام العيال"],
    "زوج": ["زوج", "زوجي", "جوزي", "ابو العيال"],
    "صديقة": ["صديقه", "صديقة", "صاحبه", "صاحبة", "صديقتي", "صاحبتي", "البيست فريند", "بيست فريند (بنت)"],
    "صديق": ["صديق", "صاحبي", "صديقي", "زميلي", "البيست فريند", "بيست فريند (ولد)"],
    "طفل": ["طفل", "طفله", "طفلة", "بيبي", "عيّل", "نونو", "اطفال", "للاطفال"],
    "أخ": ["اخ", "أخ", "اخويا", "اخي"],
    "أخت": ["اخت", "أخت", "اختي"],
    "جد": ["جد", "جدي", "جدو"],
    "جدة": ["جده", "جدة", "جدتي", "تيتا", "نانا"],
    "خطيب": ["خطيب", "خطيبي"],
    "خطيبة": ["خطيبه", "خطيبة", "خطيبتي"],
    "زميل عمل": ["زميل", "زميل عمل", "زميلي في الشغل"],
    "زميلة عمل": ["زميله", "زميلة عمل", "زميلتي في الشغل"],
    "مدير": ["مدير", "مديري", "المدير", "البوص"],
    "مديرة": ["مديره", "مديرتي", "المديره", "البوص"],
    "مدرس/ة": ["مدرس", "مدرسه", "معلم", "معلمه", "استاذ", "استاذه"],
}

# للعلاقة (قد تتداخل مع النوع، لكن نضيفها للوضوح)
RELATIONSHIP_KEYWORDS: Dict[str, List[str]] = {
    "عائلة": ["عائلتي", "حد من العيله", "قريبي", "قريبتي"],
    "زميل": ["زميل", "زميلي", "زميله", "زميلتي", "زمايل"],
    "مدير": ["مدير", "مديري", "مديره", "مديرتي"],
    "خطيب/ة": ["خطيب", "خطيبه", "خطيبتي", "خطيبي"],
    "مقرب": ["حد قريب", "شخص عزيز"],
    "رسمي": ["حد معرفه سطحيه", "شخص رسمي"],
}

# للاهتمامات والهوايات
INTERESTS_KEYWORDS: Dict[str, List[str]] = {
    "رياضة": ["رياضه", "رياضة", "رياضي", "رياضيه", "جيم", "كوره", "كرة قدم", "سباحه", "جري", "تمارين", "فتنس"],
    "موسيقى": ["موسيقى", "مزيكا", "اغاني", "غنا", "بيسمع اغاني", "موسيقي", "موسيقيه"],
    "أفلام/مسلسلات": ["افلام", "مسلسلات", "سينما", "بيتفرج", "نتفلكس", "مشاهده"],
    "قراءة/كتب": ["قرايه", "قراءة", "كتب", "روايات", "بيقرا", "قارئ", "قارئه"],
    "تكنولوجيا/ألعاب": ["تكنولوجيا", "جيمز", "العاب", "بلايستيشن", "كمبيوتر", "تقنيه", "مهتم بالتقنيه", "جيمنج"],
    "طبخ": ["طبخ", "مطبخ", "اكل", "وصفات", "بيطبخ", "بتطبخ"],
    "سفر": ["سفر", "رحلات", "بيسافر", "بتسافر", "ترحال"],
    "تصوير": ["تصوير", "صور", "كاميرا", "بيصور", "مصور", "مصوره"],
    "فنون/رسم": ["فنون", "رسم", "الوان", "بيرسم", "فنان", "فنانه", "اعمال يدويه"],
    "موضة/أزياء": ["موضه", "ازياء", "ملابس", "شيك", "انيقه", "انيق", "ستايل"],
    "عطور": ["عطور", "برفانات", "برفان", "ريحه حلوه", "بيرفيوم"],
    "مكياج/عناية بالبشرة": ["مكياج", "ميكب", "ميك اب", "عنايه بالبشره", "سكين كير", "ماسكات"],
    "نباتات/حدائق": ["زرع", "نباتات", "جنينه", "حديقه", "زراعه", "مهتم بالزرع"],
    "حيوانات أليفة": ["حيوانات اليفه", "قطط", "كلاب", "عنده قطه", "عنده كلب"],
    "سيارات": ["عربيات", "سيارات", "مهتم بالعربيات"],
    "قهوة/شاي": ["قهوه", "شاي", "مشروبات سخنه", "كيف قهوه"],
    "أعمال يدوية": ["اعمال يدويه", "هاند ميد", "كروشيه", "تريكو"],
    "ديكور": ["ديكور", "تزيين البيت", "اثاث"]
}

# للفئة العمرية (بالكلمات)
AGE_GROUP_KEYWORDS: Dict[str, List[str]] = {
    "طفل": ["طفل", "طفله", "بيبي", "نونو", "صغير", "اقل من 10", "تحت 10"],
    "مراهق": ["مراهق", "مراهقه", "تينيجر", "13 سنه", "14 سنه", "15 سنه", "16 سنه", "17 سنه", "18 سنه", "في ثانوي"],
    "شاب/ة": ["شاب", "شابه", "عشرينات", "في الجامعه", "20+", "من 20 ل 30"],
    "متوسط العمر": ["ثلاثينات", "اربعينات", "30+", "40+", "متوسط العمر", "كبير شويه"],
    "كبير السن": ["كبير", "كبيره", "كبير في السن", "عجوز", "خمسينات", "ستينات", "50+", "60+", "فوق الخمسين", "فوق الستين", "متقدم في العمر"]
}

# للميزانية (النوعية)
BUDGET_QUALITATIVE_KEYWORDS: Dict[str, List[str]] = {
    "رخيص": ["رخيص", "رخيصه", "حاجه بسيطه", "مش غاليه", "في المتناول", "اقتصادي"],
    "متوسط": ["متوسط", "متوسطه", "معقول", "لا غالي ولا رخيص", "مش فارق السعر اوي"],
    "غالي": ["غالي", "غاليه", "فخم", "فخمه", "قيمه", "قيمة", "بريستيج"],
    "مفتوح": ["اي سعر", "مش مهم السعر", "ميزانيه مفتوحه"]
}

# للإلحاح
URGENCY_KEYWORDS: Dict[str, List[str]] = {
    "عاجل": ["مستعجل", "ضروري", "بسرعه", "انهارده", "النهارده", "بكره", "في اقرب وقت"],
    "غير عاجل": ["براحتي", "مش مستعجل", "لسه بدري", "كمان اسبوع", "الشهر الجاي"]
}

# للجنس (للتعزيز إذا لم يكن واضحًا من النوع)
GENDER_KEYWORDS: Dict[str, List[str]] = {
    "ذكر": ["ذكر", "راجل", "ولد", "رجل", "رجالي"],
    "أنثى": ["انثى", "بنت", "ست", "حريمي", "نسائي"]
}

# --- Regex Patterns ---
# Improved age regex to capture more context
AGE_REGEX = re.compile(r'(\d{1,3})\s*(سنه|سنة|عام|عمر|عمره|عمرها|سن|سنها|سنه)\b', re.IGNORECASE)
# Budget regex: handles numbers, ranges, and currency symbols/words
BUDGET_REGEX_NUMBER = re.compile(r'(\d+)\s*(جني?ه|ج|ريال|درهم|دينار|دولار|يورو|ل\.? ?م\.?|egp|sar|aed|kwd|usd|eur)?\b', re.IGNORECASE)
BUDGET_REGEX_RANGE = re.compile(r'(?:من|حوالي|في حدود)\s*(\d+)\s*(?:ل|الى|لحد)\s*(\d+)\s*(جني?ه|ج|egp)?\b', re.IGNORECASE)
BUDGET_REGEX_APPROX = re.compile(r'(?:حوالي|تقريبا|في حدود)\s*(\d+)\s*(جني?ه|ج|egp)?\b', re.IGNORECASE)

# --- Helper Functions ---

def _extract_from_keywords(text: str, keywords_dict: Dict[str, List[str]]) -> Optional[str]:
    """Finds the first matching keyword category in the text."""
    for category, keywords in keywords_dict.items():
        for keyword in keywords:
            # Use word boundaries for more precise matching
            if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                return category
    return None

def _extract_entities_from_keywords(text: str, keywords_dict: Dict[str, List[str]]) -> List[str]:
    """Finds all matching keyword categories in the text."""
    found_entities = set()
    for category, keywords in keywords_dict.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                found_entities.add(category)
                # Optional: break if you only want one keyword per category
                # break
    return list(found_entities)

def _extract_age(text: str) -> Dict[str, Optional[Union[str, int]]]:
    """Extracts numerical age and/or age group."""
    age_info: Dict[str, Optional[Union[str, int]]] = {"numerical": None, "group": None}

    # Try numerical first
    match = AGE_REGEX.search(text)
    if match:
        try:
            age_info["numerical"] = int(match.group(1))
        except ValueError:
            pass # Should not happen with \d+ but good practice

    # Try age group keywords
    age_group = _extract_from_keywords(text, AGE_GROUP_KEYWORDS)
    if age_group:
        age_info["group"] = age_group

    # Basic consistency check / refinement
    if age_info["numerical"] is not None and age_info["group"] is None:
        num_age = age_info["numerical"]
        if num_age <= 12: age_info["group"] = "طفل"
        elif 13 <= num_age <= 19: age_info["group"] = "مراهق"
        elif 20 <= num_age <= 29: age_info["group"] = "شاب/ة"
        elif 30 <= num_age <= 49: age_info["group"] = "متوسط العمر"
        elif num_age >= 50: age_info["group"] = "كبير السن"

    return age_info if age_info["numerical"] or age_info["group"] else {} # Return empty dict if nothing found

def _extract_budget(text: str) -> Dict[str, Optional[Any]]:
    """Extracts budget information (numerical, range, qualitative)."""
    budget_info: Dict[str, Optional[Any]] = {"min": None, "max": None, "approx": None, "qualitative": None}

    # 1. Check for ranges first (more specific)
    range_match = BUDGET_REGEX_RANGE.search(text)
    if range_match:
        try:
            budget_info["min"] = int(range_match.group(1))
            budget_info["max"] = int(range_match.group(2))
            # Add currency if found? (group 3) - For now, assume local if unspecified
            return budget_info # Prioritize range
        except ValueError:
            pass

    # 2. Check for approximate values
    approx_match = BUDGET_REGEX_APPROX.search(text)
    if approx_match:
        try:
            budget_info["approx"] = int(approx_match.group(1))
            # Add currency if found? (group 2)
        except ValueError:
            pass

    # 3. Check for single numerical values (if no range or approx was found yet)
    # Find all potential numbers and take the most likely one (e.g., largest?)
    # Simple approach: find first match if approx wasn't set
    if budget_info["approx"] is None:
        number_match = BUDGET_REGEX_NUMBER.search(text)
        if number_match:
             try:
                 # Treat single number as an approximate upper limit or target
                 budget_info["approx"] = int(number_match.group(1))
                 # Add currency if found? (group 2)
             except ValueError:
                 pass

    # 4. Check for qualitative terms
    qualitative = _extract_from_keywords(text, BUDGET_QUALITATIVE_KEYWORDS)
    if qualitative:
        budget_info["qualitative"] = qualitative

    # Return only if some budget info was found
    return budget_info if any(budget_info.values()) else {}


def _infer_gender(recipient_type: Optional[str], relationship: Optional[str]) -> Optional[str]:
    """Infers gender based on recipient type or relationship if not explicit."""
    if recipient_type:
        if recipient_type in ["بنت", "أم", "زوجة", "صديقة", "أخت", "جدة", "خطيبة", "زميلة عمل", "مديرة", "طفله", "مدرسه", "أستاذة", "قارئه", "موسيقيه", "فنانه", "مصوره"]:
            return "أنثى"
        if recipient_type in ["ولد", "أب", "زوج", "صديق", "أخ", "جد", "خطيب", "زميل عمل", "مدير", "طفل", "مدرس", "أستاذ", "قارئ", "موسيقي", "فنان", "مصور"]:
            return "ذكر"
    if relationship:
         if relationship in ["خطيبة"]:
             return "أنثى"
         if relationship in ["خطيب"]:
            return "ذكر"
    return None


# --- Main Extraction Function ---

def extract_context(question: str) -> Dict[str, Any]:
    """
    Analyzes the user's question (in Egyptian Arabic) and extracts various contextual details.

    Args:
        question: The user's input question string.

    Returns:
        A dictionary containing extracted context:
        - occasion (str | None): The event (e.g., "عيد ميلاد").
        - recipient_type (str | None): The type of person receiving the gift (e.g., "أم", "صديق").
        - relationship (str | None): The relationship to the recipient (e.g., "زميل", "مقرب").
        - age (dict | {}): Contains "numerical" (int | None) and "group" (str | None).
        - interests (List[str] | []): List of identified interests/hobbies.
        - budget (dict | {}): Contains "min" (int | None), "max" (int | None),
                               "approx" (int | None), "qualitative" (str | None).
        - urgency (str | None): How urgent the request is (e.g., "عاجل").
        - gender (str | None): Explicitly mentioned or inferred gender ("ذكر", "أنثى").
        - other_details (str): The original preprocessed text for fallback or further analysis.
        # Potential future additions: name, specific items mentioned, sentiment, etc.
    """
    processed_q = _preprocess_text(question)

    context: Dict[str, Any] = {
        "occasion": None,
        "recipient_type": None,
        "relationship": None,
        "age": {},
        "interests": [],
        "budget": {},
        "urgency": None,
        "gender": None,
        "other_details": processed_q # Keep the processed text
    }

    # --- Extraction Steps ---
    context["occasion"] = _extract_from_keywords(processed_q, OCCASIONS_KEYWORDS)
    context["recipient_type"] = _extract_from_keywords(processed_q, RECIPIENT_TYPES_KEYWORDS)
    context["relationship"] = _extract_from_keywords(processed_q, RELATIONSHIP_KEYWORDS)
    context["urgency"] = _extract_from_keywords(processed_q, URGENCY_KEYWORDS)

    # Explicit Gender check
    context["gender"] = _extract_from_keywords(processed_q, GENDER_KEYWORDS)

    context["age"] = _extract_age(processed_q)
    context["budget"] = _extract_budget(processed_q)
    context["interests"] = _extract_entities_from_keywords(processed_q, INTERESTS_KEYWORDS)

    # --- Refinement & Inference ---
    # Infer gender if not explicitly found
    if context["gender"] is None:
        context["gender"] = _infer_gender(context["recipient_type"], context["relationship"])

    # Simple conflict handling example (optional):
    # If type is "أم" but gender is "ذكر", maybe prioritize type? Or flag conflict.
    # Current logic: Explicit gender keyword overrides inference. Inference happens only if gender is None.

    # Handle potential overlap/conflict between type and relationship (e.g., "صديق" vs "زميل")
    # Current logic takes the first match based on keyword dictionary order. More sophisticated
    # logic could analyze proximity or specific phrasing.

    return context

# --- Example Usage ---
if __name__ == "__main__":
    test_questions = [
        "عايز هدية عيد ميلاد لبنت اختي عندها 15 سنة بتحب الميكب والمزيكا",
        "ايه احسن هديه لماما في عيد الام؟ ميزانيه مفتوحه",
        "بفكر اجيب ايه لجوزي في عيد جوازنا الخامس؟ هو بيحب التكنولوجيا والجيمز وميزانيتي حوالي 1000 جنيه",
        "محتاج هديه ضروري بكره لزميلي في الشغل بمناسبه الترقيه بتاعته, حاجه بسيطه في حدود 200 ل 300 ج",
        "اقترح هديه لطفل عمره 5 سنين بيحب العربيات",
        "هديه لصديقتي المقربه بتحب تقرا و تشرب قهوه",
        "عاوز حاجه رجالي شيك لخطيبي بمناسبة الفلانتين سعرها متوسط",
        "ايه هديه مناسبه لست كبيره في السن؟ فوق الستين",
        "اي حاجه تنفع هديه لشاب رياضي؟",
        "هديه لمديري الجديد، حاجه رسميه ومش غاليه اوي", # Test qualitative budget + relationship
        "بفكر في هديه لوالدي بيحب الزرع والقرايه سنه ٦٥ سنه" # Test age + interests + typo
    ]

    for q in test_questions:
        print(f"السؤال: {q}")
        extracted = extract_context(q)
        print(f"السياق المستخرج: {extracted}\n" + "-"*30)

# --- Stubs for logic.py compatibility ---
def extract_entities(text: str):
    """
    Stub for entity extraction. Returns an empty list.
    """
    return []

def analyze_sentiment(text: str):
    """
    Stub for sentiment analysis. Returns None.
    """
    return None