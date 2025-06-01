# game_logic/mode_2_2.py

from flask_socketio import emit, join_room
import re

# Храним секретные числа и последние вопросы для каждой сессии
session_data = {}

def join_game(data):
    room = data["room"]
    join_room(room)

def set_secret(data):
    session_id = data["session_id"]
    secret = data["secret"]
    if session_id not in session_data:
        session_data[session_id] = {}
    session_data[session_id]["secret"] = secret

def handle_guess(data):
    room = data["room"]
    message = data["message"].lower()
    session_id = data["session_id"]

    # Сохраняем последний вопрос игрока
    if session_id not in session_data:
        session_data[session_id] = {}
    session_data[session_id]["last_question"] = message

    # Проверяем прямое угадывание числа
    match = re.search(r"число\s*(равно|это)\s*(-?\d+)", message)
    if match:
        guess = int(match.group(2))
        secret = session_data.get(session_id, {}).get("secret")
        correct = secret is not None and secret == guess
        emit("guess_result_2_2", {
            "target": "creator",
            "value": guess,
            "correct": correct
        }, room=room)
        emit("guess_result_2_2", {
            "target": "guesser",
            "value": guess,
            "correct": correct
        }, room=room)

def handle_reply(data):
    room = data["room"]
    session_id = data["session_id"]
    answer = data.get("answer", "").strip().lower()
    secret = data.get("secret")

    if secret is not None:
        set_secret(data)
        return

    # Находим вопрос от другого игрока
    other_session_id = None
    for role, sid in room_roles.get(room, {}).items():
        if sid != session_id:
            other_session_id = sid
            break

    if not other_session_id or other_session_id not in session_data:
        print("Нет второго игрока или нет данных")
        return

    last_question = session_data[other_session_id].get("last_question", "")
    if not last_question:
        print("Нет вопроса от второго игрока")
        return

    print("Последний вопрос:", last_question)
    print("Ответ:", answer)

    numbers = list(range(-100, 101))
    to_dim = []

    # Обработка вопроса "число больше X?"
    match = re.search(r"число\s*больше\s*(-?\d+)", last_question)
    if match:
        val = int(match.group(1))
        if answer == "да":
            to_dim = [n for n in numbers if n <= val]
        elif answer == "нет":
            to_dim = [n for n in numbers if n > val]

    # Обработка вопроса "число меньше X?"
    match = re.search(r"число\s*меньше\s*(-?\d+)", last_question)
    if match:
        val = int(match.group(1))
        if answer == "да":
            to_dim = [n for n in numbers if n >= val]
        elif answer == "нет":
            to_dim = [n for n in numbers if n < val]

    print("Зачёркиваем числа:", to_dim)

    if to_dim:
        emit("filter_numbers_2_2", {
            "target": "guesser",
            "dim": to_dim
        }, room=room)
        emit("filter_numbers_2_2", {
            "target": "creator",
            "dim": to_dim
        }, room=room)