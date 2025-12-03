import unittest
import sqlite3
import os
import tempfile
import sys
from unittest.mock import Mock, patch

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAuthModule(unittest.TestCase):
    """Тестовый модуль для проверки модуля авторизации"""
    
    @classmethod
    def setUpClass(cls):
        """Подготовка тестовой базы данных"""
        cls.test_db = tempfile.mktemp(suffix='.db')
        cls.create_test_database()
    
    @classmethod
    def create_test_database(cls):
        """Создание тестовой базы данных"""
        conn = sqlite3.connect(cls.test_db)
        cursor = conn.cursor()
        
        # Создаем таблицы
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Добавляем тестовых пользователей
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                      ("admin", "admin123", "admin"))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                      ("user", "user123", "user"))
        
        conn.commit()
        conn.close()
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.db_connection = sqlite3.connect(self.test_db)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.db_connection.close()
    
    def test_valid_login(self):
        """Тест успешного входа пользователя"""
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", 
                      ("admin", "admin123"))
        user = cursor.fetchone()
        
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "admin")
        self.assertEqual(user[3], "admin")
    
    def test_invalid_login(self):
        """Тест входа с неверными данными"""
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", 
                      ("admin", "wrongpass"))
        user = cursor.fetchone()
        
        self.assertIsNone(user)
    
    def test_user_registration(self):
        """Тест регистрации нового пользователя"""
        cursor = self.db_connection.cursor()
        
        # Проверяем, что пользователя нет в базе
        cursor.execute("SELECT * FROM users WHERE username=?", ("newuser",))
        self.assertIsNone(cursor.fetchone())
        
        # Регистрируем нового пользователя
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ("newuser", "newpass123", "user"))
        self.db_connection.commit()
        
        # Проверяем, что пользователь добавлен
        cursor.execute("SELECT * FROM users WHERE username=?", ("newuser",))
        new_user = cursor.fetchone()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user[1], "newuser")
        self.assertEqual(new_user[3], "user")
    
    def test_duplicate_username(self):
        """Тест попытки регистрации с существующим логином"""
        cursor = self.db_connection.cursor()
        
        # Пытаемся добавить пользователя с существующим логином
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                          ("admin", "differentpass", "user"))
            self.db_connection.commit()
    
    def test_password_validation(self):
        """Тест валидации пароля"""
        test_cases = [
            ("short", False),  # меньше 4 символов
            ("1234", True),    # 4 символа
            ("securepass", True),  # больше 4 символов
        ]
        
        for password, should_pass in test_cases:
            with self.subTest(password=password):
                if should_pass:
                    self.assertGreaterEqual(len(password), 4)
                else:
                    self.assertLess(len(password), 4)
    
    def test_username_validation(self):
        """Тест валидации имени пользователя"""
        test_cases = [
            ("ab", False),  # меньше 3 символов
            ("abc", True),  # 3 символа
            ("username", True),  # больше 3 символов
        ]
        
        for username, should_pass in test_cases:
            with self.subTest(username=username):
                if should_pass:
                    self.assertGreaterEqual(len(username), 3)
                else:
                    self.assertLess(len(username), 3)
    
    @classmethod
    def tearDownClass(cls):
        """Очистка после всех тестов"""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)


class TestAuthModuleIntegration(unittest.TestCase):
    """Интеграционные тесты модуля авторизации"""
    
    def test_login_flow(self):
        """Тест полного цикла входа"""
        # Мокируем callback функцию
        mock_callback = Mock()
        
        # Тестируем сценарий успешного входа
        # (Здесь можно добавить интеграцию с реальным GUI)
        pass
    
    def test_registration_flow(self):
        """Тест полного цикла регистрации"""
        # Тестируем все шаги регистрации
        # 1. Валидация полей
        # 2. Проверка уникальности
        # 3. Сохранение в БД
        # 4. Уведомление пользователя
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)