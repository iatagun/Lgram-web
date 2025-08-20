from django.contrib import admin


from .models import GeneratedText
from django.contrib import admin

@admin.register(GeneratedText)
class GeneratedTextAdmin(admin.ModelAdmin):
	list_display = ("session_key", "input_text", "generated_text", "created_at")
	search_fields = ("input_text", "generated_text", "session_key")
