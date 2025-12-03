import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import os

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("BookTracker - Учет личной библиотеки")
        self.root.geometry("800x600")
        self.current_user = None
        
        # Удаляем старую базу данных, если она есть
        if os.path.exists('booktracker.db'):
            try:
                os.remove('booktracker.db')
            except:
                pass
        
        self.create_database()
        self.show_login_screen()

    def create_database(self):
        """Создание базы данных с правильной структурой"""
        try:
            conn = sqlite3.connect('booktracker.db')
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица книг
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    genre TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица библиотеки пользователя
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'Хочу прочитать',
                    added_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (book_id) REFERENCES books(id),
                    UNIQUE(user_id, book_id)
                )
            ''')
            
            # Проверяем и добавляем тестовых пользователей
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                             ("admin", "admin123", "admin"))
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                             ("user", "user123", "user"))
            
            # Добавляем тестовые книги
            cursor.execute("SELECT COUNT(*) FROM books")
            if cursor.fetchone()[0] == 0:
                books_data = [
                    ("Мастер и Маргарита", "Михаил Булгаков", "Роман"),
                    ("1984", "Джордж Оруэлл", "Антиутопия"),
                    ("Преступление и наказание", "Фёдор Достоевский", "Роман"),
                    ("Гарри Поттер и философский камень", "Дж. К. Роулинг", "Фэнтези"),
                    ("Война и мир", "Лев Толстой", "Роман"),
                    ("Мёртвые души", "Николай Гоголь", "Поэма")
                ]
                
                for title, author, genre in books_data:
                    cursor.execute("INSERT INTO books (title, author, genre) VALUES (?, ?, ?)", 
                                 (title, author, genre))
            
            conn.commit()
            conn.close()
            print("База данных успешно создана!")
            
        except sqlite3.Error as e:
            print(f"Ошибка при создании базы данных: {e}")
            messagebox.showerror("Ошибка", f"Не удалось создать базу данных: {e}")

    def show_login_screen(self):
        """Показ экрана входа"""
        self.clear_screen()
        
        # Заголовок
        header_frame = tk.Frame(self.root, bg='#2c3e50')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="📚 BookTracker", 
                font=('Arial', 24, 'bold'), fg='white', bg='#2c3e50').pack(pady=5)
        tk.Label(header_frame, text="Система управления личной библиотекой", 
                font=('Arial', 12), fg='#bdc3c7', bg='#2c3e50').pack()
        
        # Основная область
        main_frame = tk.Frame(self.root, bg='#ecf0f1')
        main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=20)
        
        # Фрейм авторизации
        auth_frame = tk.LabelFrame(main_frame, text="Авторизация", font=('Arial', 12, 'bold'),
                                  bg='white', padx=20, pady=20)
        auth_frame.pack(expand=True, fill=tk.BOTH)
        
        # Поля ввода
        tk.Label(auth_frame, text="Логин:", font=('Arial', 11), bg='white').grid(row=0, column=0, 
                                                                                sticky='w', pady=10, padx=5)
        self.login_username = tk.Entry(auth_frame, font=('Arial', 11), width=30)
        self.login_username.grid(row=0, column=1, pady=10, padx=5)
        self.login_username.insert(0, "admin")  # Пример для теста
        
        tk.Label(auth_frame, text="Пароль:", font=('Arial', 11), bg='white').grid(row=1, column=0, 
                                                                                 sticky='w', pady=10, padx=5)
        self.login_password = tk.Entry(auth_frame, font=('Arial', 11), width=30, show="*")
        self.login_password.grid(row=1, column=1, pady=10, padx=5)
        self.login_password.insert(0, "admin123")  # Пример для теста
        
        # Кнопки входа
        btn_frame = tk.Frame(auth_frame, bg='white')
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="Войти", font=('Arial', 11, 'bold'),
                 bg='#3498db', fg='white', padx=30, pady=10,
                 command=self.login).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="Регистрация", font=('Arial', 11),
                 bg='#2ecc71', fg='white', padx=20, pady=10,
                 command=self.show_registration_screen).pack(side=tk.LEFT, padx=10)
        
        # Кнопки быстрого входа
        quick_btn_frame = tk.Frame(auth_frame, bg='white')
        quick_btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        tk.Button(quick_btn_frame, text="Быстрый вход: Admin", font=('Arial', 9),
                 bg='#e74c3c', fg='white', padx=10, pady=5,
                 command=lambda: self.set_credentials("admin", "admin123")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(quick_btn_frame, text="Быстрый вход: User", font=('Arial', 9),
                 bg='#f39c12', fg='white', padx=10, pady=5,
                 command=lambda: self.set_credentials("user", "user123")).pack(side=tk.LEFT, padx=5)
        
        # Информационная панель
        info_frame = tk.Frame(self.root, bg='#34495e', height=40)
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)
        info_frame.pack_propagate(False)
        
        tk.Label(info_frame, text=f"📅 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", 
                font=('Arial', 10), fg='white', bg='#34495e').pack(side=tk.LEFT, padx=20)
        tk.Label(info_frame, text="👤 Автор: Татьяна", 
                font=('Arial', 10), fg='white', bg='#34495e').pack(side=tk.RIGHT, padx=20)

    def show_registration_screen(self):
        """Показ экрана регистрации"""
        self.clear_screen()
        
        # Заголовок
        header_frame = tk.Frame(self.root, bg='#2ecc71')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="📝 Регистрация нового пользователя", 
                font=('Arial', 18, 'bold'), fg='white', bg='#2ecc71').pack(pady=10)
        
        # Форма регистрации
        form_frame = tk.Frame(self.root, bg='white', padx=30, pady=20)
        form_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Поля формы
        tk.Label(form_frame, text="Логин*:", font=('Arial', 11), bg='white', 
                anchor='w').grid(row=0, column=0, sticky='w', pady=10, padx=5)
        self.reg_username = tk.Entry(form_frame, font=('Arial', 11), width=35)
        self.reg_username.grid(row=0, column=1, pady=10, padx=5)
        
        tk.Label(form_frame, text="Пароль*:", font=('Arial', 11), bg='white', 
                anchor='w').grid(row=1, column=0, sticky='w', pady=10, padx=5)
        self.reg_password = tk.Entry(form_frame, font=('Arial', 11), width=35, show="*")
        self.reg_password.grid(row=1, column=1, pady=10, padx=5)
        
        tk.Label(form_frame, text="Подтвердите пароль*:", font=('Arial', 11), bg='white', 
                anchor='w').grid(row=2, column=0, sticky='w', pady=10, padx=5)
        self.reg_password_confirm = tk.Entry(form_frame, font=('Arial', 11), width=35, show="*")
        self.reg_password_confirm.grid(row=2, column=1, pady=10, padx=5)
        
        # Кнопки
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.grid(row=3, column=0, columnspan=2, pady=30)
        
        tk.Button(btn_frame, text="Зарегистрироваться", font=('Arial', 12, 'bold'),
                 bg='#27ae60', fg='white', padx=30, pady=10,
                 command=self.register_user).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="Назад", font=('Arial', 11),
                 bg='#95a5a6', fg='white', padx=20, pady=10,
                 command=self.show_login_screen).pack(side=tk.LEFT, padx=10)
        
        # Подсказки
        hint_frame = tk.Frame(form_frame, bg='white')
        hint_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        tk.Label(hint_frame, text="* - обязательные поля\nЛогин должен быть уникальным", 
                font=('Arial', 9), bg='white', fg='#7f8c8d', justify=tk.LEFT).pack()

    def set_credentials(self, username, password):
        """Установка учетных данных в поля входа"""
        self.login_username.delete(0, tk.END)
        self.login_password.delete(0, tk.END)
        self.login_username.insert(0, username)
        self.login_password.insert(0, password)

    def login(self):
        """Обработка входа пользователя"""
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Внимание", "Введите логин и пароль!")
            return
        
        try:
            conn = sqlite3.connect('booktracker.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", 
                         (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                self.current_user = {
                    'id': user[0],
                    'username': user[1],
                    'role': user[2]
                }
                
                if user[2] == "admin":
                    self.show_admin_interface()
                else:
                    self.show_user_interface()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль!")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при входе: {str(e)}")

    def register_user(self):
        """Регистрация нового пользователя"""
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()
        password_confirm = self.reg_password_confirm.get().strip()
        
        # Валидация
        if not username or not password:
            messagebox.showwarning("Внимание", "Заполните обязательные поля!")
            return
        
        if len(username) < 3:
            messagebox.showwarning("Внимание", "Логин должен содержать минимум 3 символа!")
            return
        
        if password != password_confirm:
            messagebox.showwarning("Внимание", "Пароли не совпадают!")
            return
        
        if len(password) < 4:
            messagebox.showwarning("Внимание", "Пароль должен содержать минимум 4 символа!")
            return
        
        try:
            conn = sqlite3.connect('booktracker.db')
            cursor = conn.cursor()
            
            # Проверка существования пользователя
            cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                messagebox.showwarning("Внимание", "Пользователь с таким логином уже существует!")
                conn.close()
                return
            
            # Регистрация нового пользователя
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                         (username, password, "user"))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            
            # Возвращаемся на экран входа
            self.show_login_screen()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при регистрации: {str(e)}")

    # Остальные методы остаются без изменений
    def show_admin_interface(self):
        self.clear_screen()
        
        header = tk.Frame(self.root, bg='#e74c3c')
        header.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(header, text=f"⚙️ РЕЖИМ АДМИНИСТРАТОРА: {self.current_user['username']}", 
                font=('Arial', 16, 'bold'), bg='#e74c3c', fg='white').pack(pady=10)

        add_frame = tk.LabelFrame(self.root, text="Добавить новую книгу", font=('Arial', 10, 'bold'))
        add_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(add_frame, text="Название:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.title_entry = tk.Entry(add_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(add_frame, text="Автор:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.author_entry = tk.Entry(add_frame, width=30)
        self.author_entry.grid(row=1, column=1, padx=5, pady=2)
        
        tk.Label(add_frame, text="Жанр:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.genre_entry = tk.Entry(add_frame, width=30)
        self.genre_entry.grid(row=2, column=1, padx=5, pady=2)

        tk.Button(add_frame, text="Добавить книгу", bg='#27ae60', fg='white',
                 command=self.add_book).grid(row=3, columnspan=2, pady=10)

        list_frame = tk.LabelFrame(self.root, text="Каталог книг", font=('Arial', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.book_tree = ttk.Treeview(list_frame, columns=("ID","Название","Автор","Жанр"), show='headings', height=12)
        for col in ("ID","Название","Автор","Жанр"):
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=120)
        self.book_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Удалить книгу", bg='#c0392b', fg='white',
                 command=self.delete_book).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить список", bg='#2980b9', fg='white',
                 command=self.load_books).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Выйти", bg='#7f8c8d', fg='white',
                 command=self.show_login_screen).pack(side=tk.LEFT, padx=5)

        self.load_books()

    def show_user_interface(self):
        self.clear_screen()
        
        header = tk.Frame(self.root, bg='#3498db')
        header.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(header, text=f"👤 РЕЖИМ ПОЛЬЗОВАТЕЛЯ: {self.current_user['username']}", 
                font=('Arial', 16, 'bold'), bg='#3498db', fg='white').pack(pady=10)

        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(search_frame, text="🔍 Поиск книги:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Найти", bg='#2980b9', fg='white',
                 command=self.search_books).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Сброс", bg='#95a5a6', fg='white',
                 command=self.load_books).pack(side=tk.LEFT, padx=5)

        list_frame = tk.LabelFrame(self.root, text="📚 Доступные книги", font=('Arial', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.book_tree = ttk.Treeview(list_frame, columns=("ID","Название","Автор","Жанр"), show='headings', height=10)
        for col in ("ID","Название","Автор","Жанр"):
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=120)
        self.book_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="➕ Добавить в библиотеку", bg='#27ae60', fg='white',
                 command=self.add_to_library).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📖 Моя библиотека", bg='#f39c12', fg='white',
                 command=self.show_my_library).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🚪 Выйти", bg='#7f8c8d', fg='white',
                 command=self.show_login_screen).pack(side=tk.LEFT, padx=5)

        self.load_books()

    def show_my_library(self):
        self.clear_screen()
        
        header = tk.Frame(self.root, bg='#f39c12')
        header.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(header, text="📖 МОЯ БИБЛИОТЕКА", 
                font=('Arial', 16, 'bold'), bg='#f39c12', fg='white').pack(pady=10)

        list_frame = tk.LabelFrame(self.root, text="Мои книги", font=('Arial', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.library_tree = ttk.Treeview(list_frame, columns=("ID","Название","Автор","Статус","Дата"), show='headings', height=10)
        for col in ("ID","Название","Автор","Статус","Дата"):
            self.library_tree.heading(col, text=col)
            self.library_tree.column(col, width=100)
        self.library_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="✏️ Изменить статус", bg='#9b59b6', fg='white',
                 command=self.change_status).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🔄 Обновить", bg='#2980b9', fg='white',
                 command=self.load_my_library).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🔙 Назад", bg='#95a5a6', fg='white',
                 command=self.show_user_interface).pack(side=tk.LEFT, padx=5)

        self.load_my_library()

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        
        if not title or not author:
            messagebox.showwarning("Ошибка", "Название и автор обязательны!")
            return
            
        try:
            conn = sqlite3.connect('booktracker.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (title, author, genre) VALUES (?, ?, ?)", (title, author, genre))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Книга добавлена в каталог!")
            
            # Очищаем поля после добавления
            self.title_entry.delete(0, tk.END)
            self.author_entry.delete(0, tk.END)
            self.genre_entry.delete(0, tk.END)
            
            self.load_books()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении книги: {str(e)}")

    def delete_book(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите книгу для удаления!")
            return
            
        try:
            book_id = self.book_tree.item(selected[0])['values'][0]
            if messagebox.askyesno("Подтверждение", "Удалить книгу из каталога?"):
                conn = sqlite3.connect('booktracker.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
                cursor.execute("DELETE FROM user_library WHERE book_id=?", (book_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", "Книга удалена!")
                self.load_books()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")

    def add_to_library(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите книгу!")
            return
            
        try:
            book_id = self.book_tree.item(selected[0])['values'][0]
            conn = sqlite3.connect('booktracker.db')
            cursor = conn.cursor()
            
            # Проверяем, есть ли уже книга в библиотеке
            cursor.execute("SELECT * FROM user_library WHERE user_id=? AND book_id=?", 
                         (self.current_user['id'], book_id))
            if cursor.fetchone():
                messagebox.showwarning("Ошибка", "Эта книга уже в вашей библиотеке!")
            else:
                current_date = datetime.datetime.now().strftime("%d.%m.%Y")
                cursor.execute("INSERT INTO user_library (user_id, book_id, status, added_date) VALUES (?, ?, ?, ?)", 
                             (self.current_user['id'], book_id, "Хочу прочитать", current_date))
                messagebox.showinfo("Успех", "Книга добавлена в вашу библиотеку!")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении в библиотеку: {str(e)}")

    def change_status(self):
        selected = self.library_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите книгу!")
            return
        
        try:
            book_id = self.library_tree.item(selected[0])['values'][0]
            current_status = self.library_tree.item(selected[0])['values'][3]
            
            status_window = tk.Toplevel(self.root)
            status_window.title("Изменение статуса")
            status_window.geometry("300x200")
            
            tk.Label(status_window, text="Выберите новый статус:", font=('Arial', 12)).pack(pady=10)
            
            status_var = tk.StringVar(value=current_status)
            
            for status in ["Хочу прочитать", "Читаю", "Прочитано", "Отложено"]:
                tk.Radiobutton(status_window, text=status, variable=status_var, 
                              value=status, font=('Arial', 10)).pack(anchor='w', padx=20)
            
            def save_status():
                try:
                    conn = sqlite3.connect('booktracker.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE user_library SET status=? WHERE user_id=? AND book_id=?", 
                                 (status_var.get(), self.current_user['id'], book_id))
                    conn.commit()
                    conn.close()
                    status_window.destroy()
                    self.load_my_library()
                    messagebox.showinfo("Успех", "Статус обновлен!")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при обновлении статуса: {str(e)}")
            
            tk.Button(status_window, text="Сохранить", bg='#27ae60', fg='white',
                     command=save_status).pack(pady=10)
                     
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при изменении статуса: {str(e)}")

    def search_books(self):
        query = self.search_entry.get().strip()
        
        try:
            conn = sqlite3.connect('booktracker.db')
            cursor = conn.cursor()
            
            if query:
                cursor.execute('''
                    SELECT * FROM books 
                    WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?
                ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            else:
                cursor.execute("SELECT * FROM books")
                
            books = cursor.fetchall()
            conn.close()
            
            self.update_tree(self.book_tree, books)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при поиске: {str(e)}")

    def load_books(self):
        try:
            conn = sqlite3.connect('booktracker.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books")
            books = cursor.fetchall()
            conn.close()
            self.update_tree(self.book_tree, books)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке книг: {str(e)}")

    def load_my_library(self):
        try:
            conn = sqlite3.connect('booktracker.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT b.id, b.title, b.author, ul.status, ul.added_date 
                FROM books b
                JOIN user_library ul ON b.id = ul.book_id
                WHERE ul.user_id = ?
            ''', (self.current_user['id'],))
            books = cursor.fetchall()
            conn.close()
            self.update_tree(self.library_tree, books)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке библиотеки: {str(e)}")

    def update_tree(self, tree, data):
        try:
            for item in tree.get_children():
                tree.delete(item)
            for row in data:
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении таблицы: {str(e)}")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()