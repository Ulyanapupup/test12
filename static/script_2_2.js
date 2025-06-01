// static/script_2_2.js
const socket = io();
const room = window.room;
const sessionId = window.session_id;

let myPlayer = null;
let myNumber = null;
let playersReady = {1: false, 2: false};
let currentTurn = 1;

socket.emit('join_game_room_2_2', { room, session_id: sessionId });

socket.on('redirect_2_2', (data) => {
    window.location.href = data.url;
});

socket.on('players_updated_2_2', (data) => {
    playersReady = data.playersReady || {1: false, 2: false};
    myPlayer = data.myPlayer;
    updateUI();
});

socket.on('game_started_2_2', () => {
    window.location.href = `/game2/player?room=${room}&player=${myPlayer}`;
});

function choosePlayer(player) {
    if (myPlayer === player) return;
    socket.emit('select_player_2_2', { 
        room: room, 
        session_id: sessionId, 
        player: player 
    });
}

function confirmNumber() {
    const number = parseInt(document.getElementById('number-input').value);
    if (isNaN(number) || number < -1000 || number > 1000) {
        alert('Введите число от -1000 до 1000');
        return;
    }
    myNumber = number;
    socket.emit('confirm_number_2_2', {
        room: room,
        session_id: sessionId,
        player: myPlayer,
        number: number
    });
}

function canStartGame() {
    return playersReady[1] && playersReady[2];
}

function updateUI() {
    const player1Btn = document.getElementById('player-1');
    const player2Btn = document.getElementById('player-2');
    const numberSelection = document.getElementById('number-selection');
    const startBtn = document.getElementById('start-game');
    
    player1Btn.classList.toggle('selected', myPlayer === 1);
    player2Btn.classList.toggle('selected', myPlayer === 2);
    player1Btn.disabled = playersReady[1] && myPlayer !== 1;
    player2Btn.disabled = playersReady[2] && myPlayer !== 2;
    
    if (myPlayer) {
        numberSelection.style.display = 'block';
        document.getElementById('confirm-number').disabled = !!myNumber;
    } else {
        numberSelection.style.display = 'none';
    }
    
    let statusMessage = myPlayer ? `Вы - Игрок ${myPlayer}` : 'Выберите игрока';
    if (playersReady[1]) statusMessage += ' | Игрок 1 готов';
    if (playersReady[2]) statusMessage += ' | Игрок 2 готов';
    
    document.getElementById('status-message').textContent = statusMessage;
    startBtn.disabled = !canStartGame();
}

function startGame() {
    if (canStartGame()) {
        socket.emit('start_game_2_2', { room });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('player-1').addEventListener('click', () => choosePlayer(1));
    document.getElementById('player-2').addEventListener('click', () => choosePlayer(2));
    document.getElementById('start-game').addEventListener('click', startGame);
    document.getElementById('leave-game').addEventListener('click', () => {
        window.location.href = `/game?room=${room}`;
    });
});