import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import time

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Quiz Gamificado")
        self.root.geometry("800x600")
        
        # Configurações iniciais
        self.ASSETS_DIR = "Assets"
        self.QUIZ_DIR = "Quizzes"
        os.makedirs(self.ASSETS_DIR, exist_ok=True)
        os.makedirs(self.QUIZ_DIR, exist_ok=True)
        
        # Variáveis de estado
        self.quiz_data = {"nome": "", "perguntas": []}
        self.current_quiz = None
        self.score = 0
        self.streak = 0
        
        # Configuração de estilo
        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        """Configura os estilos visuais"""
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), padding=5)
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Question.TLabel", font=("Arial", 12))

    def setup_ui(self):
        """Interface inicial"""
        self.clear_screen()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(main_frame, text="Sistema de Quiz", style="Title.TLabel").pack(pady=20)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Criar Novo Quiz", 
                  command=self.create_quiz_ui).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Carregar Quiz", 
                  command=self.load_quiz_ui).pack(side=tk.LEFT, padx=10)

    def create_quiz_ui(self):
        """Interface de criação de quiz"""
        self.clear_screen()
        self.quiz_data = {"nome": "", "perguntas": []}
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Nome do quiz
        ttk.Label(main_frame, text="Nome do Quiz:").pack()
        self.quiz_name_entry = ttk.Entry(main_frame, font=("Arial", 12))
        self.quiz_name_entry.pack(fill=tk.X, pady=5)
        
        # Lista de perguntas
        ttk.Label(main_frame, text="Perguntas:").pack()
        self.questions_list = tk.Listbox(main_frame, height=10, font=("Arial", 10))
        self.questions_list.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="+ Adicionar Pergunta", 
                  command=self.add_question_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remover Selecionada", 
                  command=self.remove_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Voltar", 
                  command=self.setup_ui).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Salvar Quiz", 
                  command=self.save_quiz).pack(side=tk.RIGHT, padx=5)

    def add_question_ui(self):
        """Janela para adicionar nova pergunta"""
        quiz_name = self.quiz_name_entry.get()
        if not quiz_name:
            messagebox.showerror("Erro", "Digite um nome para o quiz primeiro!")
            return
            
        self.quiz_data["nome"] = quiz_name
        window = tk.Toplevel(self.root)
        window.title("Nova Pergunta")
        window.geometry("600x600")
        
        # Variáveis
        question_text = tk.StringVar()
        alternatives = [tk.StringVar() for _ in range(4)]
        correct_answer = tk.IntVar(value=-1)
        image_path = tk.StringVar(value="")
        
        # Widgets
        ttk.Label(window, text="Texto da Pergunta:").pack(pady=5)
        ttk.Entry(window, textvariable=question_text, font=("Arial", 11)).pack(fill=tk.X, pady=5)
        
        # Imagem
        ttk.Label(window, text="Imagem (opcional):").pack(pady=5)
        img_frame = ttk.Frame(window)
        img_frame.pack(fill=tk.X, pady=5)
        ttk.Button(img_frame, text="Selecionar...", 
                  command=lambda: self.select_image(image_path, img_preview)).pack(side=tk.LEFT)
        ttk.Label(img_frame, textvariable=image_path).pack(side=tk.LEFT, padx=10)
        img_preview = ttk.Label(window)
        img_preview.pack(pady=5)
        
        # Alternativas
        ttk.Label(window, text="Alternativas (marque a correta):").pack(pady=10)
        
        alt_frame = ttk.Frame(window)
        alt_frame.pack(fill=tk.BOTH, expand=True)
        
        for i in range(4):
            ttk.Radiobutton(alt_frame, variable=correct_answer, value=i).grid(row=i, column=0, padx=5)
            ttk.Entry(alt_frame, textvariable=alternatives[i], font=("Arial", 10)).grid(row=i, column=1, sticky="ew", pady=2)
        
        # Botões
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Cancelar", command=window.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Salvar", 
                  command=lambda: self.save_question(
                      window, question_text.get(), 
                      [alt.get() for alt in alternatives],
                      correct_answer.get(), image_path.get()
                  )).pack(side=tk.RIGHT, padx=5)

    def remove_question(self):
        """Remove a pergunta selecionada"""
        selection = self.questions_list.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma pergunta para remover!")
            return
        
        index = selection[0]
        question_text = self.questions_list.get(index)
        
        if messagebox.askyesno("Confirmar", f"Remover a pergunta:\n{question_text}?"):
            self.quiz_data["perguntas"].pop(index)
            self.questions_list.delete(index)
            messagebox.showinfo("Sucesso", "Pergunta removida!")

    def save_question(self, window, text, alternatives, correct, image_path):
        """Valida e salva a pergunta"""
        if not text or not all(alternatives) or correct == -1:
            messagebox.showerror("Erro", "Preencha todos os campos e marque a resposta correta!")
            return
            
        # Processar imagem
        final_image_path = ""
        if image_path:
            try:
                ext = os.path.splitext(image_path)[1]
                new_name = f"q{len(self.quiz_data['perguntas'])+1}{ext}"
                final_image_path = os.path.join(self.ASSETS_DIR, new_name)
                
                with Image.open(image_path) as img:
                    img.save(final_image_path)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar a imagem: {str(e)}")
                return
        
        # Adicionar pergunta
        self.quiz_data["perguntas"].append({
            "texto": text,
            "alternativas": alternatives,
            "resposta": correct,
            "imagem": final_image_path
        })
        
        # Atualizar lista
        self.questions_list.insert(tk.END, f"Pergunta {len(self.quiz_data['perguntas'])}: {text[:30]}...")
        window.destroy()

    def save_quiz(self):
        """Salva o quiz no arquivo JSON"""
        if not self.quiz_data.get("perguntas"):
            messagebox.showerror("Erro", "Adicione pelo menos uma pergunta antes de salvar!")
            return
            
        default_name = f"{self.quiz_data['nome'].replace(' ', '_')}.json"
        file_path = filedialog.asksaveasfilename(
            initialdir=self.QUIZ_DIR,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("Arquivo Quiz", "*.json")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.quiz_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Sucesso", "Quiz salvo com sucesso!")
                self.setup_ui()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar: {str(e)}")

    def load_quiz_ui(self):
        """Interface para carregar quiz"""
        self.clear_screen()
        
        quizzes = [f for f in os.listdir(self.QUIZ_DIR) if f.endswith('.json')]
        
        if not quizzes:
            messagebox.showinfo("Info", "Nenhum quiz encontrado! Crie um primeiro.")
            self.setup_ui()
            return
            
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(main_frame, text="Selecione um Quiz:", style="Title.TLabel").pack(pady=10)
        
        self.quiz_listbox = tk.Listbox(main_frame, font=("Arial", 12), height=10)
        self.quiz_listbox.pack(fill=tk.BOTH, expand=True, pady=10)
        
        for quiz in quizzes:
            self.quiz_listbox.insert(tk.END, quiz.replace('.json', ''))
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Iniciar Quiz", 
                  command=self.start_quiz).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Voltar", 
                  command=self.setup_ui).pack(side=tk.RIGHT)

    def start_quiz(self):
        """Inicia o quiz selecionado"""
        selection = self.quiz_listbox.curselection()
        if not selection:
            messagebox.showerror("Erro", "Selecione um quiz para começar!")
            return
            
        quiz_name = self.quiz_listbox.get(selection[0]) + '.json'
        quiz_path = os.path.join(self.QUIZ_DIR, quiz_name)
        
        try:
            with open(quiz_path, 'r', encoding='utf-8') as f:
                self.current_quiz = json.load(f)
                
            if not self.current_quiz.get('perguntas'):
                messagebox.showerror("Erro", "Este quiz não tem perguntas válidas!")
                return
                
            self.score = 0
            self.current_question = 0
            self.show_question()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar o quiz: {str(e)}")

    def show_question(self):
        """Mostra a pergunta atual"""
        if self.current_question >= len(self.current_quiz['perguntas']):
            self.show_results()
            return
            
        question = self.current_quiz['perguntas'][self.current_question]
        self.clear_screen()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, 
                 text=f"Pontuação: {self.score}", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        ttk.Label(header_frame, 
                 text=f"Pergunta {self.current_question+1}/{len(self.current_quiz['perguntas'])}", 
                 font=("Arial", 12)).pack(side=tk.RIGHT)
        
        # Imagem (se existir)
        if question.get('imagem') and os.path.exists(question['imagem']):
            try:
                img = Image.open(question['imagem'])
                img.thumbnail((400, 300))
                photo = ImageTk.PhotoImage(img)
                
                img_label = ttk.Label(main_frame, image=photo)
                img_label.image = photo
                img_label.pack(pady=10)
            except Exception as e:
                print(f"Erro ao carregar imagem: {e}")
        
        # Texto da pergunta
        ttk.Label(main_frame, 
                 text=question['texto'], 
                 style="Question.TLabel").pack(pady=20)
        
        # Alternativas
        self.selected_answer = tk.IntVar(value=-1)
        for idx, alt in enumerate(question['alternativas']):
            rb = ttk.Radiobutton(
                main_frame, 
                text=alt, 
                variable=self.selected_answer, 
                value=idx
            )
            rb.pack(anchor=tk.W, pady=5, ipady=5)
        
        # Botão de confirmar
        ttk.Button(main_frame, 
                  text="Confirmar", 
                  command=self.check_answer).pack(pady=20)

    def check_answer(self):
        """Verifica a resposta selecionada"""
        if self.selected_answer.get() == -1:
            messagebox.showerror("Erro", "Selecione uma alternativa antes de confirmar!")
            return
            
        question = self.current_quiz['perguntas'][self.current_question]
        is_correct = (self.selected_answer.get() == question['resposta'])
        
        if is_correct:
            self.score += 100
            messagebox.showinfo("Correto!", f"Resposta correta! +100 pontos\nPontuação: {self.score}")
        else:
            correct_idx = question['resposta']
            correct_text = question['alternativas'][correct_idx]
            messagebox.showerror("Errado", f"Resposta incorreta!\nCorreta: {correct_text}")
        
        self.current_question += 1
        self.show_question()

    def show_results(self):
        """Mostra os resultados finais"""
        self.clear_screen()
        
        main_frame = ttk.Frame(self.root, padding=30)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(main_frame, 
                 text="Quiz Concluído!", 
                 style="Title.TLabel").pack(pady=20)
        
        total = len(self.current_quiz['perguntas'])
        percentage = (self.score / (total * 100)) * 100
        
        ttk.Label(main_frame, 
                 text=f"Pontuação Final: {self.score}/{total*100}",
                 font=("Arial", 14)).pack(pady=10)
        
        ttk.Label(main_frame, 
                 text=f"Desempenho: {percentage:.1f}%",
                 font=("Arial", 14)).pack(pady=10)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, 
                  text="Voltar ao Início", 
                  command=self.setup_ui).pack()

    def select_image(self, path_var, preview_label):
        """Seleciona uma imagem para a pergunta"""
        filetypes = [("Imagens", "*.png;*.jpg;*.jpeg;*.gif")]
        path = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=filetypes)
        
        if path:
            try:
                img = Image.open(path)
                img.thumbnail((200, 200))
                photo = ImageTk.PhotoImage(img)
                
                preview_label.config(image=photo)
                preview_label.image = photo
                path_var.set(path)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível carregar a imagem: {str(e)}")

    def clear_screen(self):
        """Remove todos os widgets da tela"""
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()