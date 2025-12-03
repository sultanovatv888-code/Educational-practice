import unittest
import sqlite3
import tempfile
import os
import sys
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestUserModule(unittest.TestCase):
    """Тестовый модуль для проверки функционала пользователя"""
    
    @classmethod
    def setUpClass(cls):
        """Создание тестовой базы данных"""
        cls.test_db = tempfile.mktemp(suffix='.db')
        cls.create_test_database()
    
    @classmethod
    def create_test_database(cls):
        """Инициализация тестовой базы данных"""
        conn = sqlite3.connect(cls.test_db)
        cursor = conn.cursor()
        
        # Создаем таблицы
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
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ("testuser", "testpass", "user"))
        
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ("otheruser", "otherpass", "user"))
        
        # Добавляем тестовые книги
        test_books = [
            (1, "Книга 1", "Автор 1", "Жанр 1"),
            (2, "Книга 2", "Автор 2", "Жанр 2"),
            (3, "Книга 3", "Автор 3", "Жанр 3"),
        ]
        
        for book_id, title, author, genre in test_books:
            cursor.execute("INSERT INTO books (id, title, author, genre) VALUES (?, ?, ?, ?)",
                          (book_id, title, author, genre))
        
        conn.commit()
        conn.close()
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.conn = sqlite3.connect(self.test_db)
        self.cursor = self.conn.cursor()
        self.test_user_id = 1  # ID testuser
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Очищаем библиотеку пользователя перед следующим тестом
        self.cursor.execute("DELETE FROM user_library WHERE user_id=?", (self.test_user_id,))
        self.conn.commit()
        self.conn.close()
    
    def test_add_book_to_library(self):
        """Тест добавления книги в библиотеку пользователя"""
        book_id = 1
        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        
        # Добавляем книгу в библиотеку
        self.cursor.execute('''
            INSERT INTO user_library (user_id, book_id, status, added_date)
            VALUES (?, ?, ?, ?)
        ''', (self.test_user_id, book_id, "Хочу прочитать", current_date))
        
        self.conn.commit()
        
        # Проверяем добавление
        self.cursor.execute('''
            SELECT * FROM user_library 
            WHERE user_id=? AND book_id=?
        ''', (self.test_user_id, book_id))
        
        library_entry = self.cursor.fetchone()
        
        self.assertIsNotNone(library_entry)
        self.assertEqual(library_entry[1], self.test_user_id)  # user_id
        self.assertEqual(library_entry[2], book_id)  # book_id
        self.assertEqual(library_entry[3], "Хочу прочитать")  # status
    
    def test_duplicate_book_in_library(self):
        """Тест предотвращения добавления дубликата книги"""
        book_id = 1
        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        
        # Первое добавление
        self.cursor.execute('''
            INSERT INTO user_library (user_id, book_id, status, added_date)
            VALUES (?, ?, ?, ?)
        ''', (self.test_user_id, book_id, "Хочу прочитать", current_date))
        self.conn.commit()
        
        # Попытка повторного добавления (должна вызвать ошибку)
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute('''
                INSERT INTO user_library (user_id, book_id, status, added_date)
                VALUES (?, ?, ?, ?)
            ''', (self.test_user_id, book_id, "Читаю", current_date))
            self.conn.commit()
    
    def test_update_book_status(self):
        """Тест изменения статуса книги"""
        book_id = 1
        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        
        # Добавляем книгу
        self.cursor.execute('''
            INSERT INTO user_library (user_id, book_id, status, added_date)
            VALUES (?, ?, ?, ?)
        ''', (self.test_user_id, book_id, "Хочу прочитать", current_date))
        self.conn.commit()
        
        # Изменяем статус
        new_status = "Прочитано"
        self.cursor.execute('''
            UPDATE user_library 
            SET status=? 
            WHERE user_id=? AND book_id=?
        ''', (new_status, self.test_user_id, book_id))
        self.conn.commit()
        
        # Проверяем изменение
        self.cursor.execute('''
            SELECT status FROM user_library 
            WHERE user_id=? AND book_id=?
        ''', (self.test_user_id, book_id))
        
        status = self.cursor.fetchone()[0]
        self.assertEqual(status, new_status)
    
    def test_get_user_library(self):
        """Тест получения библиотеки пользователя"""
        # Добавляем несколько книг в библиотеку
        books_to_add = [1, 2]
        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        
        for book_id in books_to_add:
            self.cursor.execute('''
                INSERT INTO user_library (user_id, book_id, status, added_date)
                VALUES (?, ?, ?, ?)
            ''', (self.test_user_id, book_id, "Хочу прочитать", current_date))
        
        self.conn.commit()
        
        # Получаем библиотеку пользователя
        self.cursor.execute('''
            SELECT b.id, b.title, b.author, ul.status, ul.added_date 
            FROM books b
            JOIN user_library ul ON b.id = ul.book_id
            WHERE ul.user_id = ?
            ORDER BY b.title
        ''', (self.test_user_id,))
        
        library = self.cursor.fetchall()
        
        self.assertEqual(len(library), len(books_to_add))
        
        # Проверяем структуру данных
        for book in library:
            self.assertEqual(len(book), 5)
            self.assertIsInstance(book[0], int)  # id
            self.assertIsInstance(book[1], str)  # title
            self.assertIsInstance(book[2], str)  # author
            self.assertIsInstance(book[3], str)  # status
            self.assertIsInstance(book[4], str)  # added_date
    
    def test_search_functionality(self):
        """Тест функции поиска книг"""
        test_cases = [
            ("Книга", 3),  # поиск по названию
            ("Автор", 3),  # поиск по автору
            ("Жанр", 3),  # поиск по жанру
            ("Несуществующая", 0),  # нет результатов
        ]
        
        for search_query, expected_count in test_cases:
            with self.subTest(query=search_query):
                self.cursor.execute('''
                    SELECT * FROM books 
                    WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?
                ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
                
                results = self.cursor.fetchall()
                self.assertEqual(len(results), expected_count)
    
    def test_status_options(self):
        """Тест доступных статусов книг"""
        valid_statuses = ["Хочу прочитать", "Читаю", "Прочитано", "Отложено"]
        
        for status in valid_statuses:
            with self.subTest(status=status):
                # Проверяем, что статус можно установить
                book_id = 1
                current_date = datetime.datetime.now().strftime("%d.%m.%Y")
                
                # Очищаем перед тестом
                self.cursor.execute("DELETE FROM user_library WHERE user_id=? AND book_id=?", 
                                  (self.test_user_id, book_id))
                
                self.cursor.execute('''
                    INSERT INTO user_library (user_id, book_id, status, added_date)
                    VALUES (?, ?, ?, ?)
                ''', (self.test_user_id, book_id, status, current_date))
                
                self.conn.commit()
                
                # Проверяем установку
                self.cursor.execute('''
                    SELECT status FROM user_library 
                    WHERE user_id=? AND book_id=?
                ''', (self.test_user_id, book_id))
                
                saved_status = self.cursor.fetchone()[0]
                self.assertEqual(saved_status, status)
    
    def test_library_isolation(self):
        """Тест изоляции библиотек разных пользователей"""
        # Добавляем книгу первому пользователю
        book_id = 1
        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        
        self.cursor.execute('''
            INSERT INTO user_library (user_id, book_id, status, added_date)
            VALUES (?, ?, ?, ?)
        ''', (self.test_user_id, book_id, "Хочу прочитать", current_date))
        
        # Проверяем, что у второго пользователя эта книга не отображается
        other_user_id = 2
        self.cursor.execute('''
            SELECT COUNT(*) FROM user_library 
            WHERE user_id=? AND book_id=?
        ''', (other_user_id, book_id))
        
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 0)
    
    @classmethod
    def tearDownClass(cls):
        """Очистка тестовой базы данных"""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)


class TestUserModulePerformance(unittest.TestCase):
    """Тесты производительности модуля пользователя"""
    
    def test_large_library_performance(self):
        """Тест производительности с большой библиотекой"""
        # Можно добавить тест с 1000+ книгами
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)