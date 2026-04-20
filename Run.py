#!/usr/bin/env python3
"""
Скрипт для ежедневного запуска загрузки данных в PostgreSQL.
Проверяет день недели (кроме воскресенья), наличие CSV-файлов в папке data/.
При наличии файлов вызывает Uploading_database.py и после успешного завершения удаляет все обработанные CSV-файлы.
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# Конфигурация
DATA_DIR = "data"
UPLOAD_SCRIPT = "Uploading_database.py"

def is_sunday() -> bool:
    """Возвращает True, если сегодня воскресенье."""
    return datetime.now().weekday() == 6

def has_csv_files() -> bool:
    """Проверяет наличие файлов вида *_.csv в папке data/."""
    data_path = Path(DATA_DIR)
    if not data_path.exists():
        return False
    csv_files = list(data_path.glob("[0-9]*_[0-9]*.csv"))
    return len(csv_files) > 0

def delete_all_csv_files():
    """Удаляет все CSV-файлы из папки data/ после успешной загрузки."""
    data_path = Path(DATA_DIR)
    if not data_path.exists():
        return
    csv_files = list(data_path.glob("*.csv"))
    for f in csv_files:
        try:
            f.unlink()
            print(f"Удалён файл: {f}")
        except Exception as e:
            print(f"Не удалось удалить {f}: {e}")

def main():
    # 1. Пропускаем воскресенье
    if is_sunday():
        print("Сегодня воскресенье, загрузка отменена.")
        return

    # 2. Проверяем наличие CSV-файлов
    if not has_csv_files():
        print("Нет CSV-файлов в папке data/. Загрузка не требуется.")
        return

    # 3. Запускаем скрипт загрузки
    print("Обнаружены CSV-файлы. Запуск Uploading_database.py...")
    try:
        result = subprocess.run(
            [sys.executable, UPLOAD_SCRIPT],
            capture_output=True,
            text=True,
            check=False
        )
        print(result.stdout)
        if result.stderr:
            print("Ошибки:", result.stderr, file=sys.stderr)

        if result.returncode == 0:
            print("Загрузка успешно завершена. Удаляем CSV-файлы...")
            delete_all_csv_files()
        else:
            print(f"Скрипт загрузки завершился с кодом {result.returncode}. Файлы не удалены.")

    except Exception as e:
        print(f"Не удалось запустить {UPLOAD_SCRIPT}: {e}")

if __name__ == "__main__":
    main()