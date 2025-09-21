#!/bin/bash
# PythonAnywhere Quick Setup Script
# Disk quota sorunlarını önlemek için optimize edilmiş kurulum

echo "🚀 PythonAnywhere için Lgram-web kurulum başlıyor..."

# Virtual environment oluştur
echo "📦 Virtual environment oluşturuluyor..."
python3.11 -m venv lgram-venv
source lgram-venv/bin/activate

# Pip'i güncelle ve cache temizle
echo "🔄 Pip güncelleniyor ve cache temizleniyor..."
pip install --upgrade pip
pip cache purge

# Temel paketleri kur
echo "📚 Temel paketler kuruluyor..."
pip install --no-cache-dir Django==4.2.24
pip install --no-cache-dir django-bootstrap5==25.1
pip install --no-cache-dir centering-lgram==1.2.1
pip install --no-cache-dir spacy==3.8.7

# Küçük spaCy modelini indir (400MB yerine ~15MB)
echo "🧠 SpaCy modeli indiriliyor (küçük model)..."
python -m spacy download en_core_web_sm

# Diğer gerekli paketleri kur
echo "🔧 Diğer bağımlılıklar kuruluyor..."
pip install --no-cache-dir -r requirements.txt

# Django işlemleri
echo "💾 Django ayarları yapılıyor..."
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

echo "✅ Kurulum tamamlandı!"
echo "🌐 Şimdi Web app'inizde WSGI dosyasını yapılandırın."
echo "📁 Static files: /home/$(whoami)/Lgram-web/staticfiles/"
echo "🔧 WSGI path: /home/$(whoami)/Lgram-web/"

# Disk kullanımını göster
echo "💽 Disk kullanımı:"
du -sh ~/