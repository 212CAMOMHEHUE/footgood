import sqlite3
import requests
import csv
from io import StringIO

def run_update():
    spreadsheet_id = '1LItfwAGeEVzzn6yudPsUHh90G1ySWdkcrCkLrZZN4-g'
    url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.text
        csv_reader = csv.reader(StringIO(data))
        conn = sqlite3.connect('/tmp/data.db')
        cursor = conn.cursor()

        cursor.execute('DROP TABLE IF EXISTS your_table_name')
        cursor.execute('''
            CREATE TABLE your_table_name (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                surname TEXT,
                rank TEXT,
                participate TEXT,
                team_member TEXT
            )
        ''')

        header = True
        for row in csv_reader:
            if not row:
                continue
            if header:
                header = False
                continue
            row = row[:5] if len(row) >= 5 else row + [None] * (5 - len(row))
            cursor.execute('''
                INSERT INTO your_table_name (name, surname, rank, participate, team_member)
                VALUES (?, ?, ?, ?, ?)
            ''', row)

        conn.commit()
        conn.close()
    else:
        raise Exception(f"Ошибка загрузки данных: {response.status_code}")
