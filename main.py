import tkinter as tk
from tkinter import messagebox, ttk
from handlers.user_handler import find_or_create_user, load_users, save_users
from handlers.question_handler import load_questions, prepare_questions
from handlers.results_handler import calculate_results
from utils.timer import Timer
from utils.resource_handler import resource_path
import time
import json

questions_path = resource_path('data/questions.json')
users_path = resource_path('data/users.json')

with open(questions_path, 'r', encoding='utf-8') as file:
    questions = json.load(file)

with open(users_path, 'r', encoding='utf-8') as file:
    users = json.load(file)

class EnhancedQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Quiz App")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.user = None
        self.questions = []
        self.answers = []
        self.timer = Timer(total_duration=10 * 60)  # 10 dakika
        self.timer_label = None
        self.timer_id = None

        self.sections = load_questions()
        self.user_entry_screen()

    def user_entry_screen(self):
        self.clear_window()
        tk.Label(self.root, text="User Login", font=("Arial", 24)).pack(pady=20)
        tk.Label(self.root, text="Name:", font=("Arial", 14)).pack()
        self.name_entry = tk.Entry(self.root, font=("Arial", 14))
        self.name_entry.pack()
        tk.Label(self.root, text="Email:", font=("Arial", 14)).pack()
        self.email_entry = tk.Entry(self.root, font=("Arial", 14))
        self.email_entry.pack()
        tk.Button(self.root, text="Login", font=("Arial", 14), command=self.check_user).pack(pady=20)

    def check_user(self):
        """Kullanıcı girişini kontrol eder ve sınav hakkını denetler."""
        name = self.name_entry.get()
        email = self.email_entry.get()

        if not name or not email:
            messagebox.showerror("Error", "Please fill in all fields!")
            return
        self.questions = prepare_questions(self.sections)  # Soruları yükle
        self.user = find_or_create_user(email, name)

        # Kullanıcının sınav hakkını kontrol et
        if len(self.user["history"]) >= 2:
            messagebox.showinfo("Limit Reached", "You have already taken the maximum number of exams (2).")
            self.view_previous_results()
            return

        messagebox.showinfo("Welcome", f"Welcome, {self.user['name']}!")
        self.main_menu()

    def show_question(self, index):
        self.clear_window()

        if index >= len(self.questions):
            self.review_answers()
            return

        question = self.questions[index]
        tk.Label(self.root, text=question["question_text"], font=("Arial", 14), wraplength=600).pack(pady=20)

        # Kullanıcının seçtiği cevapları saklamak için
        if "selected" not in question:
            question["selected"] = []

        def toggle_selection(option_index):
            if option_index in question["selected"]:
                question["selected"].remove(option_index)
            else:
                question["selected"].append(option_index)

            # Seçilen butonların rengini güncelle
            for opt_idx, button in enumerate(option_buttons, start=1):
                button.config(fg="blue" if opt_idx in question["selected"] else "black")

        # Seçenekler için butonları oluştur
        option_buttons = []
        for idx, option in enumerate(question["options"], start=1):
            button = tk.Button(
                self.root,
                text=f"{idx}. {option}",
                font=("Arial", 12),
                command=lambda opt_idx=idx: toggle_selection(opt_idx)
            )
            button.pack(pady=5)
            option_buttons.append(button)

        # "Next" butonu
        tk.Button(
            self.root,
            text="Next",
            font=("Arial", 14),
            command=lambda: self.record_answer_and_next(index)
        ).pack(pady=20)


    def main_menu(self):
        self.clear_window()

        tk.Label(self.root, text=f"Welcome, {self.user['name']}!", font=("Arial", 16)).pack(pady=20)

        # Kullanıcının sınav hakkını kontrol et
        if len(self.user["history"]) >= 2:
            tk.Label(self.root, text="You have reached the maximum exam attempts (2).", font=("Arial", 14), fg="red").pack(pady=10)
            tk.Button(self.root, text="View Previous Results", font=("Arial", 14), command=self.view_previous_results).pack(pady=20)
            tk.Button(self.root, text="Logout", font=("Arial", 14), command=self.user_entry_screen).pack(pady=10)
            return

        # Eğer sınav hakkı varsa sınav başlatma seçeneğini göster
        tk.Button(self.root, text="Start Exam", font=("Arial", 14), command=self.show_exam_guide).pack(pady=10)
        tk.Button(self.root, text="View Previous Results", font=("Arial", 14), command=self.view_previous_results).pack(pady=10)
        tk.Button(self.root, text="Logout", font=("Arial", 14), command=self.user_entry_screen).pack(pady=10)

    def update_timer(self):
        """Ekrandaki timer'ı günceller."""
        # Eğer Timer Label mevcut değilse oluşturulmasın
        if not self.timer_label or not self.timer_label.winfo_exists():
            return

        remaining_time = self.timer.get_remaining_time()
        if self.timer.is_time_up():
            self.timer_label.config(text="Time is up!")
            self.finalize_exam()  # Süre dolduğunda sınavı tamamla
        else:
            minutes, seconds = divmod(int(remaining_time), 60)
            self.timer_label.config(text=f"Time Remaining: {minutes:02}:{seconds:02}")
            self.timer_id = self.root.after(1000, self.update_timer)

    def stop_timer(self):
        """Timer'ı durdurur."""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer.stop()

    def show_exam_guide(self):
        """
        Kullanıcıya sınav rehberi gösterir.
        """
        self.clear_window()

        # Sınav rehberi
        tk.Label(self.root, text="Exam Guide", font=("Arial", 16)).pack(pady=10)

        total_questions = len(self.questions)
        exam_duration_minutes = self.timer.total_duration // 60

        guide_text = (
            f"Welcome to the exam!\n\n"
            f"- Total Questions: {total_questions}\n"
            f"- Exam Duration: {exam_duration_minutes} minutes\n"
            f"- Minimum Passing Score: 75%\n\n"
            f"Instructions:\n"
            f"1. Read each question carefully.\n"
            f"2. Select the correct answer for each question.\n"
            f"3. You can review and change your answers before submitting.\n"
            f"4. The exam will end automatically when time is up.\n"
        )

        tk.Label(self.root, text=guide_text, font=("Arial", 12), wraplength=700, justify="left").pack(pady=10)

        # Başlama butonu
        tk.Button(self.root, text="Start Exam", font=("Arial", 14), command=self.start_exam).pack(pady=20)

        # Ana menüye dönme butonu
        tk.Button(self.root, text="Back to Main Menu", font=("Arial", 14), command=self.main_menu).pack(pady=10)

    def start_exam(self):
        """
        Sınavı başlatır ve ilk soruyu gösterir.
        """
        self.clear_window()  # Ekranı temizle
        self.timer.start()  # Zamanlayıcıyı başlat
        self.update_timer()  # Zamanlayıcıyı güncellemeye başla
        self.show_question(0)  # İlk soruyu göster

    def show_question(self, index):
        self.clear_window()

        if index >= len(self.questions):
            self.review_answers()
            return

        question = self.questions[index]
        tk.Label(self.root, text=question["question_text"], font=("Arial", 14), wraplength=600).pack(pady=20)

        # Kullanıcının seçtiği cevapları saklamak için
        if "selected" not in question:
            question["selected"] = []

        def toggle_selection(option_index):
            if option_index in question["selected"]:
                question["selected"].remove(option_index)
            else:
                question["selected"].append(option_index)

            # Seçilen butonların rengini güncelle
            for opt_idx, button in enumerate(option_buttons, start=1):
                button.config(fg="blue" if opt_idx in question["selected"] else "black")

        # Seçenekler için butonları oluştur
        option_buttons = []
        for idx, option in enumerate(question["options"], start=1):
            button = tk.Button(
                self.root,
                text=f"{idx}. {option}",
                font=("Arial", 12),
                command=lambda opt_idx=idx: toggle_selection(opt_idx)
            )
            button.pack(pady=5)
            option_buttons.append(button)

        # "Next" butonu
        tk.Button(
            self.root,
            text="Next",
            font=("Arial", 14),
            command=lambda: self.record_answer_and_next(index)
        ).pack(pady=20)


    def record_answer_and_next(self, index):
        """
        Kullanıcının bir soruya verdiği yanıtı kaydeder ve bir sonraki soruya geçer.
        """
        question = self.questions[index]
        correct_answers = question["correct_answer"] if isinstance(question["correct_answer"], list) else [question["correct_answer"]]

        # Doğru seçilen cevapları belirle
        correct_selected = set(question["selected"]) & set(correct_answers)

        # Puanlama
        if len(correct_answers) > 0:
            score = question["score"] * (len(correct_selected) / len(correct_answers))
        else:
            score = 0

        self.answers.append({
            "question": question["question_text"],
            "selected": question["selected"],
            "correct_answers": correct_answers,
            "section_name": question["section_name"],
            "options": question["options"],
            "is_correct": len(correct_selected) == len(correct_answers),
            "score": score
        })

        # Bir sonraki soruya geç
        self.show_question(index + 1)

    def review_answers(self):
        """Kullanıcının verdiği cevapları gözden geçirme ve değiştirme ekranı."""
        self.clear_window()
        tk.Label(self.root, text="Review Your Answers", font=("Arial", 16)).pack(pady=10)

        # Kaydırılabilir yapı için Canvas ve Scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Soruları ve mevcut cevapları göster
        for idx, answer in enumerate(self.answers):
            frame = tk.Frame(scrollable_frame, bd=1, relief="solid", padx=10, pady=10)
            frame.pack(fill="x", pady=5)

            # Soru başlığı
            tk.Label(
                frame,
                text=f"Q{idx + 1}: {answer['question']}",
                font=("Arial", 12),
                wraplength=700,
                anchor="w",
                justify="left"
            ).grid(row=0, column=0, columnspan=2, sticky="w")

            # Seçenekleri göster ve kullanıcı yanıtlarını düzenlemek için buton ekle
            for opt_idx, option in enumerate(answer["options"], start=1):
                is_selected = opt_idx in answer["selected"]
                button_text = f"{opt_idx}. {option}"
                button_fg = "blue" if is_selected else "black"
                tk.Button(
                    frame,
                    text=button_text,
                    fg=button_fg,
                    font=("Arial", 10),
                    command=lambda q_idx=idx, o_idx=opt_idx: self.change_answer(q_idx, o_idx)
                ).grid(row=1 + opt_idx, column=0, padx=10, sticky="w")

        # Sınavı tamamla butonu
        tk.Button(self.root, text="Submit Exam", font=("Arial", 14), command=self.finalize_exam).pack(pady=20)

    def change_answer(self, question_idx, selected_option):
        """
        Kullanıcının seçtiği cevabı değiştirir.
        """
        # Yanıt zaten seçilmişse kaldır; değilse ekle
        if selected_option in self.answers[question_idx]["selected"]:
            self.answers[question_idx]["selected"].remove(selected_option)
        else:
            self.answers[question_idx]["selected"].append(selected_option)

        # Yanıtları gözden geçirme ekranını yeniden yükle
        self.review_answers()


    def finalize_exam(self):
        """
        Kullanıcının sınavını sonlandırır, sonuçları hesaplar, kaydeder ve timer'ı durdurur.
        """
        # Timer'ı durdur
        self.stop_timer()

        # Sonuçları hesapla
        section_results, total_correct, total_questions, overall_percentage = calculate_results(
            self.answers, self.sections
        )

        # Kullanıcı geçmişine sonuçları ekle
        self.user["history"].append({
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": section_results,
            "overall_percentage": overall_percentage
        })

        # JSON dosyasına kaydet
        users = load_users()
        for user in users:
            if user["email"] == self.user["email"]:
                user["history"] = self.user["history"]
                break
        save_users(users)

        # Sonuçları detaylı şekilde göster
        self.display_results(section_results, total_correct, total_questions, overall_percentage)

    def display_results(self, section_results, total_correct, total_questions, overall_percentage):
        """Sınav sonuçlarını detaylı bir şekilde gösterir."""
        self.clear_window()
        tk.Label(self.root, text="Exam Results", font=("Arial", 16)).pack(pady=10)

        # Genel sonuçları göster
        tk.Label(
            self.root,
            text=f"Overall Score: {total_correct} / {total_questions} ({overall_percentage:.2f}%)",
            font=("Arial", 14)
        ).pack(pady=10)

        # Başarı durumu
        if overall_percentage >= 75:
            tk.Label(self.root, text="You Passed! 🎉", font=("Arial", 16), fg="green").pack(pady=10)
        else:
            tk.Label(self.root, text="You Did Not Pass. 😔", font=("Arial", 16), fg="red").pack(pady=10)

        # Soruları detaylı göster
        tk.Label(self.root, text="Detailed Results", font=("Arial", 14)).pack(pady=10)
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for idx, answer in enumerate(self.answers):
            frame = tk.Frame(scrollable_frame, bd=1, relief="solid", padx=10, pady=10)
            frame.pack(fill="x", pady=5)

            # Soru başlığı
            tk.Label(
                frame,
                text=f"Q{idx + 1}: {answer['question']}",
                font=("Arial", 12),
                wraplength=700,
                anchor="w",
                justify="left"
            ).grid(row=0, column=0, columnspan=2, sticky="w")

            # Seçenekleri göster
            for opt_idx, option in enumerate(answer["options"], start=1):
                color = (
                    "green" if opt_idx in answer["correct_answers"] else
                    "red" if opt_idx in answer["selected"] and opt_idx not in answer["correct_answers"] else
                    "black"
                )
                tk.Label(
                    frame,
                    text=f"{opt_idx}. {option}",
                    fg=color,
                    font=("Arial", 10),
                    wraplength=700,
                    anchor="w",
                    justify="left"
                ).grid(row=1 + opt_idx, column=0, padx=10, sticky="w")

            # Kullanıcının seçimini vurgula
            selected_options_text = ", ".join(str(opt) for opt in answer["selected"])
            tk.Label(
                frame,
                text=f"Your Selection: {selected_options_text}",
                font=("Arial", 10),
                fg="blue"
            ).grid(row=len(answer["options"]) + 2, column=0, sticky="w", pady=5)

        # Ana menüye dönme butonu
        tk.Button(self.root, text="Main Menu", font=("Arial", 14), command=self.main_menu).pack(pady=20)

            
    def view_previous_results(self):
        """Önceki sınav sonuçlarını görüntüler."""
        self.clear_window()
        tk.Label(self.root, text="Previous Results", font=("Arial", 16)).pack(pady=20)

        # Kullanıcının geçmişi yoksa bilgi ver
        if not self.user["history"]:
            tk.Label(self.root, text="No previous results found.", font=("Arial", 14)).pack(pady=20)
            tk.Button(self.root, text="Main Menu", font=("Arial", 14), command=self.main_menu).pack(pady=10)
            return

        # Kullanıcının geçmişi varsa tablo düzeninde göster
        for attempt in self.user["history"]:
            tk.Label(self.root, text=f"Date: {attempt['date']}", font=("Arial", 12)).pack(pady=5)
            for section, result in attempt["results"].items():
                result_text = f"{section}: {result['correct']} / {result['total']}"
                tk.Label(self.root, text=result_text, font=("Arial", 12)).pack()
            tk.Label(self.root, text=f"Overall: {attempt['overall_percentage']:.2f}%", font=("Arial", 12)).pack(pady=5)

        tk.Button(self.root, text="Main Menu", font=("Arial", 14), command=self.main_menu).pack(pady=20)

    def clear_window(self):
        """Ekranı temizler ve gerekli olmayan widget'ları kaldırır."""
        for widget in self.root.winfo_children():
            # Timer Label'ın kaldırılmasını önleyin
            if widget == self.timer_label:
                continue
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedQuizApp(root)
    root.mainloop()
