 
Here's a step-by-step guide to complete the assignment:

### **1. Project Setup**
- **Create a Django Project**
  ```bash
  django-admin startproject faq_project
  cd faq_project
  python manage.py startapp faq
  ```
- **Install Required Packages**
  ```bash
  pip install django djangorestframework django-ckeditor django-redis googletrans==4.0.0-rc1
  ```

### **2. Model Design**
- **Update `faq/models.py`**
  ```python
  from django.db import models
  from ckeditor.fields import RichTextField
  from googletrans import Translator

  class FAQ(models.Model):
      # English (default)
      question_en = models.TextField()
      answer_en = RichTextField()
      
      # Hindi translations
      question_hi = models.TextField(blank=True)
      answer_hi = RichTextField(blank=True)
      
      # Bengali translations
      question_bn = models.TextField(blank=True)
      answer_bn = RichTextField(blank=True)

      def get_translated_field(self, field_prefix, lang):
          return getattr(self, f'{field_prefix}_{lang}', getattr(self, f'{field_prefix}_en'))

      def save(self, *args, **kwargs):
          if not self.pk:  # New instance
              translator = Translator()
              langs = ['hi', 'bn']
              for lang in langs:
                  try:
                      # Translate question
                      setattr(self, f'question_{lang}', 
                              translator.translate(self.question_en, dest=lang).text)
                      # Translate answer (caution with HTML)
                      setattr(self, f'answer_{lang}', 
                              translator.translate(self.answer_en, dest=lang).text)
                  except Exception:
                      # Fallback to English
                      setattr(self, f'question_{lang}', self.question_en)
                      setattr(self, f'answer_{lang}', self.answer_en)
          super().save(*args, **kwargs)
  ```

### **3. WYSIWYG Integration**
- **Update `settings.py`**
  ```python
  INSTALLED_APPS = [
      ...
      'ckeditor',
      'faq',
  ]
  ```

### **4. Admin Panel**
- **Update `faq/admin.py`**
  ```python
  from django.contrib import admin
  from .models import FAQ

  @admin.register(FAQ)
  class FAQAdmin(admin.ModelAdmin):
      fieldsets = (
          ('English', {
              'fields': ('question_en', 'answer_en'),
          }),
          ('Hindi', {
              'fields': ('question_hi', 'answer_hi'),
          }),
          ('Bengali', {
              'fields': ('question_bn', 'answer_bn'),
          }),
      )
  ```

### **5. API Development**
- **Create `faq/serializers.py`**
  ```python
  from rest_framework import serializers
  from .models import FAQ

  class FAQSerializer(serializers.ModelSerializer):
      question = serializers.SerializerMethodField()
      answer = serializers.SerializerMethodField()

      class Meta:
          model = FAQ
          fields = ['id', 'question', 'answer']

      def get_question(self, obj):
          lang = self.context['request'].query_params.get('lang', 'en')
          return obj.get_translated_field('question', lang)

      def get_answer(self, obj):
          lang = self.context['request'].query_params.get('lang', 'en')
          return obj.get_translated_field('answer', lang)
  ```
- **Create `faq/views.py`**
  ```python
  from django.core.cache import cache
  from rest_framework import viewsets
  from .models import FAQ
  from .serializers import FAQSerializer

  class FAQViewSet(viewsets.ModelViewSet):
      queryset = FAQ.objects.all()
      serializer_class = FAQSerializer

      def list(self, request, *args, **kwargs):
          lang = request.query_params.get('lang', 'en')
          cache_key = f'faqs_{lang}'
          cached_data = cache.get(cache_key)
          if cached_data:
              return Response(cached_data)
          response = super().list(request, *args, **kwargs)
          cache.set(cache_key, response.data, timeout=60*15)
          return response
  ```

### **6. Configure Caching (Redis)**
- **Update `settings.py`**
  ```python
  CACHES = {
      "default": {
          "BACKEND": "django_redis.cache.RedisCache",
          "LOCATION": "redis://127.0.0.1:6379/1",
          "OPTIONS": {
              "CLIENT_CLASS": "django_redis.client.DefaultClient",
          }
      }
  }
  ```

### **7. URL Configuration**
- **Update `faq_project/urls.py`**
  ```python
  from django.urls import path, include
  from rest_framework.routers import DefaultRouter
  from faq.views import FAQViewSet

  router = DefaultRouter()
  router.register(r'faqs', FAQViewSet)

  urlpatterns = [
      path('admin/', admin.site.urls),
      path('api/', include(router.urls)),
  ]
  ```

### **8. Testing**
- **Create `faq/tests.py`**
  ```python
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
  ```

### **9. Documentation (README.md)**
```markdown
# FAQ API with Multi-language Support

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/faq-project.git
   cd faq-project
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Start Redis server.
5. Run the server:
   ```bash
   python manage.py runserver
   ```

## API Usage
- Fetch FAQs in English:
  ```bash
  curl http://localhost:8000/api/faqs/
  ```
- Fetch FAQs in Hindi:
  ```bash
  curl http://localhost:8000/api/faqs/?lang=hi
  ```
```

### **10. Git Commits**
```bash
git add .
git commit -m "feat: Add multilingual FAQ model with WYSIWYG support"
git commit -m "api: Implement REST API with language support"
git commit -m "cache: Add Redis caching for API responses"
```

---

**Final Checks**
- Ensure PEP8 compliance using `flake8`.
- Run tests with `python manage.py test`.
- Verify admin interface at `http://localhost:8000/admin`.

This structured approach covers all requirements, from model design to deployment readiness.

please explain me the step 9 
