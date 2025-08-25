"""
Session Management Utilities for Lgram Web
"""
import uuid
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from typing import Optional, Dict, Any


class SessionManager:
    """
    Enhanced session management for Lgram Web application
    """
    
    @staticmethod
    def get_session_key(request) -> str:
        """
        Get consistent session key for both authenticated and anonymous users
        """
        if request.user.is_authenticated:
            return f"user_{request.user.id}"
        else:
            # Ensure session exists for anonymous users
            if not request.session.session_key:
                request.session.create()
            return request.session.session_key
    
    @staticmethod
    def store_user_preference(request, key: str, value: Any) -> None:
        """
        Store user preference in session
        """
        request.session[f"pref_{key}"] = value
        request.session.modified = True
    
    @staticmethod
    def get_user_preference(request, key: str, default: Any = None) -> Any:
        """
        Get user preference from session
        """
        return request.session.get(f"pref_{key}", default)
    
    @staticmethod
    def store_generation_settings(request, settings: Dict[str, Any]) -> None:
        """
        Store text generation settings in session
        """
        request.session['generation_settings'] = settings
        request.session.modified = True
    
    @staticmethod
    def get_generation_settings(request) -> Dict[str, Any]:
        """
        Get text generation settings from session with defaults
        """
        return request.session.get('generation_settings', {
            'num_sentences': 5,
            'length': 13,
            'temperature': 0.7,  # For future use
            'top_k': 50,         # For future use
        })
    
    @staticmethod
    def track_activity(request, activity_type: str, metadata: Dict[str, Any] = None) -> None:
        """
        Track user activity in session
        """
        activities = request.session.get('recent_activities', [])
        
        activity = {
            'type': activity_type,
            'timestamp': timezone.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Keep only last 20 activities
        activities.append(activity)
        activities = activities[-20:]
        
        request.session['recent_activities'] = activities
        request.session.modified = True
    
    @staticmethod
    def get_recent_activities(request, activity_type: str = None) -> list:
        """
        Get recent activities from session
        """
        activities = request.session.get('recent_activities', [])
        
        if activity_type:
            activities = [a for a in activities if a['type'] == activity_type]
        
        return activities
    
    @staticmethod
    def cleanup_expired_sessions() -> int:
        """
        Clean up expired sessions (to be called by management command)
        """
        expired_sessions = Session.objects.filter(
            expire_date__lt=timezone.now()
        )
        count = expired_sessions.count()
        expired_sessions.delete()
        return count
    
    @staticmethod
    def get_active_sessions_count() -> int:
        """
        Get count of active sessions
        """
        return Session.objects.filter(
            expire_date__gte=timezone.now()
        ).count()
    
    @staticmethod
    def get_user_sessions(user: User) -> list:
        """
        Get all active sessions for a user
        """
        if not user.is_authenticated:
            return []
        
        # This is more complex - would need custom session backend
        # For now, return empty list
        return []
    
    @staticmethod
    def invalidate_user_sessions(user: User, except_current: str = None) -> int:
        """
        Invalidate all sessions for a user except current one
        """
        # Would require custom implementation to track user sessions
        # For now, just return 0
        return 0
    
    @staticmethod
    def set_session_timeout(request, minutes: int = 30) -> None:
        """
        Set custom session timeout
        """
        request.session.set_expiry(minutes * 60)
    
    @staticmethod
    def extend_session(request, additional_minutes: int = 30) -> None:
        """
        Extend current session
        """
        current_expiry = request.session.get_expiry_age()
        request.session.set_expiry(current_expiry + (additional_minutes * 60))
    
    @staticmethod
    def get_session_info(request) -> Dict[str, Any]:
        """
        Get comprehensive session information
        """
        return {
            'session_key': request.session.session_key,
            'is_authenticated': request.user.is_authenticated,
            'user_id': request.user.id if request.user.is_authenticated else None,
            'username': request.user.username if request.user.is_authenticated else None,
            'session_age': request.session.get_expiry_age(),
            'session_expires': request.session.get_expiry_date(),
            'recent_activities_count': len(request.session.get('recent_activities', [])),
            'stored_preferences': [
                key for key in request.session.keys() 
                if key.startswith('pref_')
            ]
        }


class SessionMiddleware:
    """
    Custom middleware to enhance session handling
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Pre-processing
        self._pre_process(request)
        
        response = self.get_response(request)
        
        # Post-processing
        self._post_process(request, response)
        
        return response
    
    def _pre_process(self, request):
        """
        Pre-process request to set up session
        """
        # Ensure session exists for all requests
        if not request.session.session_key and not request.user.is_authenticated:
            request.session.create()
        
        # Track page views
        SessionManager.track_activity(request, 'page_view', {
            'path': request.path,
            'method': request.method
        })
    
    def _post_process(self, request, response):
        """
        Post-process response
        """
        # Update last activity timestamp
        request.session['last_activity'] = timezone.now().isoformat()
        request.session.modified = True
