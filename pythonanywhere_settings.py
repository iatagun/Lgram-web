"""
PythonAnywhere specific settings
Import this in your main settings.py for PythonAnywhere deployment
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# PythonAnywhere Production Settings
DEBUG = False
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1', 
    'yourusername.pythonanywhere.com',  # Replace with your actual username
    '.pythonanywhere.com'
]

# Database - keep SQLite for PythonAnywhere free accounts
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files for PythonAnywhere
STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourusername/Lgram-web/staticfiles'  # Replace yourusername
STATICFILES_DIRS = [
    BASE_DIR / "main" / "static",
]

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Disable WhiteNoise for PythonAnywhere (they handle static files)
# Remove WhiteNoise middleware if present in main settings