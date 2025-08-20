from django.db import models


class GeneratedText(models.Model):
	session_key = models.CharField(max_length=40, db_index=True)
	input_text = models.TextField()
	generated_text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.input_text[:30]}... -> {self.generated_text[:30]}..."
