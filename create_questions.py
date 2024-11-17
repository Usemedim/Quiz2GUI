import tkinter as tk
from tkinter import messagebox, simpledialog
import json

class JSONEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Question Editor")
        self.root.geometry("800x600")
        self.data = None

        self.file_path = "questions.json"  # JSON dosyası
        self.load_json()

        self.setup_ui()

    def load_json(self):
        """JSON dosyasını yükler."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {self.file_path}")
            self.data = {"sections": []}

    def save_json(self):
        """JSON dosyasını kaydeder."""
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Success", f"Data saved to {self.file_path}")

    def setup_ui(self):
        """Arayüzü oluşturur."""
        tk.Label(self.root, text="JSON Question Editor", font=("Arial", 16)).pack(pady=10)

        # Bölümleri listeleme
        self.section_listbox = tk.Listbox(self.root, font=("Arial", 12))
        self.section_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_section_listbox()

        # Kontrol Butonları
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(control_frame, text="Add Section", font=("Arial", 12), command=self.add_section).pack(side="left", padx=5)
        tk.Button(control_frame, text="Edit Section", font=("Arial", 12), command=self.edit_section).pack(side="left", padx=5)
        tk.Button(control_frame, text="Delete Section", font=("Arial", 12), command=self.delete_section).pack(side="left", padx=5)
        tk.Button(control_frame, text="Save JSON", font=("Arial", 12), command=self.save_json).pack(side="right", padx=5)

    def update_section_listbox(self):
        """Bölüm listesini günceller."""
        self.section_listbox.delete(0, tk.END)
        for section in self.data["sections"]:
            self.section_listbox.insert(tk.END, section["section_name"])

    def add_section(self):
        """Yeni bir bölüm ekler."""
        section_name = simpledialog.askstring("Add Section", "Enter section name:")
        if not section_name:
            return
        section_id = len(self.data["sections"]) + 1
        self.data["sections"].append({
            "section_id": section_id,
            "section_name": section_name,
            "questions": []
        })
        self.update_section_listbox()
        messagebox.showinfo("Success", f"Section '{section_name}' added.")

    def edit_section(self):
        """Mevcut bir bölümü düzenler."""
        selected_index = self.section_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No section selected!")
            return

        section = self.data["sections"][selected_index[0]]

        # Soru düzenleme arayüzü
        QuestionEditor(self.root, section, self.save_json)

    def delete_section(self):
        """Bir bölümü siler."""
        selected_index = self.section_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No section selected!")
            return

        section_name = self.data["sections"][selected_index[0]]["section_name"]
        del self.data["sections"][selected_index[0]]
        self.update_section_listbox()
        messagebox.showinfo("Success", f"Section '{section_name}' deleted.")

class QuestionEditor:
    def __init__(self, root, section, save_callback):
        self.section = section
        self.save_callback = save_callback

        self.window = tk.Toplevel(root)
        self.window.title(f"Edit Questions in {section['section_name']}")
        self.window.geometry("800x600")

        # Soru Listesi
        self.question_listbox = tk.Listbox(self.window, font=("Arial", 12))
        self.question_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_question_listbox()

        # Kontrol Butonları
        control_frame = tk.Frame(self.window)
        control_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(control_frame, text="Add Question", font=("Arial", 12), command=self.add_question).pack(side="left", padx=5)
        tk.Button(control_frame, text="Edit Question", font=("Arial", 12), command=self.edit_question).pack(side="left", padx=5)
        tk.Button(control_frame, text="Delete Question", font=("Arial", 12), command=self.delete_question).pack(side="left", padx=5)
        tk.Button(control_frame, text="Close", font=("Arial", 12), command=self.window.destroy).pack(side="right", padx=5)

    def update_question_listbox(self):
        """Soru listesini günceller."""
        self.question_listbox.delete(0, tk.END)
        for question in self.section["questions"]:
            self.question_listbox.insert(tk.END, question["question_text"])

    def add_question(self):
        """Yeni bir soru ekler."""
        question_text = simpledialog.askstring("Add Question", "Enter question text:")
        if not question_text:
            return
        options = []
        for i in range(4):
            option = simpledialog.askstring(f"Option {i + 1}", f"Enter option {i + 1}:")
            if not option:
                return
            options.append(option)
        correct_answer = simpledialog.askstring("Correct Answer", "Enter correct answer(s) (comma-separated):")
        correct_answer = [int(x.strip()) for x in correct_answer.split(",")]

        question_id = len(self.section["questions"]) + 1
        self.section["questions"].append({
            "question_id": question_id,
            "question_text": question_text,
            "options": options,
            "correct_answer": correct_answer
        })
        self.update_question_listbox()
        self.save_callback()
        messagebox.showinfo("Success", "Question added.")

    def edit_question(self):
        """Mevcut bir soruyu düzenler."""
        selected_index = self.question_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No question selected!")
            return

        question = self.section["questions"][selected_index[0]]
        question_text = simpledialog.askstring("Edit Question", "Edit question text:", initialvalue=question["question_text"])
        if not question_text:
            return
        options = []
        for i, option in enumerate(question["options"]):
            new_option = simpledialog.askstring(f"Option {i + 1}", f"Edit option {i + 1}:", initialvalue=option)
            if not new_option:
                return
            options.append(new_option)
        correct_answer = simpledialog.askstring("Correct Answer", "Edit correct answer(s) (comma-separated):", initialvalue=",".join(map(str, question["correct_answer"])))
        correct_answer = [int(x.strip()) for x in correct_answer.split(",")]

        question["question_text"] = question_text
        question["options"] = options
        question["correct_answer"] = correct_answer
        self.update_question_listbox()
        self.save_callback()
        messagebox.showinfo("Success", "Question edited.")

    def delete_question(self):
        """Bir soruyu siler."""
        selected_index = self.question_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No question selected!")
            return

        del self.section["questions"][selected_index[0]]
        self.update_question_listbox()
        self.save_callback()
        messagebox.showinfo("Success", "Question deleted.")


if __name__ == "__main__":
    root = tk.Tk()
    app = JSONEditorApp(root)
    root.mainloop()