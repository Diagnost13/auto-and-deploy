#!/usr/bin/env python3
"""
Загрузчик данных из CSV-файлов в PostgreSQL.
Перед загрузкой полностью удаляет все старые данные из таблицы (TRUNCATE).
Обрабатывает только файлы вида ЧИСЛО_ЧИСЛО.csv в папке data/.
Параметры подключения берутся из config.ini.
"""

import os
import glob
import csv
import re
import psycopg2
import configparser
from datetime import date

# Чтение конфигурации
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
DB_CONFIG = {
    'dbname': config['database']['dbname'],
    'user': config['database']['user'],
    'password': config['database']['password'],
    'host': config['database']['host'],
    'port': config['database']['port']
}

DATA_DIR = "data"
TODAY = date.today()

def get_shop_cash_from_filename(filename):
    """Извлекает shop_num и cash_num из имени файла."""
    basename = os.path.basename(filename)
    match = re.match(r'^(\d+)_(\d+)\.csv$', basename)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def create_table_if_not_exists(conn):
    """Создаёт таблицу sales, если она ещё не существует."""
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id SERIAL PRIMARY KEY,
                doc_id TEXT NOT NULL,
                item TEXT NOT NULL,
                category TEXT NOT NULL,
                amount INTEGER NOT NULL,
                price NUMERIC(10,2) NOT NULL,
                discount NUMERIC(10,2) NOT NULL,
                upload_date DATE NOT NULL,
                shop_num INTEGER NOT NULL,
                cash_num INTEGER NOT NULL,
                line_num INTEGER NOT NULL
            )
        ''')
        conn.commit()

def truncate_table(conn):
    """Полностью очищает таблицу sales и сбрасывает счётчик id."""
    with conn.cursor() as cur:
        cur.execute('TRUNCATE TABLE sales RESTART IDENTITY')
        conn.commit()
    print("Таблица sales полностью очищена (все старые данные удалены).")

def load_csv_to_db(conn, filepath):
    """Загружает один CSV-файл в БД."""
    shop_num, cash_num = get_shop_cash_from_filename(filepath)
    if shop_num is None or cash_num is None:
        print(f"Пропуск файла {filepath}: не соответствует шаблону")
        return False

    rows_to_insert = []
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            current_doc = None
            line_counter = 0
            for row in reader:
                doc_id = row['doc_id']
                if doc_id != current_doc:
                    current_doc = doc_id
                    line_counter = 1
                else:
                    line_counter += 1
                rows_to_insert.append((
                    doc_id,
                    row['item'],
                    row['category'],
                    int(row['amount']),
                    float(row['price']),
                    float(row['discount']),
                    TODAY,
                    shop_num,
                    cash_num,
                    line_counter
                ))
    except Exception as e:
        print(f"Ошибка чтения файла {filepath}: {e}")
        return False

    with conn.cursor() as cur:
        insert_sql = '''
            INSERT INTO sales (doc_id, item, category, amount, price, discount, upload_date, shop_num, cash_num, line_num)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cur.executemany(insert_sql, rows_to_insert)
        conn.commit()

    print(f"Загружено {len(rows_to_insert)} позиций из {filepath}")
    return True

def main():
    if not os.path.exists(DATA_DIR):
        print(f"Папка {DATA_DIR} не существует. Загрузка не требуется.")
        return

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        create_table_if_not_exists(conn)
        truncate_table(conn)

        pattern = os.path.join(DATA_DIR, "*.csv")
        all_csv = glob.glob(pattern)
        valid_files = [f for f in all_csv if get_shop_cash_from_filename(f)[0] is not None]

        if not valid_files:
            print("Нет подходящих файлов для загрузки.")
            return

        for filepath in valid_files:
            load_csv_to_db(conn, filepath)

    finally:
        conn.close()
    print("Загрузка завершена.")

if __name__ == "__main__":
    main()