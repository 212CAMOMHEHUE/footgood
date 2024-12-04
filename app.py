from flask import Flask, render_template_string, redirect, url_for, request
import sqlite3
import update_data_script  # Импорт скрипта для обновления данных
import os
if not os.path.exists('/tmp/data.db'):
    print("База данных не найдена. Создаем новую.")

app = Flask(__name__)

# Словарь цветов
colors = [
    ("Команда 1", "#ffa500"),
    ("Команда 2", "#008000"),
    ("Команда 3", "#000080"),
    ("Команда 4", "#FFFFFF"),
    ("Команда 5", "#000000"),
    ("Команда 6", "#FF0000"),
    ("Команда 7", "#808080"),
    ("Команда 8", "#FF00FF"),
    ("Команда 9", "#DEB887"),
    ("Команда 10", "#800080")
]

def get_active_players(cursor):
    cursor.execute("SELECT * FROM your_table_name WHERE participate = 'TRUE'")
    return cursor.fetchall()

@app.route('/')
def index():
    conn = sqlite3.connect('./data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT() FROM your_table_name WHERE participate = 'TRUE'")
    count = cursor.fetchone()[0]

    cursor.execute("SELECT team_member FROM your_table_name LIMIT 1")
    first_row_team_member = cursor.fetchone()

    if first_row_team_member:
        try:
            team_member_count = int(first_row_team_member[0])
        except ValueError:
            team_member_count = 0
    else:
        team_member_count = 0

    if team_member_count:
        num_teams = count // team_member_count
        if count >= team_member_count and count % team_member_count == 0:
            active_players = get_active_players(cursor)

            if not active_players:
                return render_template_string("""
                <!DOCTYPE html>
                <html>
                <body>
                <h1>Нет активных игроков для распределения.</h1>
                <a href='/update_data'><button>Обновить данные</button></a>
                </body>
                </html>
                """)

            teams = [[] for _ in range(num_teams)]
            for i in range(len(active_players)):
                teams[i % num_teams].append(active_players[i])

            result_html = """
            <!DOCTYPE html>
            <html>
            <body>
            <h1>Список команд и игроков:</h1>
            <a href='/update_data'><button>Обновить данные</button></a><br/><br/>
            <div>
            """
            for i in range(len(teams)):
                team_name = f"Команда {i + 1}"
                team_color = colors[i][1] if i < len(colors) else "#FFFFFF"
                result_html += f"""
                <div>
                    <h2 style='color:black;'>{team_name} <span style='background-color: {team_color}; width: 15px; height: 15px; display: inline-block;'></span></h2>
                """
                for player in teams[i]:
                    result_html += f"<p>Игрок: {player[1]} {player[2]}, Рейтинг: {player[3]}</p>"
                result_html += "</div>"

            result_html += """
            </div>
            </body>
            </html>
            """

            return render_template_string(result_html)
        else:
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <body>
            <h1>Невозможно поровну разделить участников на команды.</h1>
            <a href='/update_data'><button>Обновить данные</button></a>
            </body>
            </html>
            """)
    else:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <body>
        <h1>Количество игроков в команде равно нулю, деление невозможно.</h1>
        <a href='/update_data'><button>Обновить данные</button></a>
        </body>
        </html>
        """)

    conn.close()

@app.route('/update_data')
def update_data():
    try:
        update_data_script.run_update()  # Вызов функции обновления данных
        return redirect(url_for('index'))
    except Exception as e:
        return f"Ошибка при обновлении данных: {e}"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
