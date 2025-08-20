from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from lgram.models.chunk import create_language_model
from .models import GeneratedText

@csrf_exempt
def index(request):
	result = None
	if not request.session.session_key:
		request.session.save()
	session_key = request.session.session_key

	if request.method == 'POST':
		text = request.POST.get('input_text', '')
		input_words = text.strip().rstrip('.').split()
		try:
			model = create_language_model()
			generated_text = model.generate_text(
				num_sentences=5,
				input_words=input_words,
				length=13,
				use_progress_bar=True
			)
			corrected_text = model.correct_grammar_t5(generated_text)
			result = corrected_text
			# Save to DB
			GeneratedText.objects.create(
				session_key=session_key,
				input_text=text,
				generated_text=corrected_text
			)
		except Exception as e:
			result = f'Error: {e}'

	# Get user's history (last 10)
	history = GeneratedText.objects.filter(session_key=session_key).order_by('-created_at')[:10]
	return render(request, 'main/index.html', {'result': result, 'history': history})
