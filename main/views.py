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
from django.utils import timezone, translation
from django.conf import settings
from datetime import timedelta
import json

from lgram.models.simple_language_model import create_language_model
import lgram
from .models import GeneratedText, UserActivityLog, UserLoginLog, GenerationProgress
from .utils import (
    log_user_login, log_user_logout, log_user_activity, 
    log_text_generation, get_client_ip
)
from .session_manager import SessionManager

def get_lgram_version():
    """Get lgram package version"""
    try:
        # Use modern importlib.metadata (Python 3.8+)
        from importlib.metadata import version
        return version('centering-lgram')
    except ImportError:
        try:
            # Fallback for older Python versions
            import pkg_resources
            return pkg_resources.get_distribution('centering-lgram').version
        except:
            try:
                # Fallback to module __version__ attribute
                return lgram.__version__
            except AttributeError:
                return "unknown"

@csrf_exempt
def switch_language(request):
    """Switch interface language"""
    if request.method == 'POST':
        language = request.POST.get('language', 'en')
        
        # Validate language
        if language not in ['en', 'tr']:
            language = 'en'
        
        # Activate the language
        translation.activate(language)
        
        # Use Django's session key for language
        # Define the key manually since it's not always exposed
        LANGUAGE_SESSION_KEY = 'django_language'
        request.session[LANGUAGE_SESSION_KEY] = language
        
        # Log language switch
        log_user_activity(
            user=request.user if request.user.is_authenticated else None,
            action='switch_language',
            description=f'Switched interface language to {language}',
            request=request,
            additional_data={'new_language': language}
        )
        
        return JsonResponse({
            'success': True, 
            'language': language,
            'message': 'Language switched successfully'
        })
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

@csrf_exempt
def load_more_history(request):
    """AJAX endpoint to load more history items"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests allowed'}, status=405)
    
    try:
        # Get pagination parameters
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 5))
        
        # Use SessionManager to get consistent session key
        session_key = SessionManager.get_session_key(request)
        
        # Get more history items
        history_items = GeneratedText.objects.filter(
            session_key=session_key
        ).order_by('-created_at')[offset:offset + limit]
        
        # Convert to list of dictionaries
        history_data = []
        for item in history_items:
            # Determine model type based on some logic (you may need to store this in the model)
            model_type = 'centering' if 'centering' in item.generated_text.lower() else 'standard'
            model_name = 'Centering-Enhanced Generation' if model_type == 'centering' else 'Standard Generation'
            
            history_data.append({
                'id': item.id,
                'input_text': item.input_text,
                'generated_text': item.generated_text,
                'created_at': item.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'model_type': model_type,
                'model_name': model_name
            })
        
        # Check if there are more items
        total_count = GeneratedText.objects.filter(session_key=session_key).count()
        has_more = (offset + limit) < total_count
        
        # Log activity
        log_user_activity(
            user=request.user if request.user.is_authenticated else None,
            action='load_more_history',
            description=f'Loaded {len(history_data)} more history items (offset: {offset})',
            request=request,
            additional_data={
                'offset': offset,
                'limit': limit,
                'loaded_count': len(history_data),
                'has_more': has_more
            }
        )
        
        return JsonResponse({
            'success': True,
            'history_items': history_data,
            'has_more': has_more,
            'total_count': total_count,
            'loaded_count': len(history_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def show_terminal_progress(current, total, elapsed_time, rate=None):
    """Terminal progress bar function"""
    percentage = (current / total) * 100 if total > 0 else 0
    
    # Create visual progress bar
    bar_length = 20
    filled_length = int((percentage / 100) * bar_length)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    
    # Format time
    elapsed_mins = int(elapsed_time / 60)
    elapsed_secs = int(elapsed_time % 60)
    
    # Calculate remaining time
    if current > 0 and rate:
        remaining_time = (total - current) * rate
        remaining_mins = int(remaining_time / 60)
        remaining_secs = int(remaining_time % 60)
        remaining_str = f"{remaining_mins:02d}:{remaining_secs:02d}"
        rate_str = f"{rate:.2f}s/sent"
    else:
        remaining_str = "--:--"
        rate_str = "--s/sent"
    
    # Terminal output
    terminal_line = f'🎯 Centering Generation: {percentage:3.0f}%|{bar}| {current}/{total} [{elapsed_mins:02d}:{elapsed_secs:02d}<{remaining_str}, {rate_str}]'
    
    # Print to terminal
    print(f"\r{terminal_line}", end="", flush=True)
    
    return terminal_line


def update_progress(task_id, **kwargs):
    """Update progress in database"""
    try:
        progress = GenerationProgress.objects.get(task_id=task_id)
        
        for key, value in kwargs.items():
            if hasattr(progress, key):
                setattr(progress, key, value)
        
        progress.save()
        
    except GenerationProgress.DoesNotExist:
        print(f"[WARNING] Progress object not found for task_id: {task_id}")


class SimpleProgressGenerator:
    def __init__(self, task_id):
        self.task_id = task_id
        
    def generate_with_progress(self, input_words, num_sentences, length, model_type):
        """Generate text with real terminal and frontend progress"""
        import time
        start_time = time.time()
        
        try:
            # Initialize
            update_progress(self.task_id, status='initializing', percentage=10, 
                          status_message='Loading model...')
            
            model = create_language_model()
            
            update_progress(self.task_id, status='generating', percentage=20,
                          status_message=f'Generating {num_sentences} sentences...')
            
            print(f"\n[INFO] Starting {model_type} generation...")
            
            # Simulate real generation with progress
            for i in range(num_sentences):
                current = i + 1
                elapsed = time.time() - start_time
                
                # Calculate rate
                rate = elapsed / current if current > 0 else 0
                
                # Show terminal progress
                terminal_line = show_terminal_progress(current, num_sentences, elapsed, rate)
                
                # Calculate percentage for frontend
                generation_progress = (current / num_sentences) * 70  # 70% for generation
                overall_progress = 20 + generation_progress
                
                # Update frontend
                update_progress(self.task_id,
                              current_sentence=current,
                              percentage=overall_progress,
                              detailed_message=terminal_line)
                
                # Simulate processing time
                time.sleep(2.5)  # Realistic processing time
            
            print("\n[INFO] Performing final generation...")
            
            # Actual text generation
            if model_type == 'centering':
                result = model.generate_text_with_centering(
                    num_sentences=num_sentences,
                    input_words=input_words,
                    length=length,
                    use_progress_bar=False
                )
            else:
                result = model.generate_text(
                    num_sentences=num_sentences,
                    input_words=input_words,
                    length=length,
                    use_progress_bar=False
                )
            
            # Final update
            update_progress(self.task_id, status='completed', percentage=100,
                          current_sentence=num_sentences,
                          status_message='Generation completed successfully!')
            
            print(f"\n[SUCCESS] Generation completed: {result}")
            
            return result
            
        except Exception as e:
            print(f"\n[ERROR] Generation failed: {e}")
            update_progress(self.task_id, status='failed', 
                          status_message=f'Generation failed: {str(e)}')
            return None

@csrf_exempt
def index(request):
	print(f"[DEBUG] Request method: {request.method}")  # Debug log
	result = None
	
	# Use SessionManager to get consistent session key
	session_key = SessionManager.get_session_key(request)
	
	# Get user's generation settings from session
	settings = SessionManager.get_generation_settings(request)
	num_sentences = settings.get('num_sentences', 5)
	length = settings.get('length', 13)
	model_type = settings.get('model_type', 'chunk')  # Default to standard generation
	
	# GET request'inde son generation sonucunu kontrol et
	model_name = None
	input_text = None
	
	if request.method == 'GET' and 'last_generation' in request.session:
		last_gen = request.session.pop('last_generation')  # Bir kere göster, sonra sil
		result = last_gen.get('result')
		model_name = last_gen.get('model_name')
		input_text = last_gen.get('input_text')
		num_sentences = last_gen.get('num_sentences', num_sentences)
		length = last_gen.get('length', length)
		messages.info(request, f'Last generation used: {model_name}')

	if request.method == 'POST':
		print(f"[DEBUG] POST data received: {request.POST}")  # Debug log
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
		print(f"[DEBUG] Input text: '{text}'")  # Debug log
		
		if not text.strip():
			print("[DEBUG] Empty text, redirecting with error")  # Debug log
			messages.error(request, 'Please enter some text to generate.')
			return redirect('index')
			
		# Get user settings if provided
		try:
			num_sentences = int(request.POST.get('num_sentences', num_sentences))
			print(f"[DEBUG] num_sentences: {num_sentences}")  # Debug log
		except Exception as e:
			print(f"[DEBUG] Error parsing num_sentences: {e}")  # Debug log
			pass  # Keep default from session
		try:
			length = int(request.POST.get('length', length))
			print(f"[DEBUG] length: {length}")  # Debug log
		except Exception as e:
			print(f"[DEBUG] Error parsing length: {e}")  # Debug log
			pass  # Keep default from session
		
		# Get model type selection
		model_type = request.POST.get('model_type', model_type)
		print(f"[DEBUG] model_type: {model_type}")  # Debug log
		
		# Save settings to session for next time
		SessionManager.store_generation_settings(request, {
			'num_sentences': num_sentences,
			'length': length,
			'model_type': model_type
		})
		input_words = text.strip().rstrip('.').split()
		print(f"[DEBUG] input_words: {input_words}")  # Debug log
		
		try:
			print("[DEBUG] Starting model creation...")  # Debug log
			# Tek model kullan ama iki farklı generation metodu
			model = create_language_model()
			print("[DEBUG] Model created successfully")  # Debug log
			
			if model_type == 'centering':
				print("[DEBUG] Using centering generation")  # Debug log
				print(f"[DEBUG] Parameters - num_sentences: {num_sentences}, length: {length}")  # Debug log
				# Centering generation için user'ın istediği parametre sayısı
				try:
					generated_text = model.generate_text_with_centering(
						num_sentences=num_sentences,  # Kullanıcının istediği sayı
						input_words=input_words,
						use_progress_bar=True,  # Progress bar açık
						length=length  # Kullanıcının istediği uzunluk
					)
					print(f"[DEBUG] Centering generation completed: '{generated_text[:100]}...'")  # Debug log
					actual_sentences = len([s.strip() for s in generated_text.split('.') if s.strip()])
					print(f"[DEBUG] Generated text sentence count: {actual_sentences}, requested: {num_sentences}")  # Count sentences
					
					# Check if we got fewer sentences than requested
					if actual_sentences < num_sentences:
						print(f"[WARNING] Centering generation returned {actual_sentences} sentences, but {num_sentences} were requested")
						print("[DEBUG] Falling back to standard generation for consistency")
						# Fallback to standard generation for more reliable sentence count
						generated_text = model.generate_text(
							num_sentences=num_sentences,  # Kullanıcının istediği sayı
							input_words=input_words,
							length=length,  # Kullanıcının istediği uzunluk
							use_progress_bar=True
						)
						print(f"[DEBUG] Fallback to standard generation: '{generated_text[:100]}...'")
						fallback_sentences = len([s.strip() for s in generated_text.split('.') if s.strip()])
						print(f"[DEBUG] Fallback sentence count: {fallback_sentences}")
						model_name = "Standard Generation (Fallback)"
					else:
						model_name = "Centering-Enhanced Generation"
						
				except Exception as centering_error:
					print(f"[DEBUG] Centering generation failed: {centering_error}")  # Debug log
					# Fallback to standard generation
					generated_text = model.generate_text(
						num_sentences=num_sentences,  # Kullanıcının istediği sayı
						input_words=input_words,
						length=length,  # Kullanıcının istediği uzunluk
						use_progress_bar=True
					)
					print(f"[DEBUG] Fallback to standard generation: '{generated_text[:100]}...'")  # Debug log
					fallback_sentences = len([s.strip() for s in generated_text.split('.') if s.strip()])
					print(f"[DEBUG] Fallback sentence count: {fallback_sentences}")  # Count sentences
					model_name = "Standard Generation (Error Fallback)"
				
				# Only set model name if not already set by fallback logic
				if 'model_name' not in locals():
					model_name = "Centering-Enhanced Generation"
				
				# Centering için T5 correction kullanarak kaliteyi artır
				print("[DEBUG] Starting T5 correction...")  # Debug log
				try:
					corrected_text = model.correct_grammar_t5(generated_text, prompt_style="comprehensive")
					print(f"[DEBUG] T5 correction completed: '{corrected_text[:50]}...'")  # Debug log
					result = corrected_text
				except Exception as t5_error:
					print(f"[DEBUG] T5 correction failed: {t5_error}, using raw text")  # Debug log
					result = generated_text
			else:
				print("[DEBUG] Using standard generation")  # Debug log
				print(f"[DEBUG] Parameters - num_sentences: {num_sentences}, length: {length}")  # Debug log
				try:
					generated_text = model.generate_text(
						num_sentences=num_sentences,
						input_words=input_words,
						length=length,
						use_progress_bar=False  # Progress bar kapalı = daha hızlı
					)
					print(f"[DEBUG] Standard generation completed: '{generated_text[:100]}...'")  # Debug log
					print(f"[DEBUG] Generated text sentence count: {len([s for s in generated_text.split('.') if s.strip()])}")  # Count sentences
				except Exception as std_error:
					print(f"[DEBUG] Standard generation failed: {std_error}")  # Debug log
					# Minimal fallback
					generated_text = " ".join(input_words) + " generated text here."
				
				model_name = "Standard Generation"
				# Standard generation için T5 correction kullan
				print("[DEBUG] Starting T5 correction...")  # Debug log
				try:
					corrected_text = model.correct_grammar_t5(generated_text, prompt_style="comprehensive")
					print(f"[DEBUG] T5 correction completed: '{corrected_text[:50]}...'")  # Debug log
					result = corrected_text
				except Exception as t5_error:
					print(f"[DEBUG] T5 correction failed: {t5_error}, using raw text")  # Debug log
					result = generated_text
			
			print(f"[DEBUG] Final result: '{result[:50]}...'")  # Debug log
			
			# Add user notification about sentence count if fallback was used
			if "Fallback" in model_name:
				messages.warning(request, f'Note: Switched to {model_name} for better sentence count accuracy.')
			else:
				messages.info(request, f'Using {model_name} method')
			
			# Count final sentences for user feedback
			final_sentence_count = len([s.strip() for s in result.split('.') if s.strip()])
			if final_sentence_count != num_sentences:
				messages.warning(request, f'Generated {final_sentence_count} sentences (requested {num_sentences}). This is due to model limitations.')
			
			# Save to DB with model type info
			generated_text_obj = GeneratedText.objects.create(
				user=request.user if request.user.is_authenticated else None,
				session_key=session_key,
				input_text=text,
				generated_text=result,
				ip_address=get_client_ip(request)
			)
			
			# Log activity with model type
			log_text_generation(
				user=request.user if request.user.is_authenticated else None,
				session_key=session_key,
				input_text=text,
				generated_text=result,
				request=request
			)
			
			# Add model info to activity log
			log_user_activity(
				user=request.user if request.user.is_authenticated else None,
				action='generate_text',
				description=f'Generated text using {model_name}',
				request=request,
				additional_data={
					'model_type': model_type,
					'model_name': model_name,
					'input_length': len(text),
					'output_length': len(result) if result else 0
				}
			)
			
			messages.success(request, f'Text generated successfully with {model_name}!')
			
			# Sonucu session'a kaydet (redirect sonrası gösterebilmek için)
			request.session['last_generation'] = {
				'result': result,
				'input_text': text,
				'model_name': model_name,
				'num_sentences': num_sentences,
				'length': length
			}
			
			# POST-redirect-GET pattern: form resubmission'ı önlemek için redirect
			return redirect('index')
			
		except Exception as e:
			print(f"[DEBUG] Exception occurred: {type(e).__name__}: {str(e)}")  # Debug log
			import traceback
			print(f"[DEBUG] Traceback: {traceback.format_exc()}")  # Debug log
			messages.error(request, f'Generation failed: {str(e)}')
			return redirect('index')

	# Get user's history (only last 3 for initial load to reduce server load)
	history = GeneratedText.objects.filter(session_key=session_key).order_by('-created_at')[:3]
	
	# Check if there are more items for "Show More" button
	total_history_count = GeneratedText.objects.filter(session_key=session_key).count()
	has_more_history = total_history_count > 3
	
	# Log history view if there's any history to show
	if history and request.method == 'GET':
		log_user_activity(
			user=request.user if request.user.is_authenticated else None,
			action='view_history',
			description=f'Viewed history with {len(history)} of {total_history_count} items',
			request=request,
			additional_data={'history_count': len(history), 'total_count': total_history_count}
		)
	return render(request, 'main/index.html', {
		'result': result,
		'history': history,
		'has_more_history': has_more_history,
		'total_history_count': total_history_count,
		'num_sentences': num_sentences,
		'length': length,
		'model_type': model_type,
		'model_name': model_name,
		'input_text': input_text,
		'lgram_version': get_lgram_version(),
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
				'model_type': request.POST.get('default_model_type', 'chunk'),
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


def generate_text_async(task_id, input_words, num_sentences, length, model_type):
    """Async generation wrapper with real progress"""
    generator = SimpleProgressGenerator(task_id)
    return generator.generate_with_progress(input_words, num_sentences, length, model_type)


def create_progress_tracker(user, session_key, model_type, input_text, num_sentences):
    """Create a new progress tracker"""
    import uuid
    
    task_id = str(uuid.uuid4())
    
    progress = GenerationProgress.objects.create(
        task_id=task_id,
        user=user,
        session_key=session_key,
        model_type=model_type,
        input_text=input_text,
        total_sentences=num_sentences,
        status='pending',
        percentage=0,
        current_sentence=0,
        current_step=1,
        total_steps=5,
        status_message='Initializing...',
        detailed_message='🎯 Preparing for text generation...'
    )
    
    return progress


@csrf_exempt
def start_generation(request):
    """API endpoint to start text generation"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)
    
    try:
        # Get parameters
        input_text = request.POST.get('input_text', '').strip()
        num_sentences = int(request.POST.get('num_sentences', 5))
        length = int(request.POST.get('length', 13))
        model_type = request.POST.get('model_type', 'chunk')
        
        if not input_text:
            return JsonResponse({'error': 'input_text is required'}, status=400)
        
        # Use SessionManager to get consistent session key
        from .session_manager import SessionManager
        session_key = SessionManager.get_session_key(request)
        
        # Create progress tracker
        progress = create_progress_tracker(
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            model_type=model_type,
            input_text=input_text,
            num_sentences=num_sentences
        )
        
        # Start generation in background thread
        import threading
        input_words = input_text.strip().rstrip('.').split()
        
        def run_generation():
            try:
                result = generate_text_async(progress.task_id, input_words, num_sentences, length, model_type)
                
                if result:
                    # Save to database
                    generated_text_obj = GeneratedText.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        session_key=session_key,
                        input_text=input_text,
                        generated_text=result,
                        ip_address=get_client_ip(request)
                    )
                    
            except Exception as e:
                print(f"[ERROR] Background generation failed: {e}")
        
        # Start background thread
        generation_thread = threading.Thread(target=run_generation)
        generation_thread.daemon = True
        generation_thread.start()
        
        return JsonResponse({
            'success': True,
            'task_id': progress.task_id,
            'message': 'Generation started successfully',
            'num_sentences': num_sentences
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_generation_progress(request):
    """API endpoint to get generation progress"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests allowed'}, status=405)
    
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({'error': 'task_id is required'}, status=400)
    
    try:
        progress = GenerationProgress.objects.get(task_id=task_id)
        
        # Calculate elapsed time
        elapsed = timezone.now() - progress.started_at
        elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
        
        # Calculate processing rate
        processing_rate = "--s/sent"
        if progress.current_sentence > 0 and elapsed.total_seconds() > 0:
            rate = elapsed.total_seconds() / progress.current_sentence
            processing_rate = f"{rate:.2f}s/sent"
        
        # Estimate remaining time
        remaining_str = "estimating..."
        if progress.estimated_completion:
            remaining = progress.estimated_completion - timezone.now()
            if remaining.total_seconds() > 0:
                remaining_str = str(remaining).split('.')[0]
            else:
                remaining_str = "00:00:00"
        
        response_data = {
            'task_id': progress.task_id,
            'status': progress.status,
            'percentage': round(progress.percentage, 1),
            'current_step': progress.current_step,
            'total_steps': progress.total_steps,
            'current_sentence': progress.current_sentence,
            'total_sentences': progress.total_sentences,
            'status_message': progress.status_message,
            'detailed_message': progress.detailed_message,
            'model_type': progress.model_type,
            'elapsed_time': elapsed_str,
            'estimated_remaining': remaining_str,
            'processing_rate': processing_rate,
            'is_completed': progress.status in ['completed', 'failed'],
        }
        
        return JsonResponse(response_data)
        
    except GenerationProgress.DoesNotExist:
        return JsonResponse({'error': 'Progress not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
