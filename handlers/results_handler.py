def calculate_results(answers, sections):
    """
    Kullanıcının verdiği yanıtları analiz eder ve sonuçları döndürür.
    """
    section_results = {}
    total_correct = 0
    total_questions = 0

    # Her bir bölümü analiz et
    for section in sections:
        section_name = section["section_name"]
        section_questions = [q for q in answers if q["section_name"] == section_name]

        correct_answers = sum(1 for q in section_questions if q["is_correct"])
        section_total = len(section_questions)
        section_score = sum(q["score"] for q in section_questions)

        # Bölüm sonuçlarını kaydet
        section_results[section_name] = {
            "correct": correct_answers,
            "total": section_total,
            "score": section_score
        }

        total_correct += correct_answers
        total_questions += section_total

    # Genel başarı yüzdesi
    overall_percentage = (total_correct / total_questions) * 100 if total_questions > 0 else 0

    return section_results, total_correct, total_questions, overall_percentage


