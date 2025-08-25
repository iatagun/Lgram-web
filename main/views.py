from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from datetime import timedelta
import json

from lgram.models.chunk import create_language_model
from .models import GeneratedText, UserActivityLog, UserLoginLog
from .utils import (
    log_user_login, log_user_logout, log_user_activity, 
    log_text_generation, get_client_ip
)
from .session_manager import SessionManager

@csrf_exempt
def index(request):
	result = None
	
	# Use SessionManager to get consistent session key
	session_key = SessionManager.get_session_key(request)
	
	# Get user's generation settings from session
	settings = SessionManager.get_generation_settings(request)
	num_sentences = settings.get('num_sentences', 5)
	length = settings.get('length', 13)

	if request.method == 'POST':
		# Handle clear history request
		if 'clear_history' in request.POST:
			deleted_count = GeneratedText.objects.filter(session_key=session_key).count()
			GeneratedText.objects.filter(session_key=session_key).delete()
			
			# Log activity
			log_user_activity(
				user=request.user if request.user.is_authenticated else None,
				action='view_history',
				description=f'Cleared {deleted_count} history items',
				request=request,
				additional_data={'deleted_items': deleted_count}
			)
			
			messages.success(request, 'History cleared successfully!')
			return redirect('index')
		
		# Handle text generation request
		text = request.POST.get('input_text', '')
		if not text.strip():
			messages.error(request, 'Please enter some text to generate.')
			return redirect('index')
			
		# Get user settings if provided
		try:
			num_sentences = int(request.POST.get('num_sentences', num_sentences))
		except Exception:
			pass  # Keep default from session
		try:
			length = int(request.POST.get('length', length))
		except Exception:
			pass  # Keep default from session
		
		# Save settings to session for next time
		SessionManager.store_generation_settings(request, {
			'num_sentences': num_sentences,
			'length': length
		})
		input_words = text.strip().rstrip('.').split()
		try:
			model = create_language_model()
			generated_text = model.generate_text(
				num_sentences=num_sentences,
				input_words=input_words,
				length=length,
				use_progress_bar=True
			)
			corrected_text = model.correct_grammar_t5(generated_text)
			result = corrected_text
			# Save to DB
			generated_text_obj = GeneratedText.objects.create(
				user=request.user if request.user.is_authenticated else None,
				session_key=session_key,
				input_text=text,
				generated_text=corrected_text,
				ip_address=get_client_ip(request)
			)
			
			# Log activity
			log_text_generation(
				user=request.user if request.user.is_authenticated else None,
				session_key=session_key,
				input_text=text,
				generated_text=corrected_text,
				request=request
			)
			
			messages.success(request, 'Text generated successfully!')
		except Exception as e:
			result = f'Error: {e}'
			messages.error(request, f'Generation failed: {str(e)}')

	# Get user's history (last 10)
	history = GeneratedText.objects.filter(session_key=session_key).order_by('-created_at')[:10]
	
	# Log history view if there's any history to show
	if history and request.method == 'GET':
		log_user_activity(
			user=request.user if request.user.is_authenticated else None,
			action='view_history',
			description=f'Viewed history with {len(history)} items',
			request=request,
			additional_data={'history_count': len(history)}
		)
	return render(request, 'main/index.html', {
		'result': result,
		'history': history,
		'num_sentences': num_sentences,
		'length': length,
	})

@csrf_exempt
def transition_analysis(request):
	"""Handle transition analysis requests"""
	analysis_results = None
	
	# Log page visit
	log_user_activity(
		user=request.user if request.user.is_authenticated else None,
		action='view_transition_analysis',
		description='Visited Transition Analysis page',
		request=request
	)
	
	if request.method == 'POST':
		text = request.POST.get('text', '')
		sentence_window = int(request.POST.get('sentence_window', 3))
		coherence_threshold = float(request.POST.get('coherence_threshold', 0.5))
		
		if text.strip():
			try:
				# Placeholder for centering theory analysis
				# This would integrate with lgram's centering theory implementation
				analysis_results = {
					'continue_count': 12,
					'retain_count': 8,
					'shift_count': 5,
					'rough_shift_count': 2,
					'coherence_score': 0.78,
					'transitions': [
						{'type': 'CONTINUE', 'center': 'the student', 'backward_center': 'the student'},
						{'type': 'RETAIN', 'center': 'the professor', 'backward_center': 'the student'},
						{'type': 'SHIFT', 'center': 'the assignment', 'backward_center': 'the professor'},
					]
				}
				
				# Log analysis activity
				log_user_activity(
					user=request.user if request.user.is_authenticated else None,
					action='view_transition_analysis',
					description=f'Performed transition analysis on {len(text)} characters',
					request=request,
					additional_data={
						'text_length': len(text),
						'sentence_window': sentence_window,
						'coherence_threshold': coherence_threshold
					}
				)
				
			except Exception as e:
				analysis_results = {'error': str(e)}
	
	return render(request, 'main/transition_analysis.html', {
		'analysis_results': analysis_results
	})

@csrf_exempt
def coherence_report(request):
	"""Handle coherence report requests"""
	coherence_report = None
	
	# Log page visit
	log_user_activity(
		user=request.user if request.user.is_authenticated else None,
		action='view_coherence_report',
		description='Visited Coherence Report page',
		request=request
	)
	
	if request.method == 'POST':
		text = request.POST.get('text', '')
		analysis_depth = request.POST.get('analysis_depth', 'standard')
		entity_weight = float(request.POST.get('entity_weight', 0.7))
		transition_weight = float(request.POST.get('transition_weight', 0.3))
		
		if text.strip():
			try:
				# Placeholder for coherence analysis
				# This would integrate with lgram's coherence analysis
				coherence_report = {
					'overall_score': 0.82,
					'entity_coherence': 0.85,
					'transition_coherence': 0.79,
					'sentence_count': len(text.split('.')),
					'lexical_cohesion': 78.5,
					'semantic_coherence': 82.3,
					'referential_coherence': 76.8,
					'key_entities': [
						{'text': 'student', 'frequency': 8},
						{'text': 'professor', 'frequency': 5},
						{'text': 'assignment', 'frequency': 4},
					],
					'strengths': [
						'Strong entity continuity throughout the text',
						'Good use of referential expressions',
						'Clear topic progression'
					],
					'improvements': [
						'Some abrupt topic transitions',
						'Could benefit from more connecting phrases'
					],
					'recommendations': [
						'Add transitional sentences between paragraphs',
						'Use more varied referential expressions',
						'Consider reorganizing some content for better flow'
					]
				}
				
				# Log analysis activity
				log_user_activity(
					user=request.user if request.user.is_authenticated else None,
					action='view_coherence_report',
					description=f'Generated coherence report for {len(text)} characters',
					request=request,
					additional_data={
						'text_length': len(text),
						'analysis_depth': analysis_depth,
						'entity_weight': entity_weight,
						'transition_weight': transition_weight
					}
				)
				
			except Exception as e:
				coherence_report = {'error': str(e)}
	
	return render(request, 'main/coherence_report.html', {
		'coherence_report': coherence_report
	})

def login_view(request):
	"""Handle user login"""
	if request.user.is_authenticated:
		return redirect('/')
	
	if request.method == 'POST':
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				auth_login(request, user)
				
				# Log successful login
				log_user_login(user, request, successful=True)
				
				messages.success(request, f'Welcome back, {username}!')
				next_url = request.GET.get('next', '/')
				return redirect(next_url)
			else:
				# Log failed login attempt
				try:
					failed_user = User.objects.get(username=username)
					log_user_login(failed_user, request, successful=False)
				except User.DoesNotExist:
					pass
				messages.error(request, 'Invalid username or password.')
		else:
			messages.error(request, 'Invalid username or password.')
	else:
		form = AuthenticationForm()
	
	return render(request, 'main/login.html', {'form': form})

def register_view(request):
	"""Handle user registration"""
	if request.user.is_authenticated:
		return redirect('/')
	
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			# Create user with email
			username = form.cleaned_data.get('username')
			email = request.POST.get('email', '')
			password = form.cleaned_data.get('password1')
			
			user = User.objects.create_user(
				username=username,
				email=email,
				password=password
			)
			
			# Log registration
			log_user_activity(
				user=user,
				action='register',
				description=f'New user registered: {username}',
				request=request,
				additional_data={'email': email}
			)
			
			messages.success(request, f'Account created successfully for {username}!')
			auth_login(request, user)
			
			# Log automatic login after registration
			log_user_login(user, request, successful=True)
			
			return redirect('/')
		else:
			messages.error(request, 'Please correct the errors below.')
	else:
		form = UserCreationForm()
	
	return render(request, 'main/register.html', {'form': form})

def logout_view(request):
	"""Handle user logout"""
	user = request.user
	username = user.username if user.is_authenticated else None
	
	if user.is_authenticated:
		# Log logout
		log_user_logout(user, request)
	
	auth_logout(request)
	if username:
		messages.info(request, f'You have been logged out successfully.')
	return redirect('index')

def session_info_view(request):
	"""Display session information for debugging/educational purposes"""
	session_info = SessionManager.get_session_info(request)
	generation_settings = SessionManager.get_generation_settings(request)
	recent_activities = SessionManager.get_recent_activities(request)
	
	# Convert timestamp strings back to datetime objects for template
	for activity in recent_activities:
		from django.utils.dateparse import parse_datetime
		activity['timestamp'] = parse_datetime(activity['timestamp'])
	
	return render(request, 'main/session_info.html', {
		'session_info': session_info,
		'generation_settings': generation_settings,
		'recent_activities': recent_activities[-10:],  # Last 10 activities
	})

@login_required
def profile_view(request):
	"""Display user profile information"""
	# Get user statistics
	total_generations = GeneratedText.objects.filter(user=request.user).count()
	total_activities = UserActivityLog.objects.filter(user=request.user).count()
	login_count = UserLoginLog.objects.filter(user=request.user, login_successful=True).count()
	days_member = (timezone.now() - request.user.date_joined).days
	
	stats = {
		'total_generations': total_generations,
		'total_activities': total_activities,
		'login_count': login_count,
		'days_member': days_member,
	}
	
	# Get recent activities
	recent_activities = UserActivityLog.objects.filter(
		user=request.user
	).order_by('-timestamp')[:10]
	
	return render(request, 'main/profile.html', {
		'stats': stats,
		'recent_activities': recent_activities,
	})

@login_required
def settings_view(request):
	"""Handle user settings and preferences"""
	if request.method == 'POST':
		form_type = request.POST.get('form_type')
		
		if form_type == 'profile':
			# Update profile information
			request.user.first_name = request.POST.get('first_name', '')
			request.user.last_name = request.POST.get('last_name', '')
			request.user.email = request.POST.get('email', '')
			request.user.save()
			
			log_user_activity(
				user=request.user,
				action='update_profile',
				description='Updated profile information',
				request=request
			)
			
			messages.success(request, 'Profile updated successfully!')
			
		elif form_type == 'generation':
			# Update generation preferences
			settings = {
				'num_sentences': int(request.POST.get('default_sentences', 5)),
				'length': int(request.POST.get('default_length', 13)),
			}
			SessionManager.store_generation_settings(request, settings)
			
			# Store other preferences
			SessionManager.store_user_preference(request, 'save_history', 'save_history' in request.POST)
			SessionManager.store_user_preference(request, 'show_tips', 'show_tips' in request.POST)
			
			log_user_activity(
				user=request.user,
				action='update_preferences',
				description='Updated generation preferences',
				request=request
			)
			
			messages.success(request, 'Preferences saved successfully!')
			
		elif form_type == 'password':
			# Change password
			current_password = request.POST.get('current_password')
			new_password1 = request.POST.get('new_password1')
			new_password2 = request.POST.get('new_password2')
			
			if not request.user.check_password(current_password):
				messages.error(request, 'Current password is incorrect.')
			elif new_password1 != new_password2:
				messages.error(request, 'New passwords do not match.')
			elif len(new_password1) < 8:
				messages.error(request, 'New password must be at least 8 characters long.')
			else:
				request.user.set_password(new_password1)
				request.user.save()
				update_session_auth_hash(request, request.user)  # Keep user logged in
				
				log_user_activity(
					user=request.user,
					action='change_password',
					description='Changed account password',
					request=request
				)
				
				messages.success(request, 'Password changed successfully!')
				
		elif form_type == 'clear_history':
			# Clear all user history
			deleted_count = GeneratedText.objects.filter(user=request.user).count()
			GeneratedText.objects.filter(user=request.user).delete()
			
			log_user_activity(
				user=request.user,
				action='clear_history',
				description=f'Cleared all history ({deleted_count} items)',
				request=request
			)
			
			messages.warning(request, f'Successfully deleted {deleted_count} generation records.')
		
		return redirect('settings')
	
	# GET request - display settings form
	generation_settings = SessionManager.get_generation_settings(request)
	user_preferences = {
		'save_history': SessionManager.get_user_preference(request, 'save_history', True),
		'show_tips': SessionManager.get_user_preference(request, 'show_tips', True),
	}
	
	return render(request, 'main/settings.html', {
		'generation_settings': generation_settings,
		'user_preferences': user_preferences,
	})

@login_required
def export_data_view(request):
	"""Export user data as JSON"""
	# Collect user data
	user_data = {
		'user_info': {
			'username': request.user.username,
			'email': request.user.email,
			'first_name': request.user.first_name,
			'last_name': request.user.last_name,
			'date_joined': request.user.date_joined.isoformat(),
			'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
		},
		'generated_texts': list(
			GeneratedText.objects.filter(user=request.user).values(
				'input_text', 'generated_text', 'created_at'
			)
		),
		'activities': list(
			UserActivityLog.objects.filter(user=request.user).values(
				'action', 'description', 'timestamp', 'ip_address'
			)
		),
		'login_history': list(
			UserLoginLog.objects.filter(user=request.user).values(
				'login_time', 'logout_time', 'ip_address', 'login_successful'
			)
		),
		'export_date': timezone.now().isoformat(),
	}
	
	# Convert datetime objects to strings
	for item in user_data['generated_texts']:
		if item['created_at']:
			item['created_at'] = item['created_at'].isoformat()
	
	for item in user_data['activities']:
		if item['timestamp']:
			item['timestamp'] = item['timestamp'].isoformat()
	
	for item in user_data['login_history']:
		if item['login_time']:
			item['login_time'] = item['login_time'].isoformat()
		if item['logout_time']:
			item['logout_time'] = item['logout_time'].isoformat()
	
	# Log export activity
	log_user_activity(
		user=request.user,
		action='export_data',
		description='Exported personal data',
		request=request
	)
	
	# Return JSON response
	response = HttpResponse(
		json.dumps(user_data, indent=2, ensure_ascii=False),
		content_type='application/json'
	)
	response['Content-Disposition'] = f'attachment; filename="{request.user.username}_data_export.json"'
	
	return response

# Demo user creation function removed - no longer needed for production
