# Ana sınıfı doğrudan import ederek kullanabilirsin
# from lgram.models.chunk import create_language_model
from lgram.models.chunk import create_language_model
# Modeli oluştur (gerekli parametreleri ayarlayabilirsin)
model = create_language_model()
input_sentence = "This was precisely what had formed the subject of my reflections."
input_words = input_sentence.strip().rstrip('.').split()

generated_text = model.generate_text_with_centering(
    num_sentences=5,
    input_words=input_words,
    length=13,
    use_progress_bar=True
)

# Apply T5 correction
corrected_text = model.correct_grammar_t5(generated_text)
print("\nCorrected Text:")
print(corrected_text)
