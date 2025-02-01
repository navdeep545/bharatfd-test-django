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