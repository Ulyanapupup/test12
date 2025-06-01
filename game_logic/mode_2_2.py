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
    
    session_secrets[session_id] = session_secrets.get(session_id, {})
    session_secrets[session_id]["last_question"] = message

    numbers = list(range(-100, 101))
    
    # Сохраняем последний вопрос независимо от роли
    if session_id not in session_secrets:
        session_secrets[session_id] = {}

    session_secrets[session_id]["last_question"] = message


    # Разбор вопроса
    match = re.search(r"число\s*(?:равно|это)\s*(-?\d+)", message)
    if match:
        guess = int(match.group(1))
        emit("guess_result_2_2", {
            "target": "creator",
            "value": guess,
            "correct": session_secrets.get(session_id) == guess
        }, room=room)
        emit("guess_result_2_2", {
            "target": "guesser",
            "value": guess,
            "correct": session_secrets.get(session_id) == guess
        }, room=room)
        return

    match = re.search(r"число\s*больше\s*(-?\d+)", message)
    if match:
        val = int(match.group(1))
        to_dim = [n for n in numbers if n <= val]
        emit("filter_numbers_2_2", {
            "target": "guesser",
            "dim": to_dim
        }, room=room)
        return

    match = re.search(r"число\s*меньше\s*(-?\d+)", message)
    if match:
        val = int(match.group(1))
        to_dim = [n for n in numbers if n >= val]
        emit("filter_numbers_2_2", {
            "target": "guesser",
            "dim": to_dim
        }, room=room)
        return

def handle_reply(data):
    room = data["room"]
    session_id = data["session_id"]
    answer = data.get("answer", "").strip().lower()
    secret = data.get("secret")

    if secret is not None:
        session_secrets[session_id] = {"secret": secret}
        return

    if "answer" in data:
        if session_id not in session_secrets or "last_question" not in session_secrets[session_id]:
            return

        question = session_secrets[session_id]["last_question"]
        numbers = list(range(-100, 101))
        to_dim = []

        # Пример: "число больше 50?" и ответ "да"
        match = re.search(r"число\s*больше\s*(-?\d+)", question)
        if match:
            val = int(match.group(1))
            if answer == "да":
                to_dim = [n for n in numbers if n <= val]
            elif answer == "нет":
                to_dim = [n for n in numbers if n > val]

        match = re.search(r"число\s*меньше\s*(-?\d+)", question)
        if match:
            val = int(match.group(1))
            if answer == "да":
                to_dim = [n for n in numbers if n >= val]
            elif answer == "нет":
                to_dim = [n for n in numbers if n < val]

        if to_dim:
            # Отправляем обоим игрокам
            emit("filter_numbers_2_2", {
                "target": "guesser",
                "dim": to_dim
            }, room=room)
            emit("filter_numbers_2_2", {
                "target": "creator",
                "dim": to_dim
            }, room=room)


