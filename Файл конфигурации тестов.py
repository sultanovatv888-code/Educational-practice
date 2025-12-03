"""
Конфигурационный файл для тестирования BookTracker
"""

import os
import tempfile

# Настройки тестовой базы данных
TEST_DATABASE = {
    'filename': tempfile.mktemp(suffix='_booktracker_test.db'),
    'tables': {
        'users': '''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'books': '''
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'user_library': '''
            CREATE TABLE user_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                status TEXT DEFAULT 'Хочу прочитать',
                added_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (book_id) REFERENCES books(id),
                UNIQUE(user_id, book_id)
            )
        '''
    }
}

# Тестовые данные
TEST_DATA = {
    'users': [
        ('admin', 'admin123', 'admin'),
        ('user', 'user123', 'user'),
        ('test_user', 'test123', 'user')
    ],
    'books': [
        ('Мастер и Маргарита', 'Михаил Булгаков', 'Роман'),
        ('1984', 'Джордж Оруэлл', 'Антиутопия'),
        ('Преступление и наказание', 'Фёдор Достоевский', 'Роман'),
        ('Война и мир', 'Лев Толстой', 'Роман'),
        ('Гарри Поттер и философский камень', 'Дж. К. Роулинг', 'Фэнтези')
    ]
}

# Настройки валидации
VALIDATION_RULES = {
    'username': {
        'min_length': 3,
        'max_length': 50,
        'pattern': r'^[a-zA-Z0-9_]+$'  # только буквы, цифры и подчеркивание
    },
    'password': {
        'min_length': 4,
        'max_length': 100
    },
    'book_title': {
        'min_length': 2,
        'max_length': 200
    },
    'author': {
        'min_length': 3,
        'max_length': 100
    }
}

# Настройки статусов книг
BOOK_STATUSES = [
    'Хочу прочитать',
    'Читаю',
    'Прочитано',
    'Отложено'
]

# Настройки тестирования
TEST_SETTINGS = {
    'cleanup_database': True,  # очищать базу после тестов
    'generate_reports': True,  # генерировать отчеты
    'log_level': 'INFO',       # уровень логирования
    'timeout': 30              # таймаут для тестов (секунд)
}

# Пути для отчетов
REPORT_PATHS = {
    'json_reports': 'test_reports/json',
    'text_reports': 'test_reports/text',
    'logs': 'test_reports/logs'
}

def create_report_directories():
    """Создание директорий для отчетов"""
    for path in REPORT_PATHS.values():
        os.makedirs(path, exist_ok=True)