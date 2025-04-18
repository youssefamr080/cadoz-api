import random
from typing import List, Dict, Optional, Union, Tuple

def generate_response(context: Dict, products: List[Dict], dialect: str = 'egy') -> str:
    """
    واجهة موحدة لتوليد رد ودّي مخصص باللهجة المصرية بناءً على السياق والمنتجات المقترحة.
    """
    return friendly_message(context, products, dialect)

def friendly_message(context: Dict, products: List[Dict], dialect: str = 'egy') -> str:
    """
    بتولد رسالة ودية مصرية طبيعية بناءً على السياق والمنتجات المقترحة.
    
    المدخلات:
    - context: قاموس فيه المناسبة، النوع، العمر، الاهتمامات، نطاق السعر...
    - products: قايمة المنتجات المقترحة (ممكن تكون فاضية).
    - dialect: 'egy' (مصري افتراضي) أو 'ar' (فصحى).
    
    المخرجات:
    - رسالة ودية باللهجة المصرية مناسبة للسياق
    """
    # استخراج كل تفاصيل السياق
    occasion = context.get('occasion')
    person_type = context.get('type')
    age_raw = context.get('age')
    interests = context.get('interests', [])
    price_range = context.get('price_range')
    urgency = context.get('urgency')
    relationship = context.get('relationship')
    time_of_day = get_time_of_day()
    user_name = context.get('user_name')
    return_customer = context.get('return_customer', False)
    products_count = len(products)
    previous_purchases = context.get('previous_purchases', [])
    
    # معالجة العمر (تحويلها لفئة عمرية)
    age_category = get_age_category(age_raw)
    
    # اختيار نمط الرد - عشان نضيف تنوع أكتر
    response_style = get_response_style(context)

    # اختيار الرد المناسب حسب وجود منتجات أو لا
    if not products:
        return get_no_results_message(context, response_style)
    
    # بناء الرسالة الأساسية حسب السياق
    message = build_contextual_message(
        occasion=occasion,
        person_type=person_type,
        age_category=age_category,
        interests=interests,
        price_range=price_range,
        urgency=urgency,
        relationship=relationship,
        products_count=products_count,
        response_style=response_style,
        time_of_day=time_of_day,
        return_customer=return_customer,
        user_name=user_name,
        previous_purchases=previous_purchases
    )
    
    # إضافة تعبير أو نصيحة عشوائية للتنويع (بس مش دايمًا)
    if random.random() < 0.8:
        message = add_random_enhancement(message, context, response_style)
    
    # إضافة إيموجي مناسب للسياق (بس مش كتير)
    message = add_contextual_emojis(message, context)
    
    return message


def get_response_style(context: Dict) -> str:
    """
    بتختار نمط/أسلوب الرد بناءً على السياق ونسبة عشوائية
    عشان نضيف تنوع وشخصية للردود
    """
    # أنماط الرد المختلفة
    styles = ['حماسي', 'ودود', 'مرح', 'مساعد', 'عملي']
    
    # لو العميل حالته مستعجلة، نركز على الأنماط العملية والسريعة
    if context.get('urgency') and ('عاجل' in context['urgency'] or 'سريع' in context['urgency']):
        styles = ['عملي', 'مساعد']
    
    # لو المناسبة سعيدة زي عيد ميلاد أو خطوبة، نزود الحماس والمرح
    if context.get('occasion'):
        occasion = context['occasion'].lower()
        if any(item in occasion for item in ['عيد ميلاد', 'خطوبة', 'فرح', 'زواج']):
            styles = ['حماسي', 'مرح', 'ودود']
    
    # لو العميل راجع، نخليه رد أكثر ألفة وود
    if context.get('return_customer'):
        styles = ['ودود', 'مرح']
    
    # اختيار نمط عشوائي من الأنماط المناسبة
    return random.choice(styles)


def get_age_category(age: Optional[Union[int, str]]) -> Optional[str]:
    """بتحول العمر لفئة عمرية أكثر تفصيلًا"""
    if not age:
        return None
        
    # تحويل العمر لرقم لو كان نص
    if isinstance(age, str):
        try:
            age_num = int(age.strip())
        except ValueError:
            return None
    else:
        age_num = age
        
    if age_num <= 2:
        return "رضع"
    elif age_num <= 5:
        return "أطفال صغيرين"
    elif age_num <= 12:
        return "أطفال"
    elif age_num <= 16:
        return "مراهقين صغيرين"
    elif age_num <= 19:
        return "مراهقين"
    elif age_num <= 25:
        return "شباب"
    elif age_num <= 40:
        return "بالغين"
    elif age_num <= 60:
        return "متوسطي العمر"
    elif age_num <= 75:
        return "كبار السن"
    else:
        return "مسنين"


def get_time_of_day() -> str:
    """
    بتحدد وقت اليوم عشان نضبط التحية بشكل أفضل
    """
    import datetime
    hour = datetime.datetime.now().hour
    
    if 5 <= hour < 12:
        return "صباح"
    elif 12 <= hour < 17:
        return "ظهر"
    elif 17 <= hour < 22:
        return "مساء"
    else:
        return "ليل"


def get_no_results_message(context: Dict, response_style: str = 'مساعد') -> str:
    """
    بتجيب رسالة مخصصة في حالة عدم وجود منتجات.
    الردود بتتغير حسب نمط الرد والسياق، وبتقدم اقتراحات مناسبة وذكية.
    """
    # تحضير قاموس يحتوي كل أنماط الرد في حالة عدم وجود نتائج
    no_results_templates = {
        'حماسي': [
            "للأسف مفيش حاجات متوفرة دلوقتي بس متقلقش! 💪 أنا هنا عشان أساعدك نلاقي أحلى هدية!",
            "معندناش اللي انت عايزه بالظبط حاليًا، بس عندي أفكار تانية جامدة جدًا! 🔥",
            "هو صحيح مفيش نتايج للي بتدور عليه، بس متيأسش! فيه بدائل روعة عندنا 😎"
        ],
        'ودود': [
            "آسف يا صديقي، البحث مش لاقي حاجة دلوقتي 🙁 بس تعالى نفكر سوا في حلول تانية..",
            "معلش مفيش عندنا حاجة بالمواصفات دي حاليًا.. بس أكيد هنلاقي حاجة تعجبك برضه 💕",
            "محصلش نصيب في الطلب ده، بس أنا معاك لحد ما نلاقي حاجة تناسبك تمام 💯"
        ],
        'مرح': [
            "يا لهوي! دورت في كل حتة ومش لاقي حاجة بالضبط كده! 😄 بس عندي كام فكرة مجنونة تانية!",
            "أصل الحاجات دي الناس بتخطفها على طول! 😜 طب ما تجرب حاجة تانية أحلى؟",
            "دورت معاك لحد ما دوخت خالص 🤪 بس بردو مفيش! تعالى نجرب حاجة مختلفة..."
        ],
        'مساعد': [
            "للأسف مش لاقي حاجة مطابقة لطلبك حاليًا 🔍 ممكن تديني معلومات أكتر أو نغير شوية في المواصفات؟",
            "البحث مجبش نتايج مناسبة! 🤔 ممكن نغير السعر أو الفئة عشان نلاقي هدايا أحسن؟",
            "مفيش حاجة بالظبط كده حاليًا. ممكن أقترح عليك بعض البدائل لو تحب؟ 🙂"
        ],
        'عملي': [
            "مفيش نتايج متطابقة. خلينا نضبط البحث: ممكن نغير نطاق السعر أو نشوف فئات تانية؟",
            "البحث مطلعش نتايج. عايز تحدد فئات أو اهتمامات مختلفة؟",
            "مش متوفر طلبك حاليًا. تعالى نعدل المعايير: نوع المنتج أو السعر أو المناسبة؟"
        ]
    }
    
    # التقاط المعلومات الأساسية للسياق
    occasion = context.get('occasion')
    person_type = context.get('type')
    price_range = context.get('price_range')
    interests = context.get('interests', [])
    user_name = context.get('user_name')
    
    # اختيار رسالة أساسية حسب نمط الرد
    base_msg = random.choice(no_results_templates.get(response_style, no_results_templates['مساعد']))
    
    # بناء قائمة اقتراحات بديلة ذكية حسب السياق
    suggestions = []
    
    # اقتراحات بديلة حسب المناسبة
    if occasion:
        occasion_suggestions = {
            'عيد ميلاد': ["شفت الشنط الجلد الجديدة عندنا؟", "التجربة الحياتية أحلى من الهدايا - مثلاً تذاكر سينما أو مغامرة؟"],
            'زواج': ["أطقم المطبخ الشيك حاليًا عليها عروض", "أجهزة كهربائية عملية ممكن تبقى أحسن من الديكور!"],
            'تخرج': ["كوتش جديد أو ساعة حلوة أحسن من الهدايا التقليدية", "جهاز لاب توب أو تابلت؟"],
            'مولود جديد': ["عندنا ملابس أطفال قطن طبيعي 100%", "ألعاب تعليمية أحسن من الهدايا التقليدية"],
            'خطوبة': ["تذاكر سفر ليوم واحد؟", "سلسلة فضة أو ساعة مميزة؟"]
        }
        
        for key in occasion_suggestions:
            if key in occasion.lower():
                suggestions.append(random.choice(occasion_suggestions[key]))
                break
        else:
            suggestions.append(f"فيه هدايا تانية كتير ممكن تناسب {occasion}")
    
    # اقتراحات حسب النوع أو الجنس
    if person_type:
        if any(word in person_type.lower() for word in ['بنت', 'أنثى', 'ست', 'مدام', 'زوجة', 'خطيبة']):
            female_suggestions = [
                "شنطة ماركة من الكوليكشن الجديد",
                "سكارف حرير أنيق وعملي",
                "طقم إكسسوارات متكامل",
                "عطر فرنساوي من أحدث التشكيلات",
                "كريمات أو مكياج من براندات فاخرة"
            ]
            suggestions.append(random.choice(female_suggestions))
        elif any(word in person_type.lower() for word in ['ولد', 'ذكر', 'راجل', 'زوج', 'خطيب']):
            male_suggestions = [
                "محفظة جلد ماركة أصلية",
                "ساعة يد كلاسيك أو رياضية",
                "بيرفيوم رجالي فاخر",
                "قميص كاجوال أو كلاسيك شيك",
                "جادجت تكنولوجي عملي"
            ]
            suggestions.append(random.choice(male_suggestions))
    
    # اقتراحات حسب الاهتمامات
    if interests:
        interest_suggestions = {
            'رياضة': ['ممكن تشوف ملابس رياضية ماركة؟', 'سماعات بلوتوث مخصصة للرياضة؟'],
            'موسيقى': ['سماعات عالية الجودة بتفرق كتير', 'جيفت كارد لشراء ميوزك أونلاين؟'],
            'قراءة': ['كتب محدودة الطبعات عندنا', 'قارئ كتب إلكتروني'],
            'تكنولوجيا': ['اكسسوارات موبايل ذكية', 'سماعات ذكية أو ساعة سمارت'],
            'سفر': ['شنطة سفر عملية', 'إكسسوارات سفر مريحة']
        }
        
        for interest in interests:
            for key in interest_suggestions:
                if key in interest.lower():
                    suggestions.append(random.choice(interest_suggestions[key]))
                    break
    
    # اقتراحات حسب السعر
    if price_range:
        if any(word in price_range.lower() for word in ['رخيص', 'بسيط', 'توفير', 'قليل']):
            suggestions.append("ممكن نشوف هدايا أكتر في نطاق سعر أعلى شوية؟")
        elif any(word in price_range.lower() for word in ['غالي', 'فاخر', 'عالي']):
            suggestions.append("عندنا منتجات مميزة في فئة أسعار أقل بجودة عالية برضه")
        else:
            suggestions.append("عندنا منتجات في كل الفئات السعرية")
    
    # دمج الرسالة مع الاقتراحات بطريقة طبيعية
    if suggestions:
        # اختيار من 1-2 اقتراح فقط عشان منطولش
        selected_suggestions = random.sample(suggestions, min(2, len(suggestions)))
        
        # إضافة ترويسة للاقتراحات
        suggestion_intros = [
            "طب ما تفكر في: ",
            "أقترح عليك: ",
            "أنا شايف إن ده ممكن يعجبك: ",
            "ممكن تشوف: ",
            "فكرة كويسة: "
        ]
        
        suggestion_text = f"{random.choice(suggestion_intros)}{' وكمان '.join(selected_suggestions)}"
        
        # إضافة تشجيع في النهاية
        encouragements = [
            " إيه رأيك؟",
            " تحب أقترح حاجات تانية؟",
            " يا ترى دول مناسبين؟",
            " أعتقد دي هتعجبك.",
            " متتردش، Cadoz دايمًا معاك!"
        ]
        
        # أضف اسم المستخدم لو موجود (للمسة شخصية)
        if user_name:
            greeting = f" يا {user_name}"
        else:
            greeting = ""
            
        full_message = f"{base_msg} {suggestion_text}{random.choice(encouragements)}{greeting}"
    else:
        full_message = f"{base_msg} قولي بس انت عايز إيه بالظبط وأنا هظبطك على الآخر!"
    
    return full_message


# --- ترجمة الأقسام للعربي ---
CATEGORY_TRANSLATIONS = {
    'watches': 'ساعات',
    'wallets': 'محافظ',
    'sunglasses': 'نظارات شمس',
    'perfumes': 'عطور',
    'spray': 'سبراي',
    'accessories': 'إكسسوارات',
    'kids_toys': 'ألعاب أطفال',
    'teddy_bears': 'دباديب',
    'handbags': 'شنط',
    'men': 'رجالي',
    'women': 'حريمي',
    'kids': 'أطفال',
    'unisex': 'للجميع',
    'all': 'الكل',
}

def translate_category(cat):
    if not cat:
        return ''
    cat = str(cat).strip().lower()
    return CATEGORY_TRANSLATIONS.get(cat, cat)

def build_contextual_message(
    occasion: Optional[str], 
    person_type: Optional[str], 
    age_category: Optional[str], 
    interests: List[str], 
    price_range: Optional[str],
    urgency: Optional[str],
    relationship: Optional[str],
    products_count: int,
    response_style: str,
    time_of_day: str,
    return_customer: bool,
    user_name: Optional[str] = None,
    previous_purchases: Optional[List] = None
) -> str:
    message_parts = []  # إصلاح: يجب تعريفها هنا

    # بناء الرسالة حسب عدد المنتجات
    if products_count == 0:
        message_parts.append("مفيش منتجات مناسبة دلوقتي.")
    elif products_count == 1:
        message_parts.append("لقيتلك اختيار واحد ممتاز!")
    elif products_count <= 3:
        message_parts.append(f"دول أجمد {products_count} اختيارات ممكن تعجبك!")
    else:
        message_parts.append(f"دول {products_count} هدايا متنوعة تقدر تختار منهم!")

    # استخراج الفئات الرئيسية من المنتجات (category/subCategory)
    categories_set = set()
    subcategories_set = set()
    if 'products' in locals() and products_count > 0:
        for prod in locals()['products']:
            cat = prod.get('category', '')
            subcat = prod.get('subCategory', '')
            if cat:
                categories_set.add(translate_category(cat))
            if subcat:
                subcategories_set.add(translate_category(subcat))
    # لو فيه أكثر من فئة، اذكرهم بالعربي
    all_types = list(categories_set | subcategories_set)
    if all_types:
        if len(all_types) == 1:
            message_parts.append(f"( {all_types[0]} )")
        else:
            message_parts.append(f"({ ' و '.join(all_types) })")

    # تخصيص الرسالة حسب الاهتمامات أو القسم
    if interests:
        interests_ar = [translate_category(i) for i in interests]
        message_parts.append(f"مناسبة للي بيحب {', '.join(interests_ar)}.")
    elif person_type:
        message_parts.append(f"مناسبة لـ {person_type}.")
    elif occasion:
        message_parts.append(f"مناسبة لـ {occasion}.")

    return " ".join(message_parts)

    """
    بتبني رسالة متكاملة حسب السياق وعناصره المختلفة
    الرسالة بتضم جزء تحية، جزء مقدمة، وجزء تفاصيل حسب السياق
    """
    message_parts = []
    
    # ------------------ إضافة تحية حسب وقت اليوم والمستخدم ------------------
    greeting = build_greeting(time_of_day, user_name, return_customer, response_style)
    if greeting:
        message_parts.append(greeting)
    
    # ------------------ اختيار مقدمة الرسالة حسب عدد المنتجات وأسلوب الرد ------------------
    intro = get_products_intro(products_count, response_style)
    message_parts.append(intro)
    
    # ------------------ تخصيص الرسالة حسب المناسبة ------------------
    if occasion:
        occasion_phrase = get_occasion_phrase(occasion, response_style)
        if occasion_phrase:
            message_parts.append(occasion_phrase)
    
    # ------------------ إضافة نوع الشخص وفئة العمر ------------------
    if person_type or age_category:
        recipient_phrase = get_recipient_phrase(person_type, age_category)
        if recipient_phrase:
            message_parts.append(recipient_phrase)
    
    # ------------------ إضافة الاهتمامات ------------------
    if interests:
        interests_phrase = get_interests_phrase(interests)
        if interests_phrase:
            message_parts.append(interests_phrase)
    
    # ------------------ إضافة نطاق السعر ------------------
    if price_range:
        price_phrase = get_price_phrase(price_range, response_style)
        if price_phrase:
            message_parts.append(price_phrase)
    
    # ------------------ إضافة العلاقة مع المستلم ------------------
    if relationship:
        relationship_phrase = get_relationship_phrase(relationship)
        if relationship_phrase:
            message_parts.append(relationship_phrase)
    
    # ------------------ إضافة الإلحاح أو الضرورة ------------------
    if urgency:
        urgency_phrase = get_urgency_phrase(urgency)
        if urgency_phrase:
            message_parts.append(urgency_phrase)
    
    # ------------------ إضافة التخصيص بناءً على المشتريات السابقة ------------------
    if return_customer and previous_purchases:
        history_phrase = get_purchase_history_phrase(previous_purchases)
        if history_phrase:
            message_parts.append(history_phrase)
    
    # دمج كل أجزاء الرسالة
    return " ".join(message_parts)


def build_greeting(time_of_day: str, user_name: Optional[str], return_customer: bool, response_style: str) -> Optional[str]:
    """بتبني تحية مناسبة حسب وقت اليوم والمستخدم"""
    # احتمال إضافة تحية (مش كل مرة)
    if random.random() < 0.7:
        # تحيات حسب وقت اليوم
        time_greetings = {
            'صباح': ['صباح الخير', 'صباح الفل', 'صباحو', 'صباح النور'],
            'ظهر': ['ظهر الخير', 'يسعد أوقاتك', 'هاي', 'أهلاً بيك'],
            'مساء': ['مساء الخير', 'مساء الفل', 'مساء النور', 'مساء السعادة'],
            'ليل': ['مساء الخير', 'ليلة سعيدة', 'أهلاً بيك', 'هاي']
        }
        
        # اختيار تحية مناسبة
        greeting = random.choice(time_greetings.get(time_of_day, ['أهلاً بيك']))
        
        # إضافة اسم المستخدم لو موجود
        if user_name:
            # تنويع طريقة التحية بالاسم
            name_variations = [
                f" يا {user_name}",
                f" {user_name}",
                f" يا باشا {user_name}",
                f" يا حبيب قلبي {user_name}" if response_style in ['حماسي', 'ودود'] else f" {user_name}"
            ]
            greeting += random.choice(name_variations)
        elif return_customer:
            greeting += " يا باشا"
        
        # إضافة علامة تعجب أو لا حسب النمط
        if response_style in ['حماسي', 'مرح']:
            greeting += "! "
        else:
            greeting += ". "
            
        return greeting
    return None


def get_products_intro(products_count: int, response_style: str) -> str:
    """
    اختيار مقدمة مناسبة حسب عدد المنتجات وأسلوب الرد
    """
    # تعبيرات البداية حسب عدد المنتجات ونمط الرد
    intros_by_style = {
        'حماسي': {
            'قليل': [
                "جبتلك أحلى كام حاجة",
                "شوف أروع اختيارات",
                "عندنا تحف هتعجبك أوي",
                "دول اجمد كام اختيار هيخلوك مبسوط"
            ],
            'كثير': [
                "جبتلك كنز من الاختيارات الجامدة",
                "شوف الروعة دي كلها",
                "عندنا مجموعة نار هتعجبك جدًا",
                "دي تشكيلة تجنن بجد!"
            ]
        },
        'ودود': {
            'قليل': [
                "جمعتلك كام حاجة حلوة",
                "شوف دول كده",
                "عندي كام اقتراح هيعجبوك",
                "في كام حاجة لطيفة كده"
            ],
            'كثير': [
                "جبتلك مجموعة جميلة وشيك",
                "شوف الجمال ده كله",
                "عندنا اختيارات كتير هتفرحك",
                "دي تشكيلة كلها ذوق وأناقة"
            ]
        },
        'مرح': {
            'قليل': [
                "بص بص دول عسل أوي!",
                "شوف شوف الحاجات الحلوة دي",
                "يا واد شوف التحف دي",
                "دي أحلى من عينيك طبعاً 😜"
            ],
            'كثير': [
                "أوبااا! شوف الخير الكتير ده!",
                "ياااه! كل ده عشانك يا باشا!",
                "كتر خيرنا صح؟ بص كل دول!",
                "مقدرتش أقاوم، جبتلك كل ده!"
            ]
        },
        'مساعد': {
            'قليل': [
                "اخترتلك بعناية كام اقتراح",
                "شوف الحاجات دي ممكن تناسبك",
                "بناءً على طلبك، دول أفضل اختيارات",
                "دي كام حاجة بتناسب اللي بتدور عليه"
            ],
            'كثير': [
                "هتلاقي ضمن المجموعة دي كل اللي محتاجه",
                "دي أفضل منتجات تناسب طلبك",
                "جمعتلك اختيارات متنوعة بتناسب احتياجاتك",
                "دي قايمة شاملة من المنتجات اللي شبه اللي طلبته"
            ]
        },
        'عملي': {
            'قليل': [
                "إليك هذه الاختيارات",
                "وجدت هذه المنتجات لك",
                "هذه بعض الاقتراحات المناسبة",
                "فيما يلي أفضل المنتجات المتوفرة"
            ],
            'كثير': [
                "إليك مجموعة متكاملة من المنتجات",
                "هذه قائمة شاملة بالاختيارات المتاحة",
                "الاختيارات التالية تلبي متطلباتك",
                "وجدت لك هذه المجموعة المتنوعة"
            ]
        }
    }
    
    # اختيار التحية حسب عدد المنتجات (قليل أو كثير)
    if products_count <= 3:
        category = 'قليل'
    else:
        category = 'كثير'
    
    # في حالة عدم وجود النمط المحدد، نستخدم النمط 'مساعد' افتراضيًا
    style = response_style if response_style in intros_by_style else 'مساعد'
    
    return random.choice(intros_by_style[style][category])


def get_occasion_phrase(occasion: str, response_style: str) -> Optional[str]:
    """بتجيب عبارة مناسبة للمناسبة مع مراعاة أسلوب الرد"""
    # عبارات المناسبات حسب أسلوب الرد
    occasion_phrases_by_style = {
        'حماسي': {
            'عيد ميلاد': [
                "هتخلي عيد الميلاد مش هيتنسى أبدًا",
                "هيخلو اليوم الكبير ده إكسترا سبيشيال",
                "هتبهر بيهم صاحب عيد الميلاد بجد",
                "يستاهلوا أجمد احتفال بعيد الميلاد"
            ],
            'زواج': [
                "للفرحة الكبيرة دي هيبقوا تحفة",
                "هيضيفوا لمسة مبهرة للعرسان",
                "مستوى الفرحة ده يستاهل هدايا خيالية",
                "محدش هينسى الهدية دي أبدًا"
            ],
            'تخرج': [
                "تليق بالإنجاز الكبير ده",
                "عشان تكمل فرحة التخرج بشكل مثالي",
                "هيحتفلوا بنجاحه الباهر",
                "عشان يفتكر اليوم ده طول العمر"
            ],
            'مولود جديد': [
                "للبيبي الجميل هتبقى روعة",
                "هيفرحوا الأهل والمولود الجديد",
                "هيبقوا أحلى بداية للبيبي",
                "هياخدوا بالهم من الزغنطط الجديد"
            ],
            'خطوبة': [
                "هيبهروا المخطوبين بجد",
                "هيعملوا مفاجأة مش هتتنسى",
                "هيبقوا أجمل هدية فالخطوبة دي",
                "عشان يفرحوا بيها ويفتكروها دايمًا"
            ]
        },
        'ودود': {
            'عيد ميلاد': [
                "تسعد صاحب عيد الميلاد",
                "تحلي بيها الاحتفال الجميل ده",
                "تضيف بهجة للمناسبة الحلوة دي",
                "تخليها ذكرى حلوة"
            ],
            'زواج': [
                "تناسب الفرحة الكبيرة دي",
                "تسعد قلب العروسين",
                "تعبر عن مشاعرك الجميلة ليهم",
                "تكون بداية حلوة لحياتهم"
            ],
            'تخرج': [
                "تكافئ التعب والمجهود",
                "تكمل فرحة التخرج",
                "تناسب النجاح الكبير ده",
                "تكون هدية عملية للمستقبل"
            ],
            'مولود جديد': [
                "للبيبي اللطيف والأهل",
                "تفرح قلب الأسرة الجديدة",
                "تناسب المولود الصغير",
                "تكون مفيدة وجميلة للبيبي"
            ],
            'خطوبة': [
                "تسعد المخطوبين",
                "تكون بداية حلوة لحياتهم",
                "تناسب فرحة الخطوبة",
                "تعبر عن تمنياتك الطيبة ليهم"
            ]
        },
        'مرح': {
            'عيد ميلاد': [
                "تخليه يطير من الفرحة 🎈",
                "تفرتك عيد الميلاد فرتكة",
                "تخليه عيد ميلاد برعبيكو بجد",
                "يغمض عينيه ويطفي الشموع ويتفاجئ 😁"
            ],
            'زواج': [
                "تخلي العروسين يتنططوا من الفرحة",
                "بص هيطلعلهم قرون من كتر ما هيفرحوا 😄",
                "هيفضلوا يباركوا فيك طول العمر",
                "عندك فرصة تكسب دعوات العرايس 🤭"
            ],
            'تخرج': [
                "تخليه يرقص على السلم من الفرحة",
                "أخيرًا خلص دراسة وهياخد هدية كمان!",
                "تحلي الكابة بعد سنين المذاكرة المرعبة",
                "البس طرحة التخرج وافرح بالهدية 🎓"
            ],
            'مولود جديد': [
                "البيبي لسه مش فاهم حاجة بس الأهل هيفرحوا 👶",
                "تخلي البيبي يضحك (مع إنه اصلاً مش عارف هو فين)",
                "البيبي: أنا إيه اللي جابني هنا؟ الهدية: أنا!",
                "تناسب الزنقة الجديدة اللي هما فيها دلوقتي 🤪"
            ],
            'خطوبة': [
                "تخليهم يبصوا لبعض ويقولوا: اتجوزنا صح!",
                "يطلعوا الدبل ويلبسوا الهدايا 💍",
                "تضمن إنهم مش هيفسخوا الخطوبة بعد ما يشوفوها",
                "تخلي كل الناس تغير من المخطوبين 😎"
            ]
        },
        'مساعد': {
            'عيد ميلاد': [
                "مناسبة تمامًا للاحتفال بعيد الميلاد",
                "تم اختيارها خصيصًا لمناسبة عيد الميلاد",
                "تناسب متطلبات هدية عيد الميلاد",
                "تجمع بين الجمال والفائدة لصاحب عيد الميلاد"
            ],
            'زواج': [
                "تناسب احتياجات الزوجين الجدد",
                "عملية ومفيدة للحياة الزوجية الجديدة",
                "تم اختيارها بعناية لمناسبة الزفاف",
                "تساعد في بدء حياة زوجية سعيدة"
            ],
            'تخرج': [
                "تناسب الخريج الجديد وطموحاته",
                "تساعده في بداية حياته العملية",
                "مناسبة للمرحلة الجديدة بعد التخرج",
                "تمثل استثمارًا جيدًا لمستقبله"
            ],
            'مولود جديد': [
                "مصممة لراحة ورعاية المولود الجديد",
                "تساعد الأهل في العناية بالطفل",
                "آمنة ومناسبة للأطفال الرضع",
                "تجمع بين الجمال والفائدة للأسرة الجديدة"
            ],
            'خطوبة': [
                "تناسب مرحلة الخطوبة والتجهيز للزواج",
                "تعبر عن تهانيك للمخطوبين بشكل عملي",
                "تساعدهم في التخطيط لمستقبلهم",
                "تبقى ذكرى جميلة لمناسبة الخطوبة"
            ]
        },
        'عملي': {
            'عيد ميلاد': [
                "مناسبة لعمر وذوق صاحب عيد الميلاد",
                "تجمع بين القيمة العملية والعاطفية",
                "تدوم طويلاً كذكرى للمناسبة",
                "توفر قيمة جيدة مقابل السعر"
            ],
            'زواج': [
                "مفيدة للمنزل الجديد",
                "تناسب البداية الجديدة للزوجين",
                "توفر احتياجات أساسية للحياة الزوجية",
                "استثمار جيد للمستقبل المشترك"
            ],
            'تخرج': [
                "مفيدة للحياة العملية القادمة",
                "تناسب المرحلة المهنية الجديدة",
                "تساعد في تحقيق النجاح المهني",
                "تمثل بداية جيدة للمسار المهني"
            ],
            'مولود جديد': [
                "تلبي احتياجات الطفل الجديد",
                "تساعد في رعاية المولود بشكل عملي",
                "صممت خصيصًا للأطفال الرضع",
                "تدوم لفترة طويلة مع نمو الطفل"
            ],
            'خطوبة': [
                "تساعد في التجهيز للحياة المشتركة",
                "توفر قيمة مناسبة كهدية خطوبة",
                "عملية ومفيدة للزوجين المستقبليين",
                "تناسب متطلبات مرحلة الخطوبة"
            ]
        }
    }
    
    # البحث عن المناسبة والعبارة المناسبة
    for key in occasion_phrases_by_style.get(response_style, occasion_phrases_by_style['مساعد']):
        if key in occasion.lower():
            return random.choice(occasion_phrases_by_style.get(response_style, occasion_phrases_by_style['مساعد'])[key])
    
    # لو مفيش مناسبة محددة في القاموس
    return f"مناسبة لـ{occasion}"


def get_recipient_phrase(person_type: Optional[str], age_category: Optional[str]) -> Optional[str]:
    """بتجيب عبارة مناسبة لنوع الشخص وفئته العمرية"""
    if person_type and age_category:
        # تنويع العبارات حسب النوع والعمر معًا
        combined_phrases = [
            f"مناسبة لـ{person_type} من {age_category}",
            f"خصيصًا لـ{person_type} في سن الـ{age_category}",
            f"مثالية لـ{person_type} ضمن فئة {age_category}",
            f"تناسب {person_type} اللي في مرحلة {age_category}"
        ]
        return random.choice(combined_phrases)
    elif person_type:
        # عبارات مخصصة حسب النوع فقط
        type_phrases = {
            'بنت': ["للبنات بس", "تناسب البنوتات", "حصريًا للبنات الشيك"],
            'ولد': ["للأولاد الكول", "خصيصًا للشباب", "تناسب الرجالة بس"],
            'ست': ["للستات الذوق", "تناسب المدامات", "للسيدات الأنيقات"],
            'راجل': ["للرجالة بس", "تناسب الرجالة الجدعان", "هدايا رجالي خالص"],
            'زوجة': ["لمراتك الغالية", "تسعد الزوجة", "تناسب الست الكبيرة"],
            'زوج': ["لجوزك الغالي", "تسعد الزوج", "تناسب الراجل بتاعك"]
        }
        
        # البحث عن كلمات مفتاحية في النوع
        for key in type_phrases:
            if key in person_type.lower():
                return random.choice(type_phrases[key])
        
        # لو مفيش نوع محدد في القاموس
        return f"مناسبة لـ{person_type}"
        
    elif age_category:
        # عبارات مخصصة حسب العمر فقط
        age_phrases = {
            'رضع': ["للبيبيهات الصغيرة", "مناسبة للمواليد الجدد", "تناسب الرضع"],
            'أطفال صغيرين': ["للأطفال الصغيرين", "مناسبة للأطفال تحت 5 سنين", "للزغاليل الحلوين"],
            'أطفال': ["مناسبة للأطفال", "الأطفال هيحبوها أوي", "هتفرح قلب أي طفل"],
            'مراهقين': ["للمراهقين العصريين", "الشباب الصغير هيعشقها", "تناسب المراهقين"],
            'شباب': ["للشباب العصري", "تناسب الشباب النشيط", "عصرية ومناسبة للشباب"],
            'بالغين': ["تناسب البالغين", "للناس الناضجة", "مثالية للكبار"],
            'متوسطي العمر': ["مناسبة لمتوسطي العمر", "تناسب الناس في أحسن سن", "للناس اللي عدت الشباب شوية"],
            'كبار السن': ["مناسبة لكبار السن", "سهلة الاستخدام للكبار", "تراعي احتياجات كبار السن"],
            'مسنين': ["مصممة بعناية للمسنين", "مريحة وعملية للمسنين", "تراعي خصوصية المسنين"]
        }
        
        # البحث عن العمر المناسب
        for key in age_phrases:
            if key == age_category:
                return random.choice(age_phrases[key])
        
        # لو مفيش عمر محدد في القاموس
        return f"مناسبة لفئة الـ{age_category}"
    
    return None


def get_interests_phrase(interests: List[str]) -> Optional[str]:
    """بتجيب عبارة مناسبة للاهتمامات"""
    if not interests:
        return None
        
    # بناء الرسالة حسب عدد المنتجات
    if products_count == 0:
        message_parts.append("مفيش منتجات مناسبة دلوقتي.")
    elif products_count == 1:
        message_parts.append("لقيتلك اختيار واحد ممتاز!")
    elif products_count <= 3:
        message_parts.append(f"دول أجمد {products_count} اختيارات ممكن تعجبك!")
    else:
        message_parts.append(f"دول {products_count} هدايا متنوعة تقدر تختار منهم!")

    # تخصيص الرسالة حسب الاهتمامات أو القسم
    if interests:
        interests_ar = [translate_category(i) for i in interests]
        message_parts.append(f"مناسبة للي بيحب {', '.join(interests_ar)}.")
    elif person_type:
        message_parts.append(f"مناسبة لـ {person_type}.")
    elif occasion:
        message_parts.append(f"مناسبة لـ {occasion}.")

    # لو فيه أقسام أو subCategory في المنتجات، أضفها بالعربي فقط
    # مثال: لو المنتج الأساسي من فئة "watches"، اذكر "ساعات" فقط
    # (تحسين إضافي: لو فيه أكثر من قسم في النتائج، اذكرهم بالعربي)
    # هذا الجزء اختياري ويمكن توسيعه حسب الحاجة
    if categories:
        categories_ar = [translate_category(c) for c in categories]
        message_parts.append(f"مناسبة لـ {', '.join(categories_ar)}.")
def get_price_phrase(price_range: str, response_style: str) -> str:
    """بتجيب عبارة مناسبة لنطاق السعر مع مراعاة أسلوب الرد"""
    # عبارات السعر حسب أسلوب الرد
    price_phrases_by_style = {
        'حماسي': [
            f"وكل ده في حدود {price_range} بس!",
            f"بسعر مناسب جدًا {price_range}",
            f"وبقيمة مالية عادلة جدًا ({price_range})",
            f"بأحلى سعر ({price_range}) عشان نفرحك"
        ],
        'ودود': [
            f"بسعر مناسب ({price_range})",
            f"على قد ميزانيتك ({price_range})",
            f"وفي حدود {price_range} زي ما طلبت",
            f"بتكلفة معقولة ({price_range})"
        ],
        'مرح': [
            f"وبكام قرش بس! ({price_range}) يعني هتفرح من غير ما تفلس 😁",
            f"في نطاق {price_range} - يعني مش هتبيع الليلة عشانها",
            f"بس هي فعلاً تستاهل الـ{price_range} دي وزيادة كمان",
            f"وسعرها {price_range} يعني مش هتضرب في الحساب 😉"
        ],
        'مساعد': [
            f"ضمن نطاق السعر المطلوب ({price_range})",
            f"بما يناسب ميزانيتك المحددة ({price_range})",
            f"تقع في الفئة السعرية {price_range}",
            f"تلبي متطلبات الميزانية ({price_range})"
        ],
        'عملي': [
            f"متوفرة بسعر {price_range}",
            f"تقدم قيمة جيدة مقابل {price_range}",
            f"تلبي متطلبات السعر {price_range}",
            f"في حدود الميزانية المحددة {price_range}"
        ]
    }
    
    # اختيار عبارة مناسبة حسب النمط
    style = response_style if response_style in price_phrases_by_style else 'مساعد'
    return random.choice(price_phrases_by_style[style])


def get_relationship_phrase(relationship: str) -> Optional[str]:
    """بتجيب عبارة مناسبة للعلاقة مع المستلم"""
    relationship_phrases = {
        'صديق': ["لصاحبك المقرب", "لأعز صديق", "للباشا صاحبك", "للصديق العزيز"],
        'صديقة': ["لصحبتك المقربة", "للصاحبة العزيزة", "لأعز صاحبة", "لأقرب صديقة عندك"],
        'زوج': ["لجوزك الغالي", "لشريك حياتك", "لنص التفاحة", "للراجل بتاعك"],
        'زوجة': ["لمراتك الحبيبة", "لشريكة حياتك", "لنص التفاحة", "للست الكبيرة"],
        'أب': ["لأبوك العزيز", "للوالد الكبير", "للباشا الكبير", "لأغلى أب"],
        'أم': ["لأمك الغالية", "للوالدة الحبيبة", "للست الوالدة", "لأغلى أم"],
        'ابن': ["لابنك الغالي", "لفلذة كبدك", "للابن العزيز", "لنور عينك"],
        'بنت': ["لبنتك الغالية", "للبنوتة بتاعتك", "لحتة من قلبك", "لنور عينك"],
        'أخ': ["لأخوك العزيز", "للأخ الكبير", "للأخ الصغير", "لأقرب الناس ليك"],
        'أخت': ["لأختك العزيزة", "للأخت الكبيرة", "للأخت الصغيرة", "لأقرب الناس ليك"]
    }
    
    # البحث عن العلاقة المناسبة
    for key in relationship_phrases:
        if key in relationship.lower():
            return random.choice(relationship_phrases[key])
    
    # لو مفيش علاقة محددة في القاموس
    return f"لـ{relationship} بتاعك"


def get_urgency_phrase(urgency: str) -> Optional[str]:
    """بتجيب عبارة مناسبة للإلحاح أو الضرورة"""
    if not urgency:
        return None
        
    if any(word in urgency.lower() for word in ['عاجل', 'سريع', 'بكرة', 'النهاردة', 'اليوم']):
        urgent_phrases = [
            "وكمان عندنا توصيل سريع يوصلك على طول",
            "وهنظبطك في توصيل خلال 24 ساعة",
            "ومتقلقش من وقت التوصيل، هيوصل في وقته",
            "وطبعًا في خدمة توصيل سريعة للطلبات العاجلة دي",
            "وعندنا خدمة توصيل سريعة جدًا للي زيك مستعجل",
            "ودي كلها متوفرة حاليًا وممكن توصلك بسرعة"
        ]
        return random.choice(urgent_phrases)
    return None


def get_purchase_history_phrase(previous_purchases: List) -> Optional[str]:
    """بتضيف عبارة شخصية بناءً على المشتريات السابقة للعميل"""
    if not previous_purchases or random.random() > 0.7:  # مش كل مرة هنستخدم المشتريات السابقة
        return None
    
    # عبارات مخصصة حسب التاريخ السابق
    history_phrases = [
        "وأكيد هتعجبك زي اللي اشتريته المرة اللي فاتت",
        "وشبه اللي كنت مبسوط بيه قبل كده عندنا",
        "على نفس مستوى جودة مشترياتك السابقة",
        "وهتكمل مع مجموعتك الحلوة اللي عندك",
        "وهتلاقيها متوافقة مع ذوقك اللي عرفناه"
    ]
    
    # أحيانًا نذكر نوع منتج محدد من المشتريات السابقة
    if random.random() < 0.4 and len(previous_purchases) > 0:
        # افتراض أن previous_purchases عبارة عن قائمة بها أسماء المنتجات السابقة
        sample_product = random.choice(previous_purchases)
        personalized_phrases = [
            f"وهتناسب {sample_product} اللي اشتريته قبل كده",
            f"وزي ما عجبك {sample_product}، دي كمان هتعجبك",
            f"متوافقة مع {sample_product} بتاعك"
        ]
        return random.choice(personalized_phrases)
    
    return random.choice(history_phrases)


def add_random_enhancement(message: str, context: Dict, response_style: str) -> str:
    """
    بتضيف تعبير عشوائي للتنويع أو نصيحة أو تشجيع
    """
    # أنواع مختلفة من التعزيزات
    enhancements = [
        'encouragement',  # تشجيع للشراء
        'tip',            # نصيحة مفيدة
        'urgency',        # إشعار بعرض محدود
        'social_proof',   # إثبات اجتماعي
        'question'        # سؤال تفاعلي
    ]
    
    # اختيار نوع التعزيز عشوائيًا مع مراعاة النمط
    if response_style == 'حماسي':
        weighted_enhancements = ['encouragement', 'urgency', 'social_proof', 'encouragement', 'urgency']
    elif response_style == 'ودود':
        weighted_enhancements = ['encouragement', 'tip', 'question', 'question', 'tip']
    elif response_style == 'مرح':
        weighted_enhancements = ['question', 'encouragement', 'social_proof', 'urgency', 'question']
    elif response_style == 'مساعد':
        weighted_enhancements = ['tip', 'tip', 'question', 'encouragement', 'tip']
    elif response_style == 'عملي':
        weighted_enhancements = ['tip', 'social_proof', 'tip', 'encouragement', 'tip']
    else:
        weighted_enhancements = enhancements
    
    enhancement_type = random.choice(weighted_enhancements)
    
    # عبارات مختلفة حسب نوع التعزيز
    enhancement_phrases = {
        'encouragement': [
            "اتفرج عليهم وقوللي رأيك!",
            "شوفهم وقوللي عجبوك ولا عندك فكرة تانية؟",
            "أتمنى حاجة منهم تعجبك 🙏",
            "قوللي اللي يعجبك وأساعدك تظبطه على طول",
            "وأنا واثق إنهم هيعجبوك جدًا!",
            "وأضمنلك الجودة والسعر المناسب",
            "دوس على اللي يعجبك عشان تشوف التفاصيل",
            "وطبعًا في ضمان على كل المنتجات"
        ],
        'tip': [
            "نصيحة مني، شوف التقييمات الأول قبل ما تختار",
            "وأنصحك تطلب بدري عشان تضمن التوصيل في الوقت المناسب",
            "خد بالك، ممكن تعمل مقارنة بينهم من صفحة المقارنة",
            "من تجارب عملاء قبلك، أحجام المنتجات دي مظبوطة",
            "متنساش كمان تشوف العروض المتعلقة بيها",
            "نصيحة صغيرة: دايمًا اطلب حاجة زيادة عشان توفر في الشحن",
            "اطلب دلوقتي عشان تلحق المخزون"
        ],
        'urgency': [
            "وفي خصم 15% لو طلبت النهاردة بس!",
            "والكميات محدودة، فمتتأخرش!",
            "وفي هدية مجانية مع الطلبات النهاردة!",
            "واستفاد من الشحن المجاني للطلبات فوق 500 جنيه",
            "السعر ده لمدة محدودة بس!",
            "وعرض خاص: اشتري قطعتين والتالتة بنص السعر!"
        ],
        'social_proof': [
            "عملاءنا مبسوطين جدًا بالمنتجات دي",
            "الموديلات دي من أكتر الحاجات اللي الناس بتشتريها",
            "مبيعات الأسبوع ده عليها كتيرة جدًا",
            "العملاء اللي اشتروا زيها رجعوا يشتروا تاني",
            "الحاجات دي بتخلص بسرعة من كتر طلبات الناس عليها",
            "من أكتر المنتجات إيجابية في تقييمات العملاء"
        ],
        'question': [
            "إيه رأيك فيهم؟",
            "تحب أرشحلك حاجات تانية؟",
            "لقيت اللي كنت بتدور عليه؟",
            "عايز مساعدة في الاختيار؟",
            "محتاج معلومات أكتر عن أي منتج منهم؟",
            "فيه اقتراح تاني عندك؟",
            "يا ترى المقاسات دي مناسبة؟"
        ]
    }
    
    # اختيار عبارة مناسبة
    selected_phrase = random.choice(enhancement_phrases[enhancement_type])
    
    # إضافة العبارة للرسالة بشكل طبيعي
    connector = random.choice([" ", " و", ". "])
    return f"{message}{connector}{selected_phrase}"


def add_contextual_emojis(message: str, context: Dict) -> str:
    """
    تضيف إيموجي مناسب للسياق بشكل مدروس (مش كتير)
    """
    # نسبة احتمالية إضافة إيموجي
    if random.random() > 0.7:  # 70% فرصة لإضافة إيموجي
        return message
    
    # قائمة من الإيموجي حسب المناسبة والسياق
    occasion_emojis = {
        'عيد ميلاد': ['🎂', '🎁', '🎉', '🎊', '🥳'],
        'زواج': ['💍', '💒', '👰', '🤵', '💐'],
        'تخرج': ['🎓', '📚', '🧑‍🎓', '👨‍🎓', '👩‍🎓'],
        'مولود جديد': ['👶', '🍼', '🧸', '👼', '🤱'],
        'خطوبة': ['💍', '💕', '💘', '❤️', '💖']
    }
    
    type_emojis = {
        'بنت': ['👧', '👩', '💅', '👱‍♀️'],
        'ولد': ['👦', '👨', '👱‍♂️', '🧔'],
        'طفل': ['👶', '🧒', '🧸'],
        'رجل': ['👨', '🧔', '👨‍💼'],
        'امرأة': ['👩', '👩‍💼', '👱‍♀️']
    }
    
    interest_emojis = {
        'رياضة': ['⚽', '🏀', '🏃‍♂️', '🏋️‍♂️', '🏊‍♀️'],
        'موسيقى': ['🎵', '🎸', '🎹', '🎧', '🎼'],
        'قراءة': ['📚', '📖', '📕', '✏️'],
        'تكنولوجيا': ['📱', '💻', '⌚', '🖥️', '🎮'],
        'سفر': ['✈️', '🧳', '🏝️', '🗺️', '🏖️'],
        'طبخ': ['🍳', '👨‍🍳', '👩‍🍳', '🍽️', '🥘'],
        'فنون': ['🎨', '🖌️', '🎭', '🧵', '🎬']
    }
    
    # اختيار الإيموجي المناسب
    selected_emoji = None
    
    # البحث في المناسبة أولاً
    if context.get('occasion'):
        for key, emojis in occasion_emojis.items():
            if key in context['occasion'].lower():
                selected_emoji = random.choice(emojis)
                break
    
    # إذا لم نجد إيموجي للمناسبة، نبحث في نوع الشخص
    if not selected_emoji and context.get('type'):
        for key, emojis in type_emojis.items():
            if key in context['type'].lower():
                selected_emoji = random.choice(emojis)
                break
    
    # إذا لم نجد إيموجي للنوع، نبحث في الاهتمامات
    if not selected_emoji and context.get('interests'):
        for interest in context['interests']:
            for key, emojis in interest_emojis.items():
                if key in interest.lower():
                    selected_emoji = random.choice(emojis)
                    break
            if selected_emoji:
                break
    
    # إذا لم نجد أي إيموجي مناسب، نستخدم إيموجي عام
    if not selected_emoji:
        general_emojis = ['👍', '✨', '💯', '🔥', '⭐', '🌟', '🎯']
        selected_emoji = random.choice(general_emojis)
    
    # إضافة الإيموجي في نهاية الرسالة
    return f"{message} {selected_emoji}"


def get_time_of_day() -> str:
    """
    بتحدد وقت اليوم عشان نضبط التحية بشكل أفضل
    """
    import datetime
    hour = datetime.datetime.now().hour
    
    if 5 <= hour < 12:
        return "صباح"
    elif 12 <= hour < 17:
        return "ظهر"
    elif 17 <= hour < 22:
        return "مساء"
    else:
        return "ليل"