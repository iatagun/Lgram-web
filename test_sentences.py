#!/usr/bin/env python3
"""
Test script to debug sentence count issues
"""
import os
import sys
import django

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgramweb.settings')
django.setup()

from lgram.models.simple_language_model import create_language_model

def test_sentence_generation():
    """Test if sentence count parameter works correctly"""
    print("Testing sentence generation...")
    
    # Create model
    model = create_language_model()
    
    # Test input
    input_words = ["The", "student", "walked"]
    
    # Test different sentence counts
    for num_sentences in [1, 3, 5, 6, 8]:
        print(f"\n--- Testing {num_sentences} sentences ---")
        
        try:
            # Test standard generation
            result_standard = model.generate_text(
                num_sentences=num_sentences,
                input_words=input_words,
                length=15,
                use_progress_bar=False
            )
            
            # Count actual sentences
            actual_sentences = len([s.strip() for s in result_standard.split('.') if s.strip()])
            
            print(f"Standard Generation:")
            print(f"  Requested: {num_sentences} sentences")
            print(f"  Actual: {actual_sentences} sentences")
            print(f"  Text: {result_standard[:100]}...")
            
        except Exception as e:
            print(f"Standard generation failed: {e}")
        
        try:
            # Test centering generation
            result_centering = model.generate_text_with_centering(
                num_sentences=num_sentences,
                input_words=input_words,
                length=15,
                use_progress_bar=False
            )
            
            # Count actual sentences
            actual_sentences_c = len([s.strip() for s in result_centering.split('.') if s.strip()])
            
            print(f"Centering Generation:")
            print(f"  Requested: {num_sentences} sentences")
            print(f"  Actual: {actual_sentences_c} sentences")
            print(f"  Text: {result_centering[:100]}...")
            
        except Exception as e:
            print(f"Centering generation failed: {e}")

if __name__ == "__main__":
    test_sentence_generation()