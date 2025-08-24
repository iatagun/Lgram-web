from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from .models import UserLoginLog, UserActivityLog


def get_client_ip(request):
    """İstek yapan kullanıcının IP adresini alır"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Kullanıcının tarayıcı bilgilerini alır"""
    return request.META.get('HTTP_USER_AGENT', '')


def log_user_login(user, request, successful=True):
    """Kullanıcı girişini kaydet"""
    login_log = UserLoginLog.objects.create(
        user=user,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        session_key=request.session.session_key,
        login_successful=successful
    )
    
    # Aktivite kaydı da oluştur
    log_user_activity(
        user=user,
        action='login',
        description=f'User {"successfully" if successful else "unsuccessfully"} logged in',
        request=request
    )
    
    return login_log


def log_user_logout(user, request):
    """Kullanıcı çıkışını kaydet"""
    # En son login kaydını bul ve logout zamanını güncelle
    try:
        login_log = UserLoginLog.objects.filter(
            user=user,
            logout_time__isnull=True,
            login_successful=True
        ).latest('login_time')
        login_log.logout_time = timezone.now()
        login_log.save()
    except UserLoginLog.DoesNotExist:
        pass
    
    # Aktivite kaydı oluştur
    log_user_activity(
        user=user,
        action='logout',
        description='User logged out',
        request=request
    )


def log_user_activity(user=None, action='', description='', request=None, additional_data=None):
    """Kullanıcı aktivitesini kaydet"""
    activity_data = {
        'user': user,
        'action': action,
        'description': description,
        'additional_data': additional_data or {}
    }
    
    if request:
        activity_data.update({
            'session_key': request.session.session_key,
            'ip_address': get_client_ip(request),
            'user_agent': get_user_agent(request)
        })
    
    return UserActivityLog.objects.create(**activity_data)


def log_text_generation(user, session_key, input_text, generated_text, request=None):
    """Metin üretimi aktivitesini kaydet"""
    log_user_activity(
        user=user,
        action='generate_text',
        description=f'Generated text for input: "{input_text[:50]}..."',
        request=request,
        additional_data={
            'input_length': len(input_text),
            'output_length': len(generated_text),
            'input_preview': input_text[:100],
            'output_preview': generated_text[:100]
        }
    )


def get_user_statistics(user):
    """Kullanıcı istatistiklerini döndür"""
    login_logs = UserLoginLog.objects.filter(user=user, login_successful=True)
    activity_logs = UserActivityLog.objects.filter(user=user)
    
    stats = {
        'total_logins': login_logs.count(),
        'total_activities': activity_logs.count(),
        'text_generations': activity_logs.filter(action='generate_text').count(),
        'last_login': login_logs.first().login_time if login_logs.exists() else None,
        'most_common_actions': {}
    }
    
    # En çok yapılan aktiviteleri hesapla
    action_counts = activity_logs.values('action').annotate(
        count=models.Count('action')
    ).order_by('-count')[:5]
    
    for action in action_counts:
        stats['most_common_actions'][action['action']] = action['count']
    
    return stats


def clean_old_logs(days=30):
    """Eski log kayıtlarını temizle (varsayılan 30 gün)"""
    from django.utils import timezone
    import datetime
    
    cutoff_date = timezone.now() - datetime.timedelta(days=days)
    
    # Eski login loglarını temizle
    old_logins = UserLoginLog.objects.filter(login_time__lt=cutoff_date)
    login_count = old_logins.count()
    old_logins.delete()
    
    # Eski activity loglarını temizle
    old_activities = UserActivityLog.objects.filter(timestamp__lt=cutoff_date)
    activity_count = old_activities.count()
    old_activities.delete()
    
    return {
        'deleted_logins': login_count,
        'deleted_activities': activity_count
    }
