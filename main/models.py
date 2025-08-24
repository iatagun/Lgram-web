from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserLoginLog(models.Model):
    """Kullanıcı giriş kayıtlarını tutar"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_logs')
    login_time = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    login_successful = models.BooleanField(default=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-login_time']
        verbose_name = 'User Login Log'
        verbose_name_plural = 'User Login Logs'
    
    def __str__(self):
        status = "Successful" if self.login_successful else "Failed"
        return f"{self.user.username} - {status} - {self.login_time.strftime('%Y-%m-%d %H:%M:%S')}"


class UserActivityLog(models.Model):
    """Kullanıcı hareketlerini kaydeder"""
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('generate_text', 'Generate Text'),
        ('view_history', 'View History'),
        ('view_transition_analysis', 'View Transition Analysis'),
        ('view_coherence_report', 'View Coherence Report'),
        ('register', 'Register'),
        ('profile_update', 'Profile Update'),
        ('password_change', 'Password Change'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs', null=True, blank=True)
    session_key = models.CharField(max_length=40, db_index=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    additional_data = models.JSONField(default=dict, blank=True)  # Ekstra veri için
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'User Activity Log'
        verbose_name_plural = 'User Activity Logs'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['session_key', '-timestamp']),
        ]
    
    def __str__(self):
        user_info = self.user.username if self.user else f"Session: {self.session_key[:8]}..."
        return f"{user_info} - {self.get_action_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class GeneratedText(models.Model):
    """Üretilen metin kayıtları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_texts', null=True, blank=True)
    session_key = models.CharField(max_length=40, db_index=True)
    input_text = models.TextField()
    generated_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Generated Text'
        verbose_name_plural = 'Generated Texts'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['session_key', '-created_at']),
        ]

    def __str__(self):
        user_info = self.user.username if self.user else f"Session: {self.session_key[:8]}..."
        return f"{user_info} - {self.input_text[:30]}... -> {self.generated_text[:30]}..."
