"""
Simple translation helper for when gettext is not available
"""

TRANSLATIONS = {
    'tr': {
        'Profile': 'Profil',
        'Settings': 'Ayarlar',
        'Session Info': 'Oturum Bilgisi',
        'Logout': 'Çıkış',
        'Login': 'Giriş',
        'Register': 'Kayıt Ol',
        'Statistical Language Model with Centering Theory': 'Merkezleme Teorili İstatistiksel Dil Modeli',
        'An educational demonstration of statistical N-gram language models combined with Centering Theory for coherent text generation.': 'Tutarlı metin üretimi için Merkezleme Teorisi ile birleştirilmiş istatistiksel N-gram dil modellerinin eğitsel bir gösterimi.',
        'This project showcases traditional statistical NLP techniques for educational purposes. Please note that text generation may take considerable time due to computational complexity, and results may vary in quality as this is a research prototype.': 'Bu proje eğitim amaçları için geleneksel istatistiksel NLP tekniklerini sergiler. Hesaplamalı karmaşıklık nedeniyle metin üretiminin önemli zaman alabileceğini ve bu bir araştırma prototipi olduğu için sonuçların kalitesinin değişebileceğini lütfen unutmayın.',
        'Generate': 'Üret',
        'Enter a starting sentence for statistical text generation (processing may take several minutes)...': 'İstatistiksel metin üretimi için başlangıç cümlesi girin (işlem birkaç dakika sürebilir)...',
        'Sentences': 'Cümleler',
        'Length': 'Uzunluk',
        'Model Type': 'Model Türü',
        'Standard Generation': 'Standart Üretim',
        'Centering-Enhanced Generation': 'Merkezleme-Gelişmiş Üretim',
        'Generate Text': 'Metin Üret',
        'History': 'Geçmiş',
        'Clear History': 'Geçmişi Temizle',
        'Show More History': 'Daha Fazla Geçmiş Göster',
        'No Text Generated Yet': 'Henüz Metin Üretilmedi',
        'Start generating text from the Generate tab to see your history here.': 'Geçmişinizi burada görmek için Üret sekmesinden metin üretmeye başlayın.',
        'Please allow sufficient time for the statistical model to process your request.': 'İstatistiksel modelin isteğinizi işlemesi için lütfen yeterli zaman tanıyın.',
        'Generate Your First Text': 'İlk Metninizi Üretin',
        'Generation History': 'Üretim Geçmişi',
        'Please sign in to view your text generation history and track your experiments with the statistical language model.': 'Metin üretim geçmişinizi görüntülemek ve istatistiksel dil modeli ile deneyimlerinizi takip etmek için lütfen oturum açın.',
        'Input Text': 'Giriş Metni',
        'Generated Output': 'Üretilen Çıktı',
        'Copy': 'Kopyala',
        'Completed': 'Tamamlandı',
        'more': 'daha fazla',
        'Loading...': 'Yükleniyor...',
        'Generating...': 'Üretiliyor...',
        'Text copied!': 'Metin kopyalandı!',
        'Copy failed!': 'Kopyalama başarısız!',
        'Please enter some text.': 'Lütfen bir metin girin.',
        'Please enter at least 2 characters.': 'Lütfen en az 2 karakter girin.',
        'Text generated successfully!': 'Metin başarıyla üretildi!',
        'Generation failed': 'Üretim başarısız',
        'History cleared successfully!': 'Geçmiş başarıyla temizlendi!',
        'Are you sure you want to delete all history?': 'Tüm geçmişi silmek istediğinizden emin misiniz?',
        'This action cannot be undone.': 'Bu işlem geri alınamaz.',
        'Deleting...': 'Siliniyor...'
    }
}

def simple_translate(text, language_code):
    """Simple translation function"""
    if language_code == 'tr' and text in TRANSLATIONS['tr']:
        return TRANSLATIONS['tr'][text]
    return text