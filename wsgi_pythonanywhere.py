# This file contains the WSGI configuration required to serve up your
# web application at http://<your-username>.pythonanywhere.com/
# It has been auto-generated for your Django project

import os
import sys

# Add your project directory to the sys.path
# This is so that Django can find your application files
path = '/home/yourusername/Lgram-web'  # Replace 'yourusername' with your actual username
if path not in sys.path:
    sys.path.insert(0, path)

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'lgramweb.settings'

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()