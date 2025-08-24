from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from main.utils import clean_old_logs, get_user_statistics
from main.models import UserLoginLog, UserActivityLog, GeneratedText
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Log management utilities for user activities and login records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean-logs',
            type=int,
            metavar='DAYS',
            help='Delete log records older than specified days',
        )
        parser.add_argument(
            '--user-stats',
            type=str,
            metavar='USERNAME',
            help='Show statistics for a specific user',
        )
        parser.add_argument(
            '--summary',
            action='store_true',
            help='Show overall system statistics',
        )
        parser.add_argument(
            '--export-user-data',
            type=str,
            metavar='USERNAME',
            help='Export all data for a specific user',
        )

    def handle(self, *args, **options):
        if options['clean_logs']:
            self.clean_old_logs(options['clean_logs'])
        elif options['user_stats']:
            self.show_user_stats(options['user_stats'])
        elif options['summary']:
            self.show_summary()
        elif options['export_user_data']:
            self.export_user_data(options['export_user_data'])
        else:
            self.stdout.write(
                self.style.WARNING('No action specified. Use --help to see available options.')
            )

    def clean_old_logs(self, days):
        """Clean old log records"""
        self.stdout.write(f'Cleaning logs older than {days} days...')
        
        result = clean_old_logs(days)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Cleaned {result["deleted_logins"]} login logs and '
                f'{result["deleted_activities"]} activity logs'
            )
        )

    def show_user_stats(self, username):
        """Show statistics for a specific user"""
        try:
            user = User.objects.get(username=username)
            stats = get_user_statistics(user)
            
            self.stdout.write(f'\n=== Statistics for {username} ===')
            self.stdout.write(f'Total Logins: {stats["total_logins"]}')
            self.stdout.write(f'Total Activities: {stats["total_activities"]}')
            self.stdout.write(f'Text Generations: {stats["text_generations"]}')
            self.stdout.write(f'Last Login: {stats["last_login"]}')
            
            self.stdout.write('\nMost Common Actions:')
            for action, count in stats['most_common_actions'].items():
                self.stdout.write(f'  {action}: {count}')
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" not found')
            )

    def show_summary(self):
        """Show overall system statistics"""
        total_users = User.objects.count()
        total_logins = UserLoginLog.objects.filter(login_successful=True).count()
        total_activities = UserActivityLog.objects.count()
        total_texts = GeneratedText.objects.count()
        
        # Recent activity (last 24 hours)
        from datetime import timedelta
        yesterday = timezone.now() - timedelta(days=1)
        recent_logins = UserLoginLog.objects.filter(
            login_time__gte=yesterday,
            login_successful=True
        ).count()
        recent_activities = UserActivityLog.objects.filter(
            timestamp__gte=yesterday
        ).count()
        
        # Most active users (by total activities)
        active_users = UserActivityLog.objects.values('user__username').annotate(
            activity_count=models.Count('id')
        ).order_by('-activity_count')[:5]
        
        self.stdout.write('\n=== System Summary ===')
        self.stdout.write(f'Total Users: {total_users}')
        self.stdout.write(f'Total Successful Logins: {total_logins}')
        self.stdout.write(f'Total Activities: {total_activities}')
        self.stdout.write(f'Total Generated Texts: {total_texts}')
        
        self.stdout.write(f'\n=== Recent Activity (24 hours) ===')
        self.stdout.write(f'Recent Logins: {recent_logins}')
        self.stdout.write(f'Recent Activities: {recent_activities}')
        
        self.stdout.write(f'\n=== Most Active Users ===')
        for user_data in active_users:
            username = user_data['user__username'] or 'Anonymous'
            count = user_data['activity_count']
            self.stdout.write(f'  {username}: {count} activities')

    def export_user_data(self, username):
        """Export all data for a specific user"""
        try:
            user = User.objects.get(username=username)
            
            # Get all user data
            login_logs = UserLoginLog.objects.filter(user=user)
            activity_logs = UserActivityLog.objects.filter(user=user)
            generated_texts = GeneratedText.objects.filter(user=user)
            
            self.stdout.write(f'\n=== Data Export for {username} ===')
            
            self.stdout.write(f'\n--- Login History ({login_logs.count()} records) ---')
            for log in login_logs.order_by('-login_time')[:10]:  # Last 10
                status = "Success" if log.login_successful else "Failed"
                duration = ""
                if log.logout_time and log.login_time:
                    delta = log.logout_time - log.login_time
                    hours, remainder = divmod(delta.total_seconds(), 3600)
                    minutes, _ = divmod(remainder, 60)
                    duration = f" (Duration: {int(hours)}h {int(minutes)}m)"
                    
                self.stdout.write(
                    f'  {log.login_time.strftime("%Y-%m-%d %H:%M:%S")} - {status}{duration}'
                )
            
            self.stdout.write(f'\n--- Activity History ({activity_logs.count()} records) ---')
            for log in activity_logs.order_by('-timestamp')[:10]:  # Last 10
                self.stdout.write(
                    f'  {log.timestamp.strftime("%Y-%m-%d %H:%M:%S")} - '
                    f'{log.get_action_display()}: {log.description}'
                )
            
            self.stdout.write(f'\n--- Generated Texts ({generated_texts.count()} records) ---')
            for text in generated_texts.order_by('-created_at')[:5]:  # Last 5
                self.stdout.write(
                    f'  {text.created_at.strftime("%Y-%m-%d %H:%M:%S")} - '
                    f'Input: {text.input_text[:50]}...'
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" not found')
            )
