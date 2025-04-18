import unittest
from understanding import extract_context # Assuming the code above is saved as understanding.py

class TestUnderstanding(unittest.TestCase):

    def test_occasion_extraction(self):
        q = "هديه عيد ميلاد لبابا"
        context = extract_context(q)
        self.assertEqual(context["occasion"], "عيد ميلاد")

        q = "افكار لرمضان"
        context = extract_context(q)
        self.assertEqual(context["occasion"], "رمضان")

        q = "هدايا للعيد الكبير"
        context = extract_context(q)
        self.assertEqual(context["occasion"], "عيد الأضحى")

    def test_recipient_type_extraction(self):
        q = "هديه لماما"
        context = extract_context(q)
        self.assertEqual(context["recipient_type"], "أم")

        q = "عايز حاجه لولد صاحبي"
        context = extract_context(q)
        self.assertEqual(context["recipient_type"], "صديق") # Matches صديق first

        q = "هديه لبنوته صغيره"
        context = extract_context(q)
        self.assertEqual(context["recipient_type"], "بنت")

    def test_age_extraction(self):
        q = "هديه لطفل عنده 5 سنين"
        context = extract_context(q)
        self.assertEqual(context["age"]["numerical"], 5)
        self.assertEqual(context["age"]["group"], "طفل")

        q = "هديه لشاب في العشرينات"
        context = extract_context(q)
        self.assertIsNone(context["age"].get("numerical")) # No specific number
        self.assertEqual(context["age"]["group"], "شاب/ة")

        q = "لواحد كبير فوق الستين"
        context = extract_context(q)
        self.assertIsNone(context["age"].get("numerical"))
        self.assertEqual(context["age"]["group"], "كبير السن")

        q = "بنت عمرها 18 سنة"
        context = extract_context(q)
        self.assertEqual(context["age"]["numerical"], 18)
        self.assertEqual(context["age"]["group"], "مراهق") # Inferred from number

    def test_interest_extraction(self):
        q = "لحد بيحب القرايه و المزيكا"
        context = extract_context(q)
        self.assertIn("قراءة/كتب", context["interests"])
        self.assertIn("موسيقى", context["interests"])
        self.assertEqual(len(context["interests"]), 2)

        q = "شاب رياضي بيحب الجيم"
        context = extract_context(q)
        self.assertIn("رياضة", context["interests"])

        q = "واحد بيحب العربيات والتكنولوجيا"
        context = extract_context(q)
        self.assertIn("سيارات", context["interests"])
        self.assertIn("تكنولوجيا/ألعاب", context["interests"])

    def test_budget_extraction(self):
        q = "ميزانيه في حدود 500 جنيه"
        context = extract_context(q)
        self.assertIsNone(context["budget"].get("min"))
        self.assertIsNone(context["budget"].get("max"))
        self.assertEqual(context["budget"]["approx"], 500)
        self.assertIsNone(context["budget"].get("qualitative"))

        q = "عايز حاجه رخيصه"
        context = extract_context(q)
        self.assertEqual(context["budget"]["qualitative"], "رخيص")
        self.assertIsNone(context["budget"].get("approx"))

        q = "من 200 ل 300 جنيه مصري"
        context = extract_context(q)
        self.assertEqual(context["budget"]["min"], 200)
        self.assertEqual(context["budget"]["max"], 300)
        self.assertIsNone(context["budget"].get("approx"))

        q = "حاجه فخمه اوي مش مهم السعر"
        context = extract_context(q)
        # It might match both "فخم" and "مفتوح" based on keywords.
        # Current logic might pick one based on order. Let's test qualitative is picked.
        self.assertIn(context["budget"]["qualitative"], ["غالي", "مفتوح"]) # Accept either if both keywords are present

    def test_urgency_extraction(self):
        q = "محتاج هديه ضروري جدا لبكره"
        context = extract_context(q)
        self.assertEqual(context["urgency"], "عاجل")

        q = "بفكر في هديه للشهر الجاي"
        context = extract_context(q)
        self.assertEqual(context["urgency"], "غير عاجل")

    def test_gender_extraction_and_inference(self):
        q = "هديه لزميلي في الشغل"
        context = extract_context(q)
        self.assertEqual(context["recipient_type"], "زميل عمل")
        self.assertEqual(context["gender"], "ذكر") # Inferred

        q = "هديه لصديقتي البنت"
        context = extract_context(q)
        self.assertEqual(context["recipient_type"], "صديقة")
        self.assertEqual(context["gender"], "أنثى") # Inferred

        q = "عايز حاجه حريمي"
        context = extract_context(q)
        self.assertEqual(context["gender"], "أنثى") # Explicitly mentioned

        q = "هدية رجالي"
        context = extract_context(q)
        self.assertEqual(context["gender"], "ذكر") # Explicitly mentioned

    def test_combined_extraction(self):
        q = "عايز هدية عيد ميلاد لبنت اختي عندها 15 سنة بتحب الميكب والمزيكا وميزانيتي حوالي 500ج"
        context = extract_context(q)
        self.assertEqual(context["occasion"], "عيد ميلاد")
        self.assertEqual(context["recipient_type"], "بنت") # Might match بنت or اخت depending on order/phrasing
        self.assertEqual(context["age"]["numerical"], 15)
        self.assertEqual(context["age"]["group"], "مراهق")
        self.assertIn("مكياج/عناية بالبشرة", context["interests"])
        self.assertIn("موسيقى", context["interests"])
        self.assertEqual(context["budget"]["approx"], 500)
        self.assertEqual(context["gender"], "أنثى") # Inferred from 'بنت'

    def test_no_match(self):
        q = "اهلا بيك"
        context = extract_context(q)
        self.assertIsNone(context["occasion"])
        self.assertIsNone(context["recipient_type"])
        self.assertEqual(context["age"], {})
        self.assertEqual(context["interests"], [])
        self.assertEqual(context["budget"], {})
        self.assertIsNone(context["urgency"])
        self.assertIsNone(context["gender"])

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)