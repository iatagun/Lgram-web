# PythonAnywhere WSGI Configuration for Lgram-web
# Upload this file to your PythonAnywhere web app configuration

import os
import sys

# Add your project directory to Python path
# Replace 'yourusername' with your actual PythonAnywhere username
project_home = '/home/yourusername/Lgram-web'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Add virtual environment to Python path  
venv_path = '/home/yourusername/.virtualenvs/lgram-venv/lib/python3.10/site-packages'
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'lgramweb.settings'

# Set environment to production
os.environ.setdefault('DJANGO_ENV', 'production')

# Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()