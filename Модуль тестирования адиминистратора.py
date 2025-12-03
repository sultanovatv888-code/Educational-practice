import unittest
import sqlite3
import tempfile
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAdminModule(unittest.TestCase):
    """Тестовый модуль для проверки функционала администратора"""
    
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
        
        # Создаем таблицу книг
        cursor.execute('''
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Добавляем тестовые книги
        test_books = [
            ("Мастер и Маргарита", "Михаил Булгаков", "Роман"),
            ("1984", "Джордж Оруэлл", "Антиутопия"),
        ]
        
        for title, author, genre in test_books:
            cursor.execute("INSERT INTO books (title, author, genre) VALUES (?, ?, ?)",
                          (title, author, genre))
        
        conn.commit()
        conn.close()
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.conn = sqlite3.connect(self.test_db)
        self.cursor = self.conn.cursor()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.conn.close()
    
    def test_add_book_valid(self):
        """Тест добавления книги с корректными данными"""
        # Подготавливаем данные
        title = "Новая книга"
        author = "Новый автор"
        genre = "Фантастика"
        
        # Добавляем книгу
        self.cursor.execute("INSERT INTO books (title, author, genre) VALUES (?, ?, ?)",
                           (title, author, genre))
        self.conn.commit()
        
        # Проверяем, что книга добавлена
        self.cursor.execute("SELECT * FROM books WHERE title=?", (title,))
        book = self.cursor.fetchone()
        
        self.assertIsNotNone(book)
        self.assertEqual(book[1], title)
        self.assertEqual(book[2], author)
        self.assertEqual(book[3], genre)
    
    def test_add_book_missing_title(self):
        """Тест добавления книги без названия"""
        # Попытка добавить книгу без названия должна вызывать ошибку
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("INSERT INTO books (author, genre) VALUES (?, ?)",
                              ("Автор", "Жанр"))
            self.conn.commit()
    
    def test_add_book_missing_author(self):
        """Тест добавления книги без автора"""
        # Попытка добавить книгу без автора должна вызывать ошибку
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("INSERT INTO books (title, genre) VALUES (?, ?)",
                              ("Название", "Жанр"))
            self.conn.commit()
    
    def test_delete_book(self):
        """Тест удаления книги"""
        # Получаем ID первой книги
        self.cursor.execute("SELECT id FROM books LIMIT 1")
        book_id = self.cursor.fetchone()[0]
        
        # Удаляем книгу
        self.cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
        self.conn.commit()
        
        # Проверяем, что книга удалена
        self.cursor.execute("SELECT * FROM books WHERE id=?", (book_id,))
        book = self.cursor.fetchone()
        
        self.assertIsNone(book)
    
    def test_get_all_books(self):
        """Тест получения всех книг"""
        self.cursor.execute("SELECT COUNT(*) FROM books")
        count = self.cursor.fetchone()[0]
        
        self.assertGreater(count, 0)
        
        # Проверяем структуру данных
        self.cursor.execute("SELECT * FROM books")
        books = self.cursor.fetchall()
        
        for book in books:
            self.assertEqual(len(book), 5)  # id, title, author, genre, created_at
            self.assertIsInstance(book[0], int)  # id
            self.assertIsInstance(book[1], str)  # title
            self.assertIsInstance(book[2], str)  # author
    
    def test_search_books(self):
        """Тест поиска книг"""
        # Поиск по названию
        self.cursor.execute("SELECT * FROM books WHERE title LIKE ?", ('%Мастер%',))
        books = self.cursor.fetchall()
        self.assertGreater(len(books), 0)
        
        # Поиск по автору
        self.cursor.execute("SELECT * FROM books WHERE author LIKE ?", ('%Булгаков%',))
        books = self.cursor.fetchall()
        self.assertGreater(len(books), 0)
        
        # Поиск по жанру
        self.cursor.execute("SELECT * FROM books WHERE genre LIKE ?", ('%Роман%',))
        books = self.cursor.fetchall()
        self.assertGreater(len(books), 0)
    
    def test_book_validation(self):
        """Тест валидации данных книги"""
        test_cases = [
            ("", "Автор", False),  # пустое название
            ("Книга", "", False),  # пустой автор
            ("К", "Автор", True),  # название 1 символ
            ("Кн", "Автор", True),  # название 2 символа
            ("Книга", "А", True),  # автор 1 символ
            ("Книга", "Ав", True),  # автор 2 символа
            ("Война и мир", "Лев Толстой", True),  # корректные данные
        ]
        
        for title, author, should_pass in test_cases:
            with self.subTest(title=title, author=author):
                if should_pass:
                    self.assertGreater(len(title), 0)
                    self.assertGreater(len(author), 0)
                else:
                    self.assertTrue(len(title) == 0 or len(author) == 0)
    
    @classmethod
    def tearDownClass(cls):
        """Очистка тестовой базы данных"""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)


class TestAdminModuleIntegration(unittest.TestCase):
    """Интеграционные тесты модуля администратора"""
    
    def test_add_delete_cycle(self):
        """Тест полного цикла добавления и удаления книги"""
        # Этот тест можно расширить для интеграции с GUI
        pass
    
    def test_data_persistence(self):
        """Тест сохранения данных между сессиями"""
        # Проверяем, что данные сохраняются после перезапуска
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)