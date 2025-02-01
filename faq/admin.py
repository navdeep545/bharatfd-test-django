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