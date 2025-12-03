#!/usr/bin/env python3
"""
Модуль для запуска всех тестов BookTracker
"""

import unittest
import sys
import os
import time
import json
from datetime import datetime

def run_all_tests():
    """Запуск всех тестовых модулей"""
    # Добавляем текущую директорию в путь
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Определяем тесты для запуска
    test_modules = [
        'test_auth_module',
        'test_admin_module', 
        'test_user_module',
        'test_integration'
    ]
    
    # Загружаем и запускаем все тесты
    loader = unittest.TestLoader()
    suites = []
    loaded_modules = []
    
    print("🔍 Поиск тестовых модулей...")
    print("-" * 60)
    
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            suite = loader.loadTestsFromModule(module)
            suites.append(suite)
            loaded_modules.append(module_name)
            print(f"✅ Загружен тестовый модуль: {module_name}")
        except ImportError as e:
            print(f"❌ Ошибка загрузки модуля {module_name}: {e}")
            print(f"   Убедитесь, что файл {module_name}.py существует в текущей директории")
    
    if not suites:
        print("\n⚠️  Нет тестовых модулей для запуска")
        return False
    
    # Объединяем все сьюты
    combined_suite = unittest.TestSuite(suites)
    
    # Подсчитываем общее количество тестов
    total_tests = combined_suite.countTestCases()
    
    print("\n" + "="*60)
    print("🚀 Запуск всех тестов BookTracker")
    print("="*60)
    print(f"📊 Всего тестовых модулей: {len(loaded_modules)}")
    print(f"📈 Общее количество тестов: {total_tests}")
    print(f"⏰ Время начала: {datetime.now().strftime('%H:%M:%S')}")
    print("="*60 + "\n")
    
    # Запускаем тесты с измерением времени
    start_time = time.time()
    
    runner = unittest.TextTestRunner(
        verbosity=2,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(combined_suite)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Выводим итоговую статистику
    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*60)
    
    # Основная статистика
    print(f"\n📈 СТАТИСТИКА:")
    print(f"   Всего тестов: {result.testsRun}")
    print(f"   Успешно:      {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   Провалено:    {len(result.failures)}")
    print(f"   Ошибок:       {len(result.errors)}")
    print(f"   Пропущено:    {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    print(f"\n⏱️  ВРЕМЯ ВЫПОЛНЕНИЯ:")
    print(f"   Общее время:  {execution_time:.2f} секунд")
    print(f"   Среднее время: {(execution_time / result.testsRun):.3f} секунд на тест")
    
    # Детали по модулям
    print(f"\n📁 ПРОТЕСТИРОВАННЫЕ МОДУЛИ:")
    for module in loaded_modules:
        print(f"   • {module}")
    
    # Вывод ошибок, если они есть
    if result.failures:
        print(f"\n❌ ПРОВАЛЕННЫЕ ТЕСТЫ ({len(result.failures)}):")
        print("-" * 40)
        for i, (test, traceback) in enumerate(result.failures, 1):
            test_name = str(test).split()[0]
            print(f"\n{i}. {test_name}")
            print(f"   Ошибка: {traceback.split('AssertionError: ')[-1].split('\\n')[0] if 'AssertionError:' in traceback else 'См. traceback'}")
    
    if result.errors:
        print(f"\n⚠️  ТЕСТЫ С ОШИБКАМИ ({len(result.errors)}):")
        print("-" * 40)
        for i, (test, traceback) in enumerate(result.errors, 1):
            test_name = str(test).split()[0]
            print(f"\n{i}. {test_name}")
            print(f"   Ошибка: {traceback.split('\\n')[-2] if traceback.split('\\n') else 'Неизвестная ошибка'}")
    
    # Генерация отчета
    generate_test_report(result, execution_time, loaded_modules)
    
    # Итоговый вердикт
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print(f"🎉 Процент успешных тестов: {100 * (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun:.1f}%")
        return True
    else:
        print("❌ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ")
        print(f"📉 Процент успешных тестов: {100 * (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun:.1f}%")
        return False

def generate_test_report(result, execution_time, modules):
    """Генерация отчета о тестировании в JSON формате"""
    report = {
        "project": "BookTracker",
        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "execution_time_seconds": round(execution_time, 2),
        "summary": {
            "total_tests": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures),
            "errors": len(result.errors),
            "success_rate": round(100 * (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun, 1)
        },
        "test_modules": modules,
        "failed_tests": [],
        "error_tests": []
    }
    
    # Добавляем информацию о проваленных тестах
    for test, traceback in result.failures:
        test_info = {
            "test_name": str(test).split()[0],
            "error_type": "AssertionError",
            "error_message": traceback.split('AssertionError: ')[-1].split('\\n')[0] if 'AssertionError:' in traceback else "Unknown error"
        }
        report["failed_tests"].append(test_info)
    
    # Добавляем информацию о тестах с ошибками
    for test, traceback in result.errors:
        test_info = {
            "test_name": str(test).split()[0],
            "error_type": "Runtime Error",
            "error_message": traceback.split('\\n')[-2] if traceback.split('\\n') else "Unknown error"
        }
        report["error_tests"].append(test_info)
    
    # Сохраняем отчет в файл
    report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Отчет о тестировании сохранен в файл: {report_filename}")
    
    # Также создаем текстовую версию отчета
    generate_text_report(report, report_filename.replace('.json', '.txt'))

def generate_text_report(report, filename):
    """Генерация текстового отчета"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("ОТЧЕТ О ТЕСТИРОВАНИИ BookTracker\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Дата тестирования: {report['test_date']}\n")
        f.write(f"Время выполнения: {report['execution_time_seconds']} сек.\n\n")
        
        f.write("СВОДНАЯ СТАТИСТИКА:\n")
        f.write("-"*40 + "\n")
        f.write(f"Всего тестов:      {report['summary']['total_tests']}\n")
        f.write(f"Успешно:           {report['summary']['passed']}\n")
        f.write(f"Провалено:         {report['summary']['failed']}\n")
        f.write(f"Ошибок:            {report['summary']['errors']}\n")
        f.write(f"Процент успеха:    {report['summary']['success_rate']}%\n\n")
        
        f.write("ПРОТЕСТИРОВАННЫЕ МОДУЛИ:\n")
        f.write("-"*40 + "\n")
        for module in report['test_modules']:
            f.write(f"• {module}\n")
        
        if report['failed_tests']:
            f.write("\nПРОВАЛЕННЫЕ ТЕСТЫ:\n")
            f.write("-"*40 + "\n")
            for i, test in enumerate(report['failed_tests'], 1):
                f.write(f"{i}. {test['test_name']}\n")
                f.write(f"   Ошибка: {test['error_message']}\n")
        
        if report['error_tests']:
            f.write("\nТЕСТЫ С ОШИБКАМИ ВЫПОЛНЕНИЯ:\n")
            f.write("-"*40 + "\n")
            for i, test in enumerate(report['error_tests'], 1):
                f.write(f"{i}. {test['test_name']}\n")
                f.write(f"   Ошибка: {test['error_message']}\n")
        
        f.write("\n" + "="*60 + "\n")
        if report['summary']['failed'] == 0 and report['summary']['errors'] == 0:
            f.write("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!\n")
        else:
            f.write("❌ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ\n")
        f.write("="*60 + "\n")

def run_specific_module(module_name):
    """Запуск тестов для конкретного модуля"""
    try:
        module = __import__(module_name)
        print(f"\n🔍 Запуск тестов для модуля: {module_name}")
        print("="*60)
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    except ImportError:
        print(f"❌ Модуль {module_name} не найден")
        return False

def run_specific_test(test_name):
    """Запуск конкретного теста"""
    print(f"\n🔍 Поиск теста: {test_name}")
    
    # Ищем тест во всех модулях
    test_modules = ['test_auth_module', 'test_admin_module', 'test_user_module', 'test_integration']
    
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            
            # Ищем тест в модуле
            loader = unittest.TestLoader()
            tests = loader.loadTestsFromName(f'*.{test_name}', module)
            
            if tests.countTestCases() > 0:
                print(f"✅ Найден в модуле: {module_name}")
                print("="*60)
                
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(tests)
                return result.wasSuccessful()
        except (ImportError, AttributeError):
            continue
    
    print(f"❌ Тест {test_name} не найден")
    return False

def show_help():
    """Показать справку по использованию"""
    print("\n📖 СПРАВКА ПО ИСПОЛЬЗОВАНИЮ ТЕСТОВОГО РАННЕРА")
    print("="*60)
    print("\nДоступные команды:")
    print("  python run_tests.py           - Запустить все тесты")
    print("  python run_tests.py all       - Запустить все тесты")
    print("  python run_tests.py auth      - Запустить тесты модуля авторизации")
    print("  python run_tests.py admin     - Запустить тесты модуля администратора")
    print("  python run_tests.py user      - Запустить тесты модуля пользователя")
    print("  python run_tests.py integration - Запустить интеграционные тесты")
    print("  python run_tests.py test test_name - Запустить конкретный тест")
    print("  python run_tests.py help      - Показать эту справку")
    print("\nПримеры:")
    print("  python run_tests.py auth")
    print("  python run_tests.py test test_valid_login")
    print("  python run_tests.py test TestAdminModule.test_add_book_valid")

if __name__ == "__main__":
    # Обработка аргументов командной строки
    if len(sys.argv) == 1 or sys.argv[1] == "all":
        # Запуск всех тестов
        success = run_all_tests()
        sys.exit(0 if success else 1)
    
    elif sys.argv[1] == "auth":
        success = run_specific_module("test_auth_module")
        sys.exit(0 if success else 1)
    
    elif sys.argv[1] == "admin":
        success = run_specific_module("test_admin_module")
        sys.exit(0 if success else 1)
    
    elif sys.argv[1] == "user":
        success = run_specific_module("test_user_module")
        sys.exit(0 if success else 1)
    
    elif sys.argv[1] == "integration":
        success = run_specific_module("test_integration")
        sys.exit(0 if success else 1)
    
    elif sys.argv[1] == "test" and len(sys.argv) > 2:
        test_name = sys.argv[2]
        success = run_specific_test(test_name)
        sys.exit(0 if success else 1)
    
    elif sys.argv[1] == "help":
        show_help()
        sys.exit(0)
    
    else:
        print(f"❌ Неизвестная команда: {sys.argv[1]}")
        show_help()
        sys.exit(1)
