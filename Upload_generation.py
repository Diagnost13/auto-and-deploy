#!/usr/bin/env python3
"""
Генератор CSV-выгрузок для магазинов.
Формат имени: {shop_num}_{cash_num}.csv
Запускается ежедневно, кроме воскресенья (проверка внутри скрипта).
"""

import os
import csv
import random
import string
import argparse
from datetime import datetime

# Список товаров с категориями
PRODUCTS = [
    ("Мыло", "Бытовая химия"),
    ("Шампунь", "Бытовая химия"),
    ("Порошок стиральный", "Бытовая химия"),
    ("Средство для мытья посуды", "Бытовая химия"),
    ("Полотенце", "Текстиль"),
    ("Простыня", "Текстиль"),
    ("Наволочка", "Текстиль"),
    ("Тарелка", "Посуда"),
    ("Чашка", "Посуда"),
    ("Кастрюля", "Посуда"),
    ("Сковорода", "Посуда"),
    ("Вилка", "Посуда"),
    ("Ложка", "Посуда"),
    ("Нож", "Посуда"),
    ("Футболка", "Одежда"),
    ("Джинсы", "Одежда"),
    ("Куртка", "Одежда"),
]

def generate_doc_id(existing_ids):
    """Генерирует уникальный численно-буквенный идентификатор чека."""
    while True:
        doc_id = f"DOC{random.randint(10000, 99999)}{random.choice(string.ascii_uppercase)}{random.randint(100, 999)}"
        if doc_id not in existing_ids:
            existing_ids.add(doc_id)
            return doc_id

def generate_receipt(existing_doc_ids, max_items=5):
    """Генерирует один чек (список строк CSV)."""
    doc_id = generate_doc_id(existing_doc_ids)
    num_items = random.randint(1, max_items)
    receipt_lines = []
    for _ in range(num_items):
        product, category = random.choice(PRODUCTS)
        amount = random.randint(1, 10)
        price = round(random.uniform(10.0, 1000.0), 2)
        discount = round(random.uniform(0, price * 0.3), 2)
        receipt_lines.append({
            'doc_id': doc_id,
            'item': product,
            'category': category,
            'amount': amount,
            'price': price,
            'discount': discount
        })
    return receipt_lines

def generate_csv_for_shop_cash(shop_num, cash_num, num_receipts_range=(10, 100)):
    """Генерирует CSV-файл для одной кассы."""
    filename = f"data/{shop_num}_{cash_num}.csv"
    existing_doc_ids = set()
    all_lines = []
    num_receipts = random.randint(*num_receipts_range)
    for _ in range(num_receipts):
        receipt_lines = generate_receipt(existing_doc_ids)
        all_lines.extend(receipt_lines)
    
    os.makedirs("data", exist_ok=True)
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['doc_id', 'item', 'category', 'amount', 'price', 'discount'])
        writer.writeheader()
        writer.writerows(all_lines)
    print(f"Сгенерирован {filename} (чеков: {num_receipts}, позиций: {len(all_lines)})")

def main():
    parser = argparse.ArgumentParser(description='Генерация CSV-выгрузок для магазинов')
    parser.add_argument('--shops', type=int, default=5, help='Количество магазинов (N)')
    parser.add_argument('--max-cash', type=int, default=3, help='Максимальное количество касс на магазин')
    args = parser.parse_args()

    if datetime.now().weekday() == 6:
        print("Сегодня воскресенье, генерация отменена.")
        return

    print(f"Начало генерации для {args.shops} магазинов (макс. касс: {args.max_cash})")
    for shop_num in range(1, args.shops + 1):
        cash_count = random.randint(1, args.max_cash)
        for cash_num in range(1, cash_count + 1):
            generate_csv_for_shop_cash(shop_num, cash_num)
    print("Генерация завершена.")

if __name__ == "__main__":
    main()
