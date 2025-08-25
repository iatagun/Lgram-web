"""
URL configuration for lgramweb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main.views import (
    index, transition_analysis, coherence_report, 
    login_view, register_view, logout_view, session_info_view,
    profile_view, settings_view, export_data_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('transition-analysis/', transition_analysis, name='transition_analysis'),
    path('coherence-report/', coherence_report, name='coherence_report'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('session-info/', session_info_view, name='session_info'),
    path('profile/', profile_view, name='profile'),
    path('settings/', settings_view, name='settings'),
    path('export-data/', export_data_view, name='export_data'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
