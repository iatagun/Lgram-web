"""
Management command to clean up expired sessions and old data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.session_manager import SessionManager
from main.models import GeneratedText, UserActivityLog


class Command(BaseCommand):
    help = 'Clean up expired sessions and old data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete data older than N days (default: 30)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"{'[DRY RUN] ' if dry_run else ''}Cleaning up data older than {days} days..."
            )
        )
        
        # Clean up expired sessions
        expired_sessions_count = SessionManager.cleanup_expired_sessions()
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {expired_sessions_count} expired sessions"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Would delete {expired_sessions_count} expired sessions"
                )
            )
        
        # Clean up old generated texts (for anonymous users only)
        old_generated_texts = GeneratedText.objects.filter(
            created_at__lt=cutoff_date,
            user__isnull=True  # Only delete anonymous user data
        )
        old_texts_count = old_generated_texts.count()
        
        if not dry_run:
            old_generated_texts.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {old_texts_count} old anonymous generated texts"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Would delete {old_texts_count} old anonymous generated texts"
                )
            )
        
        # Clean up old activity logs (keep user logs, clean anonymous)
        old_activity_logs = UserActivityLog.objects.filter(
            timestamp__lt=cutoff_date,
            user__isnull=True
        )
        old_logs_count = old_activity_logs.count()
        
        if not dry_run:
            old_activity_logs.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {old_logs_count} old anonymous activity logs"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Would delete {old_logs_count} old anonymous activity logs"
                )
            )
        
        # Show statistics
        active_sessions = SessionManager.get_active_sessions_count()
        self.stdout.write(
            self.style.SUCCESS(
                f"\nCurrent statistics:"
                f"\n- Active sessions: {active_sessions}"
                f"\n- Total generated texts: {GeneratedText.objects.count()}"
                f"\n- Total activity logs: {UserActivityLog.objects.count()}"
            )
        )
