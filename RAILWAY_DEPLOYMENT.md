# Railway Deployment Rehberi

Django projenizi Railway'de deploy etmek için modern ve hızlı rehber.

## 🚀 Railway Avantajları
- ✅ Otomatik HTTPS
- ✅ Global CDN
- ✅ Otomatik scaling
- ✅ PostgreSQL database dahil
- ✅ Git entegrasyonu
- ✅ Disk kotası sorunu yok
- ✅ Ücretsiz tier (500 saat/ay)

## 📁 Hazır Dosyalar
✅ `Dockerfile` - Container yapılandırması
✅ `railway.json` - Railway ayarları
✅ `Procfile` - Web server yapılandırması
✅ `requirements_railway.txt` - Optimize edilmiş paketler
✅ `.env.example` - Environment variables şablonu

## 🛠️ Deployment Adımları

### 1. Railway Hesabı Oluşturun
- [Railway.app](https://railway.app) adresine gidin
- GitHub ile giriş yapın
- Ücretsiz hesap oluşturun

### 2. PostgreSQL Database Oluşturun
```bash
# Railway Dashboard'da:
1. "New Project" tıklayın
2. "Provision PostgreSQL" seçin
3. Database bilgilerini not alın
```

### 3. GitHub Repository'yi Railway'e Bağlayın
```bash
# Railway Dashboard'da:
1. "New Service" → "GitHub Repo"
2. Lgram-web repository'sini seçin
3. Otomatik deploy başlayacak
```

### 4. Environment Variables Ayarlayın
Railway Dashboard → Settings → Environment Variables:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DATABASE_URL=postgresql://user:pass@host:port/dbname
RAILWAY_PUBLIC_DOMAIN=your-app.railway.app
```

### 5. Custom Domain (İsteğe Bağlı)
```bash
# Railway Dashboard'da:
1. Settings → Domains
2. "Custom Domain" ekleyin
3. DNS ayarlarını yapın
```

## 🔧 Otomatik Deployment

Railway otomatik olarak:
1. ✅ Git push'larda yeniden deploy eder
2. ✅ Database migrations çalıştırır
3. ✅ Static files toplar
4. ✅ SpaCy modelini indirir
5. ✅ HTTPS sertifikası oluşturur

## 📊 Monitoring & Logs

Railway Dashboard'da:
- **Deployments**: Deploy geçmişi
- **Metrics**: CPU, RAM, Network kullanımı
- **Logs**: Real-time application logs
- **Settings**: Environment variables

## 🛡️ Güvenlik

Production ayarları otomatik aktif:
- ✅ DEBUG = False
- ✅ HTTPS force redirect
- ✅ Secure cookies
- ✅ XSS protection
- ✅ Content security policy

## 💾 Database Yönetimi

```bash
# Railway CLI ile (opsiyonel)
# Terminal'de:
railway login
railway connect
python manage.py shell
```

## 🔄 Manuel Deploy

```bash
# Değişiklikler sonrası:
git add .
git commit -m "Update"
git push origin main
# Railway otomatik deploy edecek
```

## 📈 Scaling

Railway otomatik scaling yapar:
- **Free tier**: 512MB RAM, 1GB disk
- **Paid plans**: Unlimited scaling
- **Auto-sleep**: 5 dakika inaktivite sonrası

## 🐛 Troubleshooting

### Build Failures
```bash
# Railway Dashboard → Deployments → Logs
# Hata mesajlarını kontrol edin

# Yaygın sorunlar:
1. requirements.txt hatası → requirements_railway.txt kontrol edin
2. Migration hatası → DATABASE_URL kontrol edin
3. Static files hatası → STATIC_ROOT ayarlarını kontrol edin
```

### Database Connection
```bash
# Environment variables kontrol:
echo $DATABASE_URL

# Django shell'de test:
python manage.py dbshell
```

### SpaCy Model
```bash
# Model indirme sorunu:
python -m spacy download en_core_web_sm
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('Model loaded!')"
```

## 🚀 Go Live

Deployment tamamlandığında:
1. ✅ `https://your-app.railway.app` adresiniz hazır
2. ✅ PostgreSQL database aktif
3. ✅ Static files CDN'de
4. ✅ Otomatik HTTPS aktif
5. ✅ Monitoring dashboards hazır

## 📞 Destek

- Railway Docs: https://docs.railway.app/
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- Railway Discord: https://discord.gg/railway

---

🎉 **Tebrikler!** Projeniz Railway'de live!

Railway > PythonAnywhere avantajları:
- ⚡ Çok daha hızlı
- 🌍 Global CDN
- 🔒 Otomatik HTTPS
- 💾 Disk kotası yok
- 🔄 Git otomasyonu
- 📊 Gelişmiş monitoring