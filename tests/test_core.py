import sys
sys.path.insert(0, ".")
from core import is_free_model, TaskClassifier

def test_is_free():
    assert is_free_model("lokal-kecil") == True
    assert is_free_model("openai") == False

def test_classifier():
    result = TaskClassifier.classify("Buat REST API")
    assert result[0][0] == "coding"
