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
        # Если данные о местах или рейтингах существуют, возвращаем сообщение
        result_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body { background-color: #D3D3D3; color: black; font-family: Verdana, sans-serif; }
        .team-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }
        .team { background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 10px; padding: 15px; width: 400px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); }
        .team h2 { margin: 0; font-size: 18px; color: black; }
        .team p { margin: 5px 0; }
        </style>
        </head>
        <body>
        <h1>Места проставлены!</h1> 
        <h2>Невозможно загрузить новых участников команд!</h2>
        <p>Сначала сохраните новые значения рейтингов или очистите места.</p>
        <a href='/assign_places'><button>Проставить места</button></a>
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

            result_html = """
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            body {
                background-color: #D3D3D3;
                color: black;
                font-family: Verdana, sans-serif;
            }
            .team-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
            }
            .team {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 15px;
                width: 400px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
            }
            .team h2 {
                margin: 0;
                font-size: 18px;
                color: black;
            }
            .team p {
                margin: 5px 0;
            }
            </style>
            </head>
            <body>
            <h1>Список команд и игроков:</h1>
            <a href='/update_data'><button>Обновить данные</button></a>
            <a href='/reshuffle_teams'><button>Пересортировать команды</button></a>
            <a href='/assign_places'><button>Назначить места</button></a>
            <div class="team-container">
            """

            for i in range(len(teams)):
                team_name = f"Команда {i + 1}"
                team_color = colors[i][1] if i < len(colors) else "#FFFFFF"
                result_html += f"""
                <div class="team">
                    <h2 style='color:black;'>{team_name} <span style='display:inline-block; width: 15px; height: 15px; background-color: {team_color};'></span></h2>
                """
                for player in teams[i]:
                    result_html += f"<p>Игрок: {player[1]} {player[2]}, Рейтинг: {player[3]}</p>"
                average_rating = sum(int(player[3]) for player in teams[i]) / len(teams[i])
                result_html += f"<p>Средний рейтинг команды: {average_rating:.2f}</p></div>"

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
        # Если данные о местах или рейтингах существуют, возвращаем сообщение
        result_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body { background-color: #D3D3D3; color: black; font-family: Verdana, sans-serif; }
        .team-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }
        .team { background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 10px; padding: 15px; width: 400px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); }
        .team h2 { margin: 0; font-size: 18px; color: black; }
        .team p { margin: 5px 0; }
        </style>
        </head>
        <body>
        <h1>Места проставлены! Невозможно пересортировать участников команд!</h1>
        <p>Сначала сохраните новые значения рейтингов или очистите места.</p>
        <a href='/'><button>Назад</button></a>
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

    result_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body { background-color: #D3D3D3; color: black; font-family: Verdana, sans-serif; }
    .team-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }
    .team { background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 10px; padding: 15px; width: 400px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); }
    .team h2 { margin: 0; font-size: 18px; color: black; }
    .team p { margin: 5px 0; }
    </style>
    </head>
    <body>
    <h1>Пересортированные команды:</h1>
    <a href='/update_data'><button>Обновить данные</button></a>
    <a href='/reshuffle_teams'><button>Пересортировать команды</button></a>
    <a href='/assign_places'><button>Назначить места</button></a>
    <div class="team-container">
    """

    for i in range(len(reshuffled_teams)):
        team_name = f"Команда {i + 1}"
        team_color = colors[i][1] if i < len(colors) else "#FFFFFF"
        result_html += f"""
        <div class="team">
            <h2 style='color:black;'>{team_name} <span style='display:inline-block; width: 15px; height: 15px; background-color: {team_color};'></span></h2>
        """
        for player in reshuffled_teams[i]:
            result_html += f"<p>Игрок: {player[1]} {player[2]}, Рейтинг: {player[3]}</p>"
        average_rating = sum(int(player[3]) for player in reshuffled_teams[i]) / len(reshuffled_teams[i])
        result_html += f"<p>Средний рейтинг команды: {average_rating:.2f}</p></div>"

    result_html += """
    </div>
    </body>
    </html>
    """

    return render_template_string(result_html)

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
        elif 'clear' in request.form:
            # Очищаем значения мест и новых рейтингов
            cursor.execute("UPDATE your_table_name SET current_place = NULL, new_rating = NULL")
            conn.commit()

    # Обновляем список команд и их текущих мест после сохранения
    cursor.execute("SELECT team, current_place FROM your_table_name WHERE team IS NOT NULL GROUP BY team ORDER BY team")
    teams = cursor.fetchall()

    # Генерируем HTML для отображения списка команд
    result_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body { background-color: #D3D3D3; color: black; font-family: Verdana, sans-serif; }
    .place-container { display: flex; flex-direction: column; align-items: center; }
    .team-row { display: flex; align-items: center; margin-bottom: 10px; }
    .team-row span { margin-right: 20px; font-size: 16px; }
    select { padding: 5px; font-size: 14px; }
    </style>
    </head>
    <body>
    <h1>Назначение мест для команд:</h1>
    <a href='/'><button>Назад</button></a>
    <form method="POST">
    <div class="place-container">
    """

    color_map = {team_name: color for team_name, color in colors}

    for team, current_place in teams:
        team_color = color_map.get(team, "#FFFFFF")
        result_html += f"""
        <div class="team-row">
            <span style='background-color: {team_color}; width: 20px; height: 20px; display: inline-block;'></span>
            <span>{team}</span>
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
