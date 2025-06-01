from flask_socketio import emit, join_room
import re

# Храним данные для каждой сессии: {'session_id': {'secret': число, 'last_question': текст}}
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
    
    # Инициализация данных сессии если нужно
    if session_id not in session_data:
        session_data[session_id] = {}
    
    # Сохраняем последний вопрос
    session_data[session_id]["last_question"] = message

    # Обработка прямого предположения числа
    if match := re.search(r"число\s*(?:равно|это)\s*(-?\d+)", message):
        guess = int(match.group(1))
        secret = session_data.get(session_id, {}).get("secret")
        
        emit("guess_result_2_2", {
            "target": "opponent",  # Отправляем результат противоположному игроку
            "value": guess,
            "correct": secret == guess
        }, room=room)
        return

    # Для вопросов "больше/меньше" сохраняем вопрос
    if match := re.search(r"число\s*больше\s*(-?\d+)", message):
        session_data[session_id]["pending_question"] = {
            'type': '>', 
            'value': int(match.group(1))
        }
        return

    elif match := re.search(r"число\s*меньше\s*(-?\d+)", message):
        session_data[session_id]["pending_question"] = {
            'type': '<', 
            'value': int(match.group(1))
        }
        return

def handle_reply(data):
    room = data["room"]
    session_id = data["session_id"]
    
    # Установка секретного числа
    if "secret" in data:
        set_secret(data)
        return

    # Обработка ответа на вопрос
    if "answer" in data and "pending_question" in session_data.get(session_id, {}):
        answer = data["answer"].strip().lower()
        question = session_data[session_id]["pending_question"]
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
            "target": "sender",  # Фильтруем числа у отправителя вопроса
            "dim": to_dim
        }, room=room)
        del session_data[session_id]["pending_question"]