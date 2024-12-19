from flask import Flask, render_template_string, redirect, url_for, request
import sqlite3
import subprocess
import os
import random

app = Flask(__name__)

# Словарь цветов
colors = [
    ("Команда 1", "#ffa500"),  # Оранжевый
    ("Команда 2", "#008000"),  # Зеленый
    ("Команда 3", "#000080"),  # Синий
    ("Команда 4", "#FFFFFF"),  # Белый
    ("Команда 5", "#000000"),  # Черный
    ("Команда 6", "#FF0000"),  # Красный
    ("Команда 7", "#808080"),  # Серый
    ("Команда 8", "#FF00FF"),  # Розовый
    ("Команда 9", "#DEB887"),  # Коричневый
    ("Команда 10", "#800080")   # Пурпурный
]

def get_active_players(cursor):
    cursor.execute("SELECT * FROM your_table_name WHERE participate = 'TRUE'")
    return cursor.fetchall()

def distribute_players(teams, active_players):
    sorted_players = sorted(active_players, key=lambda x: int(x[3]), reverse=True)
    balanced_teams = [[] for _ in range(len(teams))]

    for player in sorted_players:
        team_index = min(range(len(balanced_teams)), key=lambda idx: sum(int(p[3]) for p in balanced_teams[idx]))
        balanced_teams[team_index].append(player)

    return balanced_teams

def reshuffle_teams(teams, cursor, max_rating_difference=5):
    flat_players = [player for team in teams for player in team]
    num_teams = len(teams)
    team_sizes = [len(team) for team in teams]

    for _ in range(1000):  # Ограничение на количество попыток
        random.shuffle(flat_players)
        reshuffled_teams = [[] for _ in range(num_teams)]
        current_index = 0
        for i, size in enumerate(team_sizes):
            reshuffled_teams[i] = flat_players[current_index:current_index + size]
            current_index += size

        team_ratings = [
            sum(int(player[3]) for player in team) / len(team) for team in reshuffled_teams if team
        ]

        if max(team_ratings) - min(team_ratings) <= max_rating_difference:
            for team_index, team in enumerate(reshuffled_teams):
                for player in team:
                    cursor.execute("UPDATE your_table_name SET team = ? WHERE id = ?", (f"Команда {team_index + 1}", player[0]))
            return reshuffled_teams

    return teams
#
#################### #################### ####################
#####          ##### #########  ######### #####          #####
############## ##### ########## ######### ############## #####
#####          ##### ########## ######### #####          #####
##### ############## ########## ######### ##### ##############
#####          ##### #####          ##### #####          #####
#################### #################### ####################
# тут страница Обновить данные:
#

@app.route('/')
def index():
    conn = sqlite3.connect('C:/Users/212/Desktop/212/footgood/data.db')
    cursor = conn.cursor()

    # Проверяем, есть ли в базе данные о местах команд или новых рейтингах
    cursor.execute("SELECT COUNT(*) FROM your_table_name WHERE current_place IS NOT NULL OR new_rating IS NOT NULL")
    data_exists = cursor.fetchone()[0] > 0

    if data_exists:
        result_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #f4f4f5;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            text-align: center;
            padding: 20px;
            background: #fff;
            border-radius: 14px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }
        h1, h2 {
            margin: 20px 0;
            font-weight: 600;
        }
        p {
            margin: 10px 0;
            color: #666;
        }
        a button {
            padding: 10px 16px;
            background-color: #007aff;
            border: none;
            color: #fff;
            border-radius: 8px;
            font-size: 0.9em;
            cursor: pointer;
            margin-top: 10px;
        }
        a button:hover {
            background-color: #005ecb;
        }
        </style>
        </head>
        <body>
        <div class="container">
            <h1>Места проставлены!</h1>
            <h2>Невозможно загрузить новых участников команд!</h2>
            <p>Сначала сохраните новые значения рейтингов или очистите места.</p>
            <a href='/assign_places'><button>Проставить места</button></a>
        </div>
        </body>
        </html>
        """
        conn.close()
        return render_template_string(result_html)

    cursor.execute("SELECT COUNT() FROM your_table_name WHERE participate = 'TRUE'")
    count = cursor.fetchone()[0]

    cursor.execute("SELECT team_member FROM your_table_name LIMIT 1")
    first_row_team_member = cursor.fetchone()

    if first_row_team_member:
        team_member_count_str = first_row_team_member[0]
        try:
            team_member_count = int(team_member_count_str)
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
            teams = distribute_players(teams, active_players)

            # Записываем команды в базу данных
            for team_index, team in enumerate(teams):
                team_name = f"Команда {team_index + 1}"
                for player in team:
                    cursor.execute("UPDATE your_table_name SET team = ? WHERE id = ?", (team_name, player[0]))

            conn.commit()

            # Форматируем средний рейтинг заранее
            average_ratings = [
                f"{sum(int(player[3]) for player in team) / len(team):.2f}" if len(team) > 0 else "0.00"
                for team in teams
            ]

            colors = ["#FF9500", "#28CD41", "#5E5CE6", "#FF2D55", "#AF52DE"]  # Пример цветов

            result_html = """
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: #f4f4f5;
                color: #333;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: auto;
            }
            h1 {
                text-align: center;
                margin-bottom: 20px;
                font-size: 1.8em;
            }
            .team-container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: center;
            }
            .team {
                max-width: 400px;
                flex: 1 1 calc(33.33% - 20px);
                background: #fff;
                border-radius: 14px;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                padding: 15px;
                box-sizing: border-box;
            }
            .team h2 {
                font-size: 1.2em;
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 10px;
            }
            .team h2 span {
                width: 15px;
                height: 15px;
                display: inline-block;
                border-radius: 50%;
            }
            .team p {
                font-size: 0.9em;
                color: #555;
                margin: 5px 0;
            }
            .buttons {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-bottom: 20px;
            }
            button {
                padding: 10px 16px;
                background-color: #007aff;
                border: none;
                color: #fff;
                border-radius: 8px;
                cursor: pointer;
            }
            button:hover {
                background-color: #005ecb;
            }
            </style>
            </head>
            <body>
            <div class="container">
                <h1>Список команд и игроков:</h1>
                <div class="buttons">
                    <a href='/update_data'><button>Обновить данные</button></a>
                    <a href='/reshuffle_teams'><button>Пересортировать команды</button></a>
                    <a href='/assign_places'><button>Назначить места</button></a>
                </div>
                <div class="team-container">
                {% for i, team in enumerate(teams) %}
                <div class="team">
                    <h2>
                        <span style="background-color: {{ colors[i] }};"></span>
                        Команда {{ i+1 }}
                    </h2>
                    {% for player in team %}
                    <p>Игрок: {{ player[1] }} {{ player[2] }}, Рейтинг: {{ player[3] }}</p>
                    {% endfor %}
                    <p><strong>Средний рейтинг команды:</strong> {{ average_ratings[i] }}</p>
                </div>
                {% endfor %}
                </div>
            </div>
            </body>
            </html>
            """

            return render_template_string(result_html, teams=teams, colors=colors, enumerate=enumerate, average_ratings=average_ratings)

    conn.close()

#
#################### #################### ####################
#####          ##### #########  ######### #####          #####
############## ##### ########## ######### ############## #####
#####          ##### ########## ######### #####          #####
##### ############## ########## ######### ##### ##############
#####          ##### #####          ##### #####          #####
#################### #################### ####################
# тут страница пересортировки команд:
#

@app.route('/reshuffle_teams')
def reshuffle_teams_route():
    conn = sqlite3.connect('C:/Users/212/Desktop/212/footgood/data.db')
    cursor = conn.cursor()

    # Проверяем, есть ли в базе данные о местах команд или новых рейтингах
    cursor.execute("SELECT COUNT(*) FROM your_table_name WHERE current_place IS NOT NULL OR new_rating IS NOT NULL")
    data_exists = cursor.fetchone()[0] > 0

    if data_exists:
        result_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #f4f4f5;
            color: #333;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: auto;
            text-align: center;
            padding: 20px;
            background: #fff;
            border-radius: 14px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            margin: 20px 0;
            font-weight: 600;
        }
        p {
            color: #555;
        }
        a button {
            padding: 10px 16px;
            background-color: #007aff;
            border: none;
            color: #fff;
            border-radius: 8px;
            font-size: 0.9em;
            cursor: pointer;
            margin-top: 10px;
        }
        a button:hover {
            background-color: #005ecb;
        }
        </style>
        </head>
        <body>
        <div class="container">
            <h1>Места проставлены! Невозможно пересортировать участников команд!</h1>
            <p>Сначала сохраните новые значения рейтингов или очистите места.</p>
            <a href='/'><button>Назад</button></a>
        </div>
        </body>
        </html>
        """
        conn.close()
        return render_template_string(result_html)

    # Если данных о местах или рейтингах нет, выполняем пересортировку
    active_players = get_active_players(cursor)

    cursor.execute("SELECT COUNT() FROM your_table_name WHERE participate = 'TRUE'")
    count = cursor.fetchone()[0]

    cursor.execute("SELECT team_member FROM your_table_name LIMIT 1")
    team_member_count_str = cursor.fetchone()[0]
    team_member_count = int(team_member_count_str)

    num_teams = count // team_member_count
    teams = [[] for _ in range(num_teams)]
    teams = distribute_players(teams, active_players)
    reshuffled_teams = reshuffle_teams(teams, cursor, max_rating_difference=5)

    conn.commit()
    conn.close()

    # Форматируем средний рейтинг заранее
    average_ratings = [
        f"{sum(int(player[3]) for player in team) / len(team):.2f}" if len(team) > 0 else "0.00"
        for team in reshuffled_teams
    ]

    colors = ["#FF9500", "#28CD41", "#5E5CE6", "#FF2D55", "#AF52DE"]  # Пример цветов

    result_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: #f4f4f5;
        color: #333;
        margin: 0;
        padding: 20px;
    }
    .container {
        max-width: 1200px;
        margin: auto;
    }
    h1 {
        text-align: center;
        margin-bottom: 20px;
        font-size: 1.8em;
    }
    .team-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
    }
    .team {
        max-width: 400px;
        flex: 1 1 calc(33.33% - 20px);
        background: #fff;
        border-radius: 14px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        padding: 15px;
        box-sizing: border-box;
    }
    .team h2 {
        font-size: 1.2em;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }
    .team h2 span {
        width: 15px;
        height: 15px;
        display: inline-block;
        border-radius: 50%;
    }
    .team p {
        font-size: 0.9em;
        color: #555;
        margin: 5px 0;
    }
    .buttons {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 20px;
    }
    button {
        padding: 10px 16px;
        background-color: #007aff;
        border: none;
        color: #fff;
        border-radius: 8px;
        cursor: pointer;
    }
    button:hover {
        background-color: #005ecb;
    }
    </style>
    </head>
    <body>
    <div class="container">
        <h1>Пересортированные команды:</h1>
        <div class="buttons">
            <a href='/update_data'><button>Обновить данные</button></a>
            <a href='/reshuffle_teams'><button>Пересортировать команды</button></a>
            <a href='/assign_places'><button>Назначить места</button></a>
        </div>
        <div class="team-container">
        {% for i, team in enumerate(reshuffled_teams) %}
        <div class="team">
            <h2>
                <span style="background-color: {{ colors[i] }};"></span>
                Команда {{ i+1 }}
            </h2>
            {% for player in team %}
            <p>Игрок: {{ player[1] }} {{ player[2] }}, Рейтинг: {{ player[3] }}</p>
            {% endfor %}
            <p><strong>Средний рейтинг команды:</strong> {{ average_ratings[i] }}</p>
        </div>
        {% endfor %}
        </div>
    </div>
    </body>
    </html>
    """

    return render_template_string(result_html, reshuffled_teams=reshuffled_teams, colors=colors, enumerate=enumerate, average_ratings=average_ratings)


#
#################### #################### ####################
#####          ##### #########  ######### #####          #####
############## ##### ########## ######### ############## #####
#####          ##### ########## ######### #####          #####
##### ############## ########## ######### ##### ##############
#####          ##### #####          ##### #####          #####
#################### #################### ####################
# тут страница распределения команд по занятым местам за игру:
#

@app.route('/assign_places', methods=['GET', 'POST'])
def assign_places():
    conn = sqlite3.connect('C:/Users/212/Desktop/212/footgood/data.db')
    cursor = conn.cursor()

    # Проверяем количество команд
    cursor.execute("SELECT team, current_place FROM your_table_name WHERE team IS NOT NULL GROUP BY team ORDER BY team")
    teams = cursor.fetchall()
    num_teams = len(teams)

    rating_adjustments = {
        6: [2, 1, 0, 0, -1, -2],
        5: [2, 1, 0, -1, -2],
        4: [2, 1, -1, -2],
        3: [2, 1, -2],
        2: [2, -2]
    }

    adjustments = rating_adjustments.get(num_teams, [])

    if request.method == 'POST':
        if 'save' in request.form:
            # Сохраняем выбранные места в базу данных
            for team, _ in teams:
                selected_place = request.form.get(team)
                if selected_place:
                    # Обновляем текущее место команды
                    cursor.execute("UPDATE your_table_name SET current_place = ? WHERE team = ?", (selected_place, team))

                    # Обновляем новый рейтинг для игроков в команде
                    cursor.execute("SELECT id, rank FROM your_table_name WHERE team = ?", (team,))
                    players = cursor.fetchall()
                    for player_id, rank in players:
                        try:
                            new_rating = int(rank) + adjustments[int(selected_place) - 1]
                            cursor.execute("UPDATE your_table_name SET new_rating = ? WHERE id = ?", (new_rating, player_id))
                        except ValueError:
                            print(f"Невозможно преобразовать рейтинг игрока с id {player_id} в число.")
            conn.commit()

            # Формируем список игроков с разбивкой по командам
            cursor.execute("SELECT team, current_place, name, surname, rank, new_rating FROM your_table_name WHERE team IS NOT NULL ORDER BY team")
            player_data = cursor.fetchall()

            result_html = """
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: #f4f4f5;
                color: #333;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: auto;
                background: #fff;
                border-radius: 14px;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                padding: 20px;
            }
            h1 {
                margin-bottom: 20px;
                font-size: 1.8em;
                font-weight: 600;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            table th, table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            table th {
                background-color: #e0e0e0; /* Тёмно-серый цвет для заголовка */
                font-weight: bold;
            }
            table tr:nth-child(even) {
                background-color: #f4f4f5; /* Светло-серый для чётных строк */
            }
            table tr:nth-child(odd) {
                background-color: #ffffff; /* Белый для нечётных строк */
            }
            </style>
            </head>
            <body>
            <div class="container">
                <h1>Список игроков по командам</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Команда</th>
                            <th>Место</th>
                            <th>Имя</th>
                            <th>Фамилия</th>
                            <th>Старый рейтинг</th>
                            <th>Новый рейтинг</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for team, current_place, name, surname, rank, new_rating in player_data:
                result_html += f"""
                    <tr>
                        <td>{team}</td>
                        <td>{current_place}</td>
                        <td>{name}</td>
                        <td>{surname}</td>
                        <td>{rank}</td>
                        <td>{new_rating}</td>
                    </tr>
                """

            result_html += """
                    </tbody>
                </table>
                <a href='/'><button>Назад</button></a>
            </div>
            </body>
            </html>
            """

            conn.close()
            return render_template_string(result_html)

        elif 'clear' in request.form:
            # Очищаем значения мест и новых рейтингов
            cursor.execute("UPDATE your_table_name SET current_place = NULL, new_rating = NULL")
            conn.commit()

            # Обновляем список команд после очистки
            cursor.execute("SELECT team, current_place FROM your_table_name WHERE team IS NOT NULL GROUP BY team ORDER BY team")
            teams = cursor.fetchall()

    # Генерируем HTML для отображения формы назначения мест
    result_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: #f4f4f5;
        color: #333;
        margin: 0;
        padding: 20px;
    }
    .container {
        max-width: 800px;
        margin: auto;
        background: #fff;
        border-radius: 14px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        padding: 20px;
        text-align: center;
    }
    h1 {
        margin-bottom: 20px;
        font-size: 1.8em;
        font-weight: 600;
    }
    .place-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
        align-items: center;
    }
    .team-row {
        display: flex;
        align-items: center;
        gap: 8px;
        justify-content: flex-start;
        width: 100%;
        max-width: 280px;
        padding: 8px 0;
    }
    .team-row span.color {
        display: inline-block;
        width: 15px;
        height: 15px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .team-row span.name {
        flex-grow: 1;
        text-align: left;
        font-size: 16px;
        font-weight: 500;
    }
    select {
        padding: 5px 10px;
        font-size: 14px;
        border: 1px solid #ccc;
        border-radius: 8px;
        margin-left: auto;
    }
    button {
        padding: 10px 16px;
        background-color: #007aff;
        border: none;
        color: #fff;
        border-radius: 8px;
        font-size: 0.9em;
        cursor: pointer;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    button:hover {
        background-color: #005ecb;
    }
    </style>
    </head>
    <body>
    <div class="container">
        <h1>Назначение мест для команд:</h1>
        <a href='/'><button>Назад</button></a>
        <form method="POST">
            <div class="place-container">
    """

    # Цвета команд
    colors = ["#FF9500", "#28CD41", "#5E5CE6", "#FF2D55", "#AF52DE"]
    color_map = {f"Команда {i+1}": colors[i % len(colors)] for i in range(len(teams))}

    for team, current_place in teams:
        team_color = color_map.get(team, "#FFFFFF")
        result_html += f"""
        <div class="team-row">
            <span class="color" style="background-color: {team_color};"></span>
            <span class="name">{team}</span>
            <select name="{team}">
                <option value="" {'selected' if not current_place else ''}>Выберите место</option>
        """
        for i in range(1, num_teams + 1):
            selected = "selected" if current_place == str(i) else ""
            result_html += f"<option value='{i}' {selected}>Место {i}</option>"

        result_html += "</select></div>"

    result_html += """
            </div>
            <button type="submit" name="save">Сохранить</button>
            <button type="submit" name="clear">Стереть</button>
        </form>
    </div>
    </body>
    </html>
    """

    conn.close()
    return render_template_string(result_html)


#
#################### #################### ####################
#####          ##### #########  ######### #####          #####
############## ##### ########## ######### ############## #####
#####          ##### ########## ######### #####          #####
##### ############## ########## ######### ##### ##############
#####          ##### #####          ##### #####          #####
#################### #################### ####################
# тут кнопка обновить данные из гуглтаблицы:
#

@app.route('/update_data')
def update_data():
    conn = sqlite3.connect('C:/Users/212/Desktop/212/footgood/data.db')
    cursor = conn.cursor()

    script_path = os.path.join(os.path.dirname(__file__), '2.py')
    result = subprocess.run(['python', script_path], capture_output=True, text=True)
    if result.returncode == 0:
        print("Данные успешно обновлены.")
    else:
        print("Ошибка при обновлении данных:", result.stderr)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
