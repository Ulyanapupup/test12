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

    if match := re.search(r"число\s*больше\s*(-?\d+)", message):
        session_secrets[session_id]["pending_question"] = {
            'type': '>', 
            'value': int(match.group(1))
        }
        # Не фильтруем сразу, только сохраняем вопрос
        return

    elif match := re.search(r"число\s*меньше\s*(-?\d+)", message):
        session_secrets[session_id]["pending_question"] = {
            'type': '<', 
            'value': int(match.group(1))
        }
        # Не фильтруем сразу, только сохраняем вопрос
        return

def handle_reply(data):
    room = data["room"]
    session_id = data["session_id"]

    # Установка секретного числа
    if "secret" in data and "answer" not in data:
        session_secrets[session_id] = data["secret"]
        return

    # Обработка логического ответа (да/нет)
    if "answer" in data:
        answer = data["answer"].strip().lower()
        secret = session_secrets.get(session_id)
        if not secret or "pending_question" not in session_secrets[session_id]:
            return
            
        question = session_secrets[session_id]["pending_question"]
        numbers = list(range(-100, 101))
        
        if question['type'] == '>':
            if answer == 'да':
                to_dim = [n for n in numbers if n <= question['value']]
            else:
                to_dim = [n for n in numbers if n > question['value']]
        elif question['type'] == '<':
            if answer == 'да':
                to_dim = [n for n in numbers if n >= question['value']]
            else:
                to_dim = [n for n in numbers if n < question['value']]
        
        emit("filter_numbers_2_2", {
            "target": "guesser",
            "dim": to_dim
        }, room=room)
        del session_secrets[session_id]["pending_question"]

