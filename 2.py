import sqlite3
import requests
import csv
from io import StringIO

# Получаем данные из Google Таблицы
spreadsheet_id = '1LItfwAGeEVzzn6yudPsUHh90G1ySWdkcrCkLrZZN4-g'   # id оригинальной таблицы
url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv'
response = requests.get(url)

if response.status_code == 200:
    data = response.text
    # Читаем данные как CSV
    csv_reader = csv.reader(StringIO(data))
    
    # Создаем подключение к SQLite базе данных (или создаем новую)
    conn = sqlite3.connect('./footgood/data.db')
    cursor = conn.cursor()

    # Удаляем таблицу, если она уже существует
    cursor.execute('DROP TABLE IF EXISTS your_table_name')

    # Создаем таблицу с заголовками и добавляем новые колонки "новый рейтинг" и "текущее место"
    cursor.execute('''
        CREATE TABLE your_table_name (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            surname TEXT,
            rank TEXT,
            participate TEXT,
            team_member TEXT,
            team TEXT,  -- Колонка для команды
            new_rating TEXT,  -- Новая колонка для нового рейтинга
            current_place TEXT  -- Новая колонка для текущего места
        )
    ''')

    # Флаг для пропуска первой строки заголовков
    header = True

    # Обработка данных
    for row in csv_reader:
        # Пропускаем пустые строки
        if not row:  # Проверяем на пустоту
            continue

        if header:
            header = False  # Пропускаем первую строку с заголовками
            continue
        
        # Обрезаем строку до максимума 5 элементов, добавляем None, если элементов меньше
        row = row[:5] if len(row) >= 5 else row + [None] * (5 - len(row))

        # Проверка, что первое значение не пустое
        if not row[0]:  # Если первое значение пустое
            continue
        
        print("Вставляем строку:", row)

        try:
            cursor.execute('''
                INSERT INTO your_table_name (name, surname, rank, participate, team_member)
                VALUES (?, ?, ?, ?, ?)
            ''', row)
        except sqlite3.Error as e:
            print("Ошибка при вставке данных:", e)

    # Сохраняем изменения
    conn.commit()

    # Получаем и выводим все данные из таблицы
    cursor.execute("SELECT * FROM your_table_name")
    all_rows = cursor.fetchall()
    print("Данные в базе:")
    for r in all_rows:
        print(r)

    # Закрываем соединение
    conn.close()
else:
    print("Ошибка при получении данных:", response.status_code)
