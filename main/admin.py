from django.contrib import admin
from .models import GeneratedText, UserLoginLog, UserActivityLog


@admin.register(GeneratedText)
class GeneratedTextAdmin(admin.ModelAdmin):
    list_display = ("user", "session_key", "input_text_preview", "generated_text_preview", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("input_text", "generated_text", "session_key", "user__username")
    readonly_fields = ("created_at",)
    
    def input_text_preview(self, obj):
        return obj.input_text[:50] + "..." if len(obj.input_text) > 50 else obj.input_text
    input_text_preview.short_description = "Input Text"
    
    def generated_text_preview(self, obj):
        return obj.generated_text[:50] + "..." if len(obj.generated_text) > 50 else obj.generated_text
    generated_text_preview.short_description = "Generated Text"


@admin.register(UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    list_display = ("user", "login_time", "logout_time", "ip_address", "login_successful", "session_duration")
    list_filter = ("login_successful", "login_time", "logout_time")
    search_fields = ("user__username", "ip_address", "session_key")
    readonly_fields = ("login_time", "session_key")
    ordering = ("-login_time",)
    
    def session_duration(self, obj):
        if obj.logout_time and obj.login_time:
            duration = obj.logout_time - obj.login_time
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        return "Active" if obj.login_successful else "N/A"
    session_duration.short_description = "Session Duration"


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "description_preview", "timestamp", "ip_address")
    list_filter = ("action", "timestamp", "user")
    search_fields = ("user__username", "description", "ip_address", "session_key")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)
    
    def description_preview(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    description_preview.short_description = "Description"
