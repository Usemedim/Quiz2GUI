import random
import json
from tkinter import messagebox
from utils.resource_handler import resource_path

def load_questions():
    """Soruları JSON dosyasından yükler."""
    questions_path = resource_path('data/questions.json')  # Dosya yolunu belirle
    try:
        with open(questions_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # JSON dosyasını yükle
            return data["sections"]  # "sections" anahtarını döndür
    except Exception as e:
        raise ValueError(f"Error loading questions: {e}")

def prepare_questions(sections):
    """Soruları karıştırır ve bir liste olarak döndürür."""
    questions = []
    for section in sections:
        for question in section["questions"]:
            question["section_name"] = section["section_name"]  # Bölüm adını ekle
            questions.append(question)
    random.shuffle(questions)  # Soruları karıştır
    return questions
