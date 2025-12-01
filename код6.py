import sqlite3
from typing import List, Dict
import datetime

class BookTracker:
    def __init__(self, db_name: str = "book_tracker.db"):
        self.db_name = db_name
        self.init_database()
        self.star_time = datetime.datetime.now()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_library (
                library_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                reading_status TEXT DEFAULT 'Хочу прочитать',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                UNIQUE(user_id, book_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ База данных инициализирована")
    
    def add_user(self, username: str) -> bool:
        """Добавление пользователя"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
            conn.close()
            print(f"✅ Пользователь {username} добавлен")
            return True
        except sqlite3.Error:
            print("❌ Пользователь уже существует")
            return False
    
    def add_book_to_catalog(self, title: str, author: str) -> bool:
        """Добавление книги в каталог"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
            conn.commit()
            conn.close()
            print(f"✅ Книга '{title}' добавлена в каталог")
            return True
        except sqlite3.Error as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def add_book_to_library(self, user_id: int, book_id: int) -> bool:
        """Добавление книги в библиотеку"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Проверка существования книги
            cursor.execute("SELECT title FROM books WHERE book_id = ?", (book_id,))
            if not cursor.fetchone():
                print("❌ Книга не найдена")
                return False
            
            # Проверка дубликата
            cursor.execute("SELECT 1 FROM user_library WHERE user_id = ? AND book_id = ?", (user_id, book_id))
            if cursor.fetchone():
                print("❌ Книга уже в библиотеке")
                return False
            
            cursor.execute("INSERT INTO user_library (user_id, book_id) VALUES (?, ?)", (user_id, book_id))
            conn.commit()
            conn.close()
            print("✅ Книга добавлена в библиотеку")
            return True
        except sqlite3.Error as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def get_user_library(self, user_id: int) -> List[Dict]:
        """Получение библиотеки пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ul.library_id, b.book_id, b.title, b.author, ul.reading_status, ul.added_at
            FROM user_library ul
            JOIN books b ON ul.book_id = b.book_id
            WHERE ul.user_id = ?
            ORDER BY ul.added_at DESC
        ''', (user_id,))
        
        library_books = []
        for row in cursor.fetchall():
            library_books.append({
                'library_id': row[0],
                'book_id': row[1],
                'title': row[2],
                'author': row[3],
                'reading_status': row[4],
                'added_at': row[5]
            })
        
        conn.close()
        return library_books
    
    def remove_book_from_library(self, library_id: int) -> bool:
        """Удаление книги из библиотеки"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_library WHERE library_id = ?", (library_id,))
            conn.commit()
            conn.close()
            print("✅ Книга удалена из библиотеки")
            return True
        except sqlite3.Error as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def update_reading_status(self, library_id: int, new_status: str) -> bool:
        """Обновление статуса чтения"""
        valid_statuses = ['Хочу прочитать', 'Читаю', 'Прочитано', 'Отложено']
        
        if new_status not in valid_statuses:
            print(f"❌ Неверный статус. Допустимые: {', '.join(valid_statuses)}")
            return False
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE user_library SET reading_status = ? WHERE library_id = ?", (new_status, library_id))
            conn.commit()
            conn.close()
            print(f"✅ Статус обновлен: {new_status}")
            return True
        except sqlite3.Error as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def get_available_books(self) -> List[Dict]:
        """Получение каталога книг"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT book_id, title, author FROM books ORDER BY title')
        
        books = []
        for row in cursor.fetchall():
            books.append({
                'book_id': row[0],
                'title': row[1],
                'author': row[2]
            })
        
        conn.close()
        return books
    
    def get_user_by_username(self, username: str) -> Dict:
        """Поиск пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id, username FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {'user_id': user[0], 'username': user[1]}
        return None

class BookTrackerApp:
    def __init__(self):
        self.tracker = BookTracker()
        self.current_user = None
        
    def display_menu(self):
        """Главное меню"""
        print("\n📚 BookTracker")
        print("1. Войти")
        print("2. Регистрация")
        print("3. Каталог книг")
        print("4. Добавить книгу в библиотеку")
        print("5. Моя библиотека")
        print("6. Удалить книгу")
        print("7. Изменить статус")
        print("8. Выйти")
    
    def run(self):
        """Запуск приложения"""
        print("🎯 Добро пожаловать в BookTracker!")
        
        while True:
            self.display_menu()
            choice = input("\nВыберите действие (1-8): ")
            
            if choice == '1':
                self.login_user()
            elif choice == '2':
                self.register_user()
            elif choice == '3':
                self.view_catalog()
            elif choice == '4':
                self.add_book_to_library_ui()
            elif choice == '5':
                self.view_my_library()
            elif choice == '6':
                self.remove_book_from_library_ui()
            elif choice == '7':
                self.update_reading_status_ui()
            elif choice == '8':
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор")
    
    def login_user(self):
        """Вход пользователя"""
        username = input("Имя пользователя: ")
        user = self.tracker.get_user_by_username(username)
        
        if user:
            self.current_user = user
            print(f"✅ Вход выполнен! Добро пожаловать, {user['username']}!")
        else:
            print("❌ Пользователь не найден")
    
    def register_user(self):
        """Регистрация"""
        username = input("Имя пользователя: ")
        if self.tracker.add_user(username):
            print("✅ Регистрация успешна!")
    
    def view_catalog(self):
        """Просмотр каталога"""
        books = self.tracker.get_available_books()
        
        if not books:
            print("📭 Каталог пуст")
            return
        
        print("\n📖 Каталог книг:")
        for book in books:
            print(f"ID: {book['book_id']} | {book['title']} - {book['author']}")
    
    def add_book_to_library_ui(self):
        """Добавление книги в библиотеку"""
        if not self.current_user:
            print("❌ Сначала войдите в систему")
            return
        
        try:
            book_id = int(input("ID книги для добавления: "))
            self.tracker.add_book_to_library(self.current_user['user_id'], book_id)
        except ValueError:
            print("❌ Неверный формат ID")
    
    def view_my_library(self):
        """Просмотр библиотеки"""
        if not self.current_user:
            print("❌ Сначала войдите в систему")
            return
        
        library = self.tracker.get_user_library(self.current_user['user_id'])
        
        if not library:
            print("📭 Библиотека пуста")
            return
        
        print(f"\n📚 Моя библиотека ({len(library)} книг):")
        for book in library:
            status_icon = "📖" if book['reading_status'] == 'Читаю' else "✅" if book['reading_status'] == 'Прочитано' else "⭐"
            print(f"ID записи: {book['library_id']}")
            print(f"  📖 {book['title']}")
            print(f"  👤 {book['author']}")
            print(f"  📊 {status_icon} {book['reading_status']}")
            print(f"  📅 {book['added_at']}")
            print("-" * 50)
    
    def remove_book_from_library_ui(self):
        """Удаление книги"""
        if not self.current_user:
            print("❌ Сначала войдите в систему")
            return
        
        try:
            library_id = int(input("ID записи для удаления: "))
            self.tracker.remove_book_from_library(library_id)
        except ValueError:
            print("❌ Неверный формат ID")
    
    def update_reading_status_ui(self):
        """Изменение статуса"""
        if not self.current_user:
            print("❌ Сначала войдите в систему")
            return
        
        try:
            library_id = int(input("ID записи в библиотеке: "))
            
            print("\n📊 Статусы чтения:")
            print("1. Хочу прочитать")
            print("2. Читаю")
            print("3. Прочитано")
            print("4. Отложено")
            
            status_choice = input("Выберите статус (1-4): ")
            status_map = {'1': 'Хочу прочитать', '2': 'Читаю', '3': 'Прочитано', '4': 'Отложено'}
            
            if status_choice in status_map:
                self.tracker.update_reading_status(library_id, status_map[status_choice])
            else:
                print("❌ Неверный выбор")
        except ValueError:
            print("❌ Неверный формат ID")

def demo():
    """Демонстрация работы"""
    print("🚀 Запуск демонстрации...")
    
    app = BookTrackerApp()
    
    # Добавляем тестовые данные
    app.tracker.add_user("ivan_reader")
    app.tracker.add_user("book_lover")
    
    books_data = [
        ("Мастер и Маргарита", "Михаил Булгаков"),
        ("1984", "Джордж Оруэлл"),
        ("Преступление и наказание", "Фёдор Достоевский"),
        ("Гарри Поттер", "Дж. К. Роулинг"),
        ("Маленький принц", "Антуан де Сент-Экзюпери")
    ]
    
    for title, author in books_data:
        app.tracker.add_book_to_catalog(title, author)
    
    print("✅ Демо данные добавлены!")
    app.run()

if __name__ == "__main__":

    demo()
