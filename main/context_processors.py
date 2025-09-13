"""
Context processors for the main app
"""
from django.utils import translation
from .translation_helper import simple_translate

def language_context(request):
    """Add language context to all templates"""
    current_language = translation.get_language() or 'en'
    
    return {
        'LANGUAGE_CODE': current_language,
        'simple_translate': lambda text: simple_translate(text, current_language),
    }