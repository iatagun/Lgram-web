#!/bin/bash
# PythonAnywhere Optimized Setup Script
# Minimal disk usage deployment

echo "🚀 PythonAnywhere için Lgram-web kurulum başlıyor..."
echo "📊 Mevcut disk kullanımı:"
du -sh ~ 2>/dev/null || echo "Disk kontrol edilemiyor"

# Temizlik işlemi
echo "🧹 Cache ve geçici dosyaları temizleniyor..."
rm -rf ~/.cache/pip 2>/dev/null
pip cache purge 2>/dev/null

# Virtual environment oluştur (sadece yoksa)
if [ ! -d "~/.virtualenvs/lgram-venv" ]; then
    echo "📦 Virtual environment oluşturuluyor..."
    mkvirtualenv --python=python3.10 lgram-venv
else
    echo "📦 Mevcut virtual environment kullanılıyor..."
    workon lgram-venv
fi

# Proje dizinine git
cd ~/Lgram-web || { echo "❌ Proje dizini bulunamadı!"; exit 1; }

echo "� Minimal paketler kuruluyor (disk kotası optimizasyonu)..."
# Önce temel Django'yu kur
pip install --no-cache-dir Django==4.2.24
pip install --no-cache-dir django-bootstrap5==25.1

# SpaCy ve centering-lgram'ı dikkatli kur
echo "🧠 Text processing paketleri kuruluyor..."
pip install --no-cache-dir spacy==3.8.7 --no-deps
pip install --no-cache-dir centering-lgram==1.2.1 --no-deps

# Gerekli bağımlılıkları tek tek kur
echo "🔧 Gerekli bağımlılıklar kuruluyor..."
pip install --no-cache-dir numpy
pip install --no-cache-dir requests

# Küçük spaCy modelini indir
echo "⬇️ SpaCy modeli indiriliyor (küçük model ~15MB)..."
python -m spacy download en_core_web_sm

# Django veritabanı işlemleri
echo "💾 Django veritabanı ayarları..."
python manage.py makemigrations
python manage.py migrate

# Static files topla
echo "📁 Static files toplanıyor..."
python manage.py collectstatic --noinput

# Disk kullanımını kontrol et
echo "📊 Kurulum sonrası disk kullanımı:"
du -sh ~ 2>/dev/null || echo "Disk kontrol edilemiyor"

echo ""
echo "✅ Kurulum tamamlandı!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Sonraki adımlar:"
echo "1. Web app'te WSGI dosyasını yapılandırın"
echo "2. Static files yolunu ayarlayın: ~/Lgram-web/staticfiles"
echo "3. Virtual environment yolunu ayarlayın: ~/.virtualenvs/lgram-venv"
echo "4. Reload butonuna basın"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"