# PythonAnywhere Deployment Rehberi

Bu rehber, Django projenizi PythonAnywhere'e deploy etmek için gereken adımları içerir.

## Ön Hazırlık

### 1. PythonAnywhere Hesabı
- [PythonAnywhere](https://www.pythonanywhere.com) sitesinde hesap oluşturun
- Beginner (ücretsiz) veya ücretli hesap seçin

### 2. Proje Dosyaları Hazırlığı
✅ `requirements.txt` - Gerekli Python paketleri
✅ `lgramweb/settings.py` - Production ayarları
✅ `wsgi_pythonanywhere.py` - WSGI yapılandırması

## PythonAnywhere'e Deploy Adımları

### Adım 1: Dosyaları Yükleyin

#### Seçenek A: Git ile (Önerilen)
```bash
# PythonAnywhere Bash Console'da
cd ~
git clone https://github.com/iatagun/Lgram-web.git
cd Lgram-web
```

#### Seçenek B: Dosya Yükleme
- PythonAnywhere Dashboard → Files
- Proje dosyalarını `/home/yourusername/Lgram-web/` klasörüne yükleyin

### Adım 2: Virtual Environment Oluşturun

```bash
# PythonAnywhere Bash Console'da
cd ~
python3.11 -m venv lgram-venv
source lgram-venv/bin/activate
cd Lgram-web
pip install -r requirements.txt
```

### Adım 3: SpaCy Model İndirin

```bash
# Virtual environment aktifken
python -m spacy download en_core_web_sm
```

### Adım 4: Django Ayarları

```bash
# Database migrations
python manage.py makemigrations
python manage.py migrate

# Superuser oluşturun
python manage.py createsuperuser

# Static files topla
python manage.py collectstatic --noinput
```

### Adım 5: Web App Oluşturun

1. PythonAnywhere Dashboard → Web
2. "Add a new web app" tıklayın
3. Domain seçin: `yourusername.pythonanywhere.com`
4. "Manual configuration" seçin
5. Python version: 3.11

### Adım 6: WSGI Dosyasını Yapılandırın

1. Web tab'inde "WSGI configuration file" linkini tıklayın
2. Dosya içeriğini şununla değiştirin:

```python
import os
import sys

# Virtual environment
path = '/home/yourusername/lgram-venv/lib/python3.11/site-packages'
if path not in sys.path:
    sys.path.insert(0, path)

# Project directory
path = '/home/yourusername/Lgram-web'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'lgramweb.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Adım 7: Static Files Ayarları

1. Web tab'inde "Static files" bölümüne:
   - URL: `/static/`
   - Directory: `/home/yourusername/Lgram-web/staticfiles/`

### Adım 8: Environment Variables (İsteğe Bağlı)

Web tab'inde "Environment variables" bölümüne:
- `DJANGO_DEBUG`: `False`
- `DJANGO_SECRET_KEY`: (yeni bir secret key üretin)

### Adım 9: Domain Ayarları

`lgramweb/settings.py` dosyasında:
```python
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1',
    'yourusername.pythonanywhere.com',  # Kendi domain'inizi yazın
]
```

### Adım 10: Reload ve Test

1. Web tab'inde "Reload" butonuna tıklayın
2. `https://yourusername.pythonanywhere.com` adresine gidin
3. Sitenizin çalıştığını kontrol edin

## Sorun Giderme

### Error Logs
- Web tab → Error log linkini kontrol edin
- Server log linkini kontrol edin

### Yaygın Sorunlar

1. **ALLOWED_HOSTS hatası**
   - `settings.py`'de domain'inizi eklediğinizden emin olun

2. **Static files görünmüyor**
   - `python manage.py collectstatic` çalıştırın
   - Static files yolunu kontrol edin

3. **Import errors**
   - Virtual environment'ın doğru kurulduğunu kontrol edin
   - Requirements.txt'deki paketlerin kurulu olduğunu kontrol edin

4. **Database errors**
   - Migrations'ları çalıştırdığınızdan emin olun
   - Database dosyasının yazma izinlerini kontrol edin

### Güncelleme Yapmak

```bash
# Git ile güncellemek için
cd ~/Lgram-web
git pull origin main
source ~/lgram-venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
# Web app'i reload edin
```

## Güvenlik Notları

1. Production'da yeni bir SECRET_KEY kullanın
2. DEBUG = False olarak ayarlayın
3. HTTPS kullanın (ücretli hesaplarda mevcut)
4. Database backup'larını düzenli alın

## Destek

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/

---

Bu rehberi takip ederek projenizi başarıyla PythonAnywhere'e deploy edebilirsiniz.