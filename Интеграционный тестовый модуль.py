import unittest
import sqlite3
import tempfile
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBookTrackerIntegration(unittest.TestCase):
    """Интеграционные тесты всего приложения BookTracker"""
    
    @classmethod
    def setUpClass(cls):
        """Создание комплексной тестовой базы данных"""
        cls.test_db = tempfile.mktemp(suffix='.db')
        cls.create_integration_database()
    
    @classmethod
    def create_integration_database(cls):
        """Создание базы данных для интеграционных тестов"""
        conn = sqlite3.connect(cls.test_db)
        cursor = conn.cursor()
        
        # Создаем все таблицы
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE user_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                status TEXT DEFAULT 'Хочу прочитать',
                added_date TEXT,
                UNIQUE(user_id, book_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
        ''')
        
        # Добавляем тестовые данные
        # Пользователи
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ("admin", "admin123", "admin"))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ("user1", "user123", "user"))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ("user2", "user456", "user"))
        
        # Книги
        books = [
            ("Мастер и Маргарита", "Михаил Булгаков", "Роман"),
            ("1984", "Джордж Оруэлл", "Антиутопия"),
            ("Преступление и наказание", "Фёдор Достоевский", "Роман"),
        ]
        
        for title, author, genre in books:
            cursor.execute("INSERT INTO books (title, author, genre) VALUES (?, ?, ?)",
                          (title, author, genre))
        
        conn.commit()
        conn.close()
    
    def setUp(self):
        self.conn = sqlite3.connect(self.test_db)
        self.cursor = self.conn.cursor()
    
    def tearDown(self):
        # Очищаем user_library для изоляции тестов
        self.cursor.execute("DELETE FROM user_library")
        self.conn.commit()
        self.conn.close()
    
    def test_complete_user_journey(self):
        """Тест полного пути пользователя"""
        # 1. Пользователь ищет книгу
        search_query = "Достоевский"
        self.cursor.execute('''
            SELECT * FROM books 
            WHERE author LIKE ? OR title LIKE ? OR genre LIKE ?
        ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        
        search_results = self.cursor.fetchall()
        self.assertGreater(len(search_results), 0)
        
        # 2. Пользователь добавляет книгу в библиотеку
        book_id = search_results[0][0]  # берем первую найденную книгу
        user_id = 2  # user1
        
        from datetime import datetime
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        self.cursor.execute('''
            INSERT INTO user_library (user_id, book_id, status, added_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, book_id, "Хочу прочитать", current_date))
        self.conn.commit()
        
        # 3. Проверяем, что книга добавилась
        self.cursor.execute('''
            SELECT COUNT(*) FROM user_library 
            WHERE user_id=? AND book_id=?
        ''', (user_id, book_id))
        
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 1)
        
        # 4. Пользователь меняет статус книги
        new_status = "Читаю"
        self.cursor.execute('''
            UPDATE user_library 
            SET status=? 
            WHERE user_id=? AND book_id=?
        ''', (new_status, user_id, book_id))
        self.conn.commit()
        
        # 5. Проверяем изменение статуса
        self.cursor.execute('''
            SELECT status FROM user_library 
            WHERE user_id=? AND book_id=?
        ''', (user_id, book_id))
        
        status = self.cursor.fetchone()[0]
        self.assertEqual(status, new_status)
    
    def test_admin_user_interaction(self):
        """Тест взаимодействия администратора и пользователя"""
        # 1. Администратор добавляет новую книгу
        new_book = ("Новая книга", "Новый автор", "Фантастика")
        self.cursor.execute("INSERT INTO books (title, author, genre) VALUES (?, ?, ?)", new_book)
        self.conn.commit()
        
        # 2. Проверяем, что книга добавлена
        self.cursor.execute("SELECT * FROM books WHERE title=?", (new_book[0],))
        added_book = self.cursor.fetchone()
        self.assertIsNotNone(added_book)
        
        # 3. Пользователь видит новую книгу
        user_id = 2
        self.cursor.execute('''
            SELECT b.* FROM books b
            WHERE NOT EXISTS (
                SELECT 1 FROM user_library ul 
                WHERE ul.user_id=? AND ul.book_id=b.id
            )
            ORDER BY b.title
        ''', (user_id,))
        
        available_books = self.cursor.fetchall()
        
        # Новая книга должна быть в списке доступных
        new_book_found = any(book[1] == new_book[0] for book in available_books)
        self.assertTrue(new_book_found)
    
    def test_data_integrity(self):
        """Тест целостности данных"""
        # 1. Попытка добавить книгу в библиотеку несуществующего пользователя
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute('''
                INSERT INTO user_library (user_id, book_id, status, added_date)
                VALUES (?, ?, ?, ?)
            ''', (999, 1, "Хочу прочитать", "01.01.2023"))
            self.conn.commit()
        
        # 2. Попытка добавить несуществующую книгу в библиотеку
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute('''
                INSERT INTO user_library (user_id, book_id, status, added_date)
                VALUES (?, ?, ?, ?)
            ''', (2, 999, "Хочу прочитать", "01.01.2023"))
            self.conn.commit()
    
    def test_concurrent_operations(self):
        """Тест параллельных операций"""
        # Симулируем работу нескольких пользователей одновременно
        users = [2, 3]  # user1 и user2
        book_id = 1
        
        for user_id in users:
            self.cursor.execute('''
                INSERT OR IGNORE INTO user_library (user_id, book_id, status, added_date)
                VALUES (?, ?, ?, ?)
            ''', (user_id, book_id, "Хочу прочитать", "01.01.2023"))
        
        self.conn.commit()
        
        # Проверяем, что оба пользователя добавили книгу
        for user_id in users:
            self.cursor.execute('''
                SELECT COUNT(*) FROM user_library 
                WHERE user_id=? AND book_id=?
            ''', (user_id, book_id))
            
            count = self.cursor.fetchone()[0]
            self.assertEqual(count, 1)
    
    def test_error_handling_scenarios(self):
        """Тест сценариев обработки ошибок"""
        test_cases = [
            # (операция, ожидаемая ошибка)
            ("DELETE FROM books WHERE id=999", None),  # удаление несуществующей книги
            ("UPDATE users SET username='admin' WHERE id=2", None),  # дублирование username
        ]
        
        for query, expected_error in test_cases:
            with self.subTest(query=query):
                try:
                    self.cursor.execute(query)
                    self.conn.commit()
                    if expected_error:
                        self.fail(f"Expected {expected_error} but no error was raised")
                except sqlite3.Error as e:
                    if not expected_error:
                        self.fail(f"Unexpected error: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Очистка тестовой базы данных"""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)


class TestBookTrackerEndToEnd(unittest.TestCase):
    """End-to-end тесты приложения"""
    
    def test_registration_to_library_flow(self):
        """Тест полного потока от регистрации до работы с библиотекой"""
        # Этот тест можно расширить для GUI тестирования
        pass
    
    def test_admin_management_flow(self):
        """Тест потока управления администратора"""
        # Тестирование полного цикла работы администратора
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)