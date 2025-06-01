# game_logic/mode_2_2.py

from flask_socketio import emit, join_room
import re

# Храним секретные числа для каждой сессии
session_secrets = {}

def join_game(data):
    room = data["room"]
    join_room(room)

def set_secret(data):
    session_id = data["session_id"]
    secret = data["secret"]
    session_secrets[session_id] = secret

def handle_guess(data):
    room = data["room"]
    message = data["message"].lower()
    session_id = data["session_id"]

    # Сохраняем последний вопрос игрока
    if session_id not in session_secrets:
        session_secrets[session_id] = {}

    session_secrets[session_id]["last_question"] = message

    # Никакого фильтра — только если это прямое угадывание числа
    match = re.search(r"число\s*(равно|это)\s*(-?\d+)", message)
    if match:
        guess = int(match.group(2))
        correct = session_secrets.get(session_id, {}).get("secret") == guess
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
        if session_id not in session_secrets:
            session_secrets[session_id] = {}
        session_secrets[session_id]["secret"] = secret
        return

    # Найдём вопрос от другого игрока
    other_session_id = None
    for role, sid in room_roles.get(room, {}).items():
        if sid != session_id:
            other_session_id = sid
            break

    if not other_session_id or other_session_id not in session_secrets:
        print("Нет второго игрока или нет данных")
        return

    last_question = session_secrets[other_session_id].get("last_question")
    if not last_question:
        print("Нет вопроса от второго игрока")
        return

    print("Последний вопрос:", last_question)
    print("Ответ:", answer)

    numbers = list(range(-100, 101))
    to_dim = []

    match = re.search(r"число\s*больше\s*(-?\d+)", last_question)
    if match:
        val = int(match.group(1))
        to_dim = [n for n in numbers if (answer == "да" and n <= val) or (answer == "нет" and n > val)]

    match = re.search(r"число\s*меньше\s*(-?\d+)", last_question)
    if match:
        val = int(match.group(1))
        to_dim = [n for n in numbers if (answer == "да" and n >= val) or (answer == "нет" and n < val)]

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



