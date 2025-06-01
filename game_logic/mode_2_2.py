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

    # Установка секретного числа
    if "secret" in data and "answer" not in data:
        session_secrets[session_id] = data["secret"]
        return

    # Обработка логического ответа (да/нет)
    if "answer" in data:
        answer = data["answer"].strip().lower()
        secret = session_secrets.get(session_id)
        if secret is None:
            return

        # Попытка восстановить вопрос из чата
        # Пример: последний вопрос был "Число больше 20?", пользователь отвечает "да"
        # Ты можешь хранить последнее сообщение соперника для более точной логики,
        # но здесь сделаем простую эвристику
        # В дальнейшем можно улучшить логику с контекстом чата

        # Пример (если последнее сообщение известно и было сохранено в session)
        # Здесь просто для примера жестко заданы шаблоны

        # Это пример на будущее — пока просто покажем как можно отфильтровать

        # Пример — если бы вопрос был "Число больше 50?"
        # и ответ "да", значит убираем все ≤ 50

        # Простой парсинг — лучше привязать к предыдущему сообщению, а не к ответу
        # можно позже передавать в reply последний вопрос
        pass  # Сейчас основная логика в guess_logic — ответ только показывает "да/нет"

