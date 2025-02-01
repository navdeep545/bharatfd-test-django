from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import FAQ

class FAQTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.faq = FAQ.objects.create(
            question_en="Test question",
            answer_en="<p>Test answer</p>"
        )

    def test_translation(self):
        self.assertEqual(self.faq.get_translated_field('question', 'hi'), self.faq.question_hi)

    def test_api_lang_param(self):
        response = self.client.get('/api/faqs/?lang=hi')
        self.assertEqual(response.status_code, 200)