# PythonAnywhere Deployment Checklist

## 🚀 Hızlı Deploy Rehberi

### 1️⃣ PythonAnywhere Hesabı
- [ ] [PythonAnywhere.com](https://www.pythonanywhere.com)'da ücretsiz hesap oluştur
- [ ] Beginner plan seç (500MB disk, ücretsiz)

### 2️⃣ Proje Hazırlığı
- [x] `requirements_pythonanywhere.txt` - optimize edilmiş paketler
- [x] `setup_pythonanywhere.sh` - otomatik kurulum scripti
- [x] `wsgi_pythonanywhere.py` - WSGI yapılandırması
- [x] `pythonanywhere_settings.py` - production ayarları

### 3️⃣ Deploy Adımları

#### A) Dosyaları Yükle
```bash
# PythonAnywhere Bash Console
cd ~
git clone https://github.com/iatagun/Lgram-web.git
cd Lgram-web
```

#### B) Otomatik Kurulum Çalıştır
```bash
chmod +x setup_pythonanywhere.sh
./setup_pythonanywhere.sh
```

#### C) Web App Oluştur
1. Dashboard → Web → "Add a new web app"
2. Manual configuration → Python 3.10 seç
3. Next → Next → Create

#### D) WSGI Dosyasını Yapılandır
1. Web tab → WSGI configuration file linkine tıkla
2. Dosya içeriğini `wsgi_pythonanywhere.py` ile değiştir
3. `yourusername` kısımlarını kendi kullanıcı adınla değiştir

#### E) Virtual Environment Ayarla
1. Web tab → Virtualenv bölümü
2. Path: `/home/yourusername/.virtualenvs/lgram-venv`

#### F) Static Files Ayarla
1. Web tab → Static files bölümü
2. URL: `/static/`
3. Directory: `/home/yourusername/Lgram-web/staticfiles/`

### 4️⃣ Son Kontroller

#### ALLOWED_HOSTS Güncelle
```python
# lgramweb/settings.py dosyasında:
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1', 
    'yourusername.pythonanywhere.com',  # Kendi kullanıcı adınız
    '.pythonanywhere.com'
]
```

#### Test Et
1. Web tab → Reload butonu
2. `https://yourusername.pythonanywhere.com` adresine git
3. Site açılıyor mu kontrol et

### 5️⃣ Sorun Giderme

#### Error Log Kontrol
- Web tab → Error log linkine tıkla
- Server log linkine tıkla

#### Yaygın Hatalar
```bash
# Disk kotası aştı
du -sh ~  # Disk kullanımını kontrol et
pip cache purge  # Cache temizle

# SpaCy modeli bulunamadı  
python -m spacy download en_core_web_sm

# Permission denied
chmod +x setup_pythonanywhere.sh

# Virtual environment bulunamadı
mkvirtualenv --python=python3.10 lgram-venv
```

### 6️⃣ Güncellemeler

```bash
# Kod güncellemek için:
cd ~/Lgram-web
git pull origin main
workon lgram-venv
python manage.py migrate
python manage.py collectstatic --noinput
# Web app'te Reload butonuna bas
```

## ⚡ Önemli Notlar

- **Disk Kotası:** Ücretsiz hesapta 500MB sınır var
- **CPU Seconds:** Günde 100 CPU saniye sınır  
- **Web App:** Sadece 1 web app ücretsiz
- **HTTPS:** Otomatik dahil
- **Database:** SQLite kullanıyoruz (PostgreSQL ücretli)

## 📊 Performans Optimizasyonları

- ✅ Minimal paket kurulumu (~50MB)
- ✅ Küçük SpaCy modeli (~15MB vs 400MB)
- ✅ SQLite database (dosya bazlı)
- ✅ Static files optimize edildi
- ✅ Cache devre dışı

## 🎉 Başarı!

Site çalışıyorsa:
- ✅ `https://yourusername.pythonanywhere.com` adresiniz aktif
- ✅ Text generation çalışıyor
- ✅ Progress tracking aktif
- ✅ Bootstrap UI düzgün görünüyor

---

**⚠️ Ücretsiz Plan Sınırları:**
- 500MB disk alanı
- 1 web app
- 100 CPU saniye/gün
- SQLite database only