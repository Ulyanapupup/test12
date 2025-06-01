// static/script_2_2.js
const socket = io();
const room = window.room;
const sessionId = window.session_id;

let myPlayer = null;
let myNumber = null;
let playersReady = {1: false, 2: false};

// Подключаемся к комнате
socket.emit('join_game_room_2_2', { room, session_id: sessionId });

// Обработка редиректа
socket.on('redirect_2_2', (data) => {
    window.location.href = data.url;
});

// Обновление информации об игроках
socket.on('players_updated_2_2', (data) => {
    playersReady = data.playersReady || {1: false, 2: false};
    if (data.myPlayer) {
        myPlayer = data.myPlayer;
    }
    updateUI();
});

// Обновление интерфейса
function updateUI() {
    const player1Btn = document.getElementById('player-1');
    const player2Btn = document.getElementById('player-2');
    const numberSelection = document.getElementById('number-selection');
    const confirmBtn = document.getElementById('confirm-number');
    const startBtn = document.getElementById('start-game');
    const statusMessage = document.getElementById('status-message');

    // Обновляем кнопки выбора игрока
    player1Btn.classList.toggle('selected', myPlayer === 1);
    player2Btn.classList.toggle('selected', myPlayer === 2);
    
    // Блокируем кнопки, если игрок уже выбран другим участником
    player1Btn.disabled = playersReady[1] && myPlayer !== 1;
    player2Btn.disabled = playersReady[2] && myPlayer !== 2;

    // Показываем поле для ввода числа, если игрок выбран
    if (myPlayer) {
        numberSelection.style.display = 'block';
        confirmBtn.disabled = !!myNumber;
    } else {
        numberSelection.style.display = 'none';
    }

    // Обновляем статусное сообщение
    let message = myPlayer ? `Вы - Игрок ${myPlayer}` : 'Выберите игрока';
    if (playersReady[1]) message += ' | Игрок 1 готов';
    if (playersReady[2]) message += ' | Игрок 2 готов';
    statusMessage.textContent = message;

    // Активируем кнопку "Играть", если оба игрока готовы
    startBtn.disabled = !(playersReady[1] && playersReady[2]);
}

// Выбор игрока
function choosePlayer(player) {
    if (myPlayer === player) return;
    socket.emit('select_player_2_2', { 
        room: room, 
        session_id: sessionId, 
        player: player 
    });
}

// Подтверждение числа
function confirmNumber() {
    const numberInput = document.getElementById('number-input');
    const number = parseInt(numberInput.value);
    
    if (isNaN(number) || number < -1000 || number > 1000) {
        alert('Пожалуйста, введите число от -1000 до 1000');
        return;
    }
    
    myNumber = number;
    socket.emit('confirm_number_2_2', {
        room: room,
        session_id: sessionId,
        player: myPlayer,
        number: number
    });
    
    // Блокируем поле ввода после подтверждения
    numberInput.disabled = true;
    document.getElementById('confirm-number').disabled = true;
}

// Начало игры
function startGame() {
    if (playersReady[1] && playersReady[2]) {
        socket.emit('start_game_2_2', { room });
    }
}

// Выход из игры
function leaveGame() {
    window.location.href = `/game?room=${room}`;
}

// Инициализация событий
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('player-1').addEventListener('click', () => choosePlayer(1));
    document.getElementById('player-2').addEventListener('click', () => choosePlayer(2));
    document.getElementById('confirm-number').addEventListener('click', confirmNumber);
    document.getElementById('start-game').addEventListener('click', startGame);
    document.getElementById('leave-game').addEventListener('click', leaveGame);
    
    // Обновляем UI при загрузке
    updateUI();
});

socket.on('connect_error', (error) => {
  console.error('Connection Error:', error);
});

socket.on('connect_timeout', (timeout) => {
  console.error('Connection Timeout:', timeout);
});

socket.on('reconnect_attempt', (attempt) => {
  console.log('Reconnect Attempt:', attempt);
});

socket.on('reconnect_error', (error) => {
  console.error('Reconnect Error:', error);
});