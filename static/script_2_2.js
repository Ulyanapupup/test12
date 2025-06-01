// static/script_2_2.js
const socket = io();
const room = window.room;
const sessionId = window.session_id;

let myRole = null;
let currentRoles = { player1: null, player2: null };

// Подключение к комнате
socket.emit('join_game_room_2_2', { room, session_id: sessionId });

socket.on('redirect_2_2', (data) => {
    console.log('Redirecting (2.2) to:', data.url);
    window.location.href = data.url;
});

socket.on('roles_updated_2_2', (data) => {
    console.log('Получены обновленные роли:', data);
    currentRoles = data.roles || { player1: null, player2: null };
	secrets = data.secrets || { player1: null, player2: null };
    myRole = null;
    for (const [role, sid] of Object.entries(currentRoles)) {
        if (sid === sessionId) {
            myRole = role;
            break;
        }
    }
    updateUI();
});

socket.on('secret_set', (data) => {
    secrets[data.role] = data.secret;
    updateUI();
});

socket.on('role_taken_2_2', (data) => {
    alert(`Роль "${getRoleName(data.role)}" уже занята другим игроком!`);
});

socket.on('player_left', () => {
    alert('Другой игрок покинул игру. Вы будете перенаправлены в комнату.');
    window.location.href = `/game?room=${room}`;
});

// Вспомогательные функции
function getRoleName(role) {
    return role === 'player1' ? 'Игрок 1' : 'Игрок 2';
}

function chooseRole(role) {
    if (myRole === role) return;
    socket.emit('select_role_2_2', { 
        room: room, 
        session_id: sessionId, 
        role: role 
    });
    // Показать поле для ввода числа
    document.getElementById('number-input').style.display = 'block';
}

function setSecretNumber() {
    const num = parseInt(document.getElementById('secret-number').value);
    if (num >= -1000 && num <= 1000) {
        socket.emit('set_secret_2_2', {
            room: room,
            session_id: sessionId,
            secret: num
        });
        document.getElementById('secret-status').textContent = `Вы загадали: ${num}`;
    } else {
        alert("Число должно быть от -1000 до 1000");
    }
}

function canStartGame() {
    return currentRoles.player1 && 
           currentRoles.player2 && 
           currentRoles.player1 !== currentRoles.player2 &&
		   secrets.player1 && 
           secrets.player2;
}

function updateUI() {
    const player1Btn = document.getElementById('role-player1');
    const player2Btn = document.getElementById('role-player2');
    const startBtn = document.getElementById('start-game');
    
    player1Btn.classList.toggle('selected', myRole === 'player1');
    player2Btn.classList.toggle('selected', myRole === 'player2');
    player1Btn.disabled = !!currentRoles.player1 && currentRoles.player1 !== sessionId;
    player2Btn.disabled = !!currentRoles.player2 && currentRoles.player2 !== sessionId;
    
    let statusMessage = myRole ? `Ваша роль: ${getRoleName(myRole)}` : 'Выберите роль';
    if (currentRoles.player1 && currentRoles.player1 !== sessionId) {
        statusMessage += ` | Угадывающий: другой игрок`;
    }
    if (currentRoles.player2 && currentRoles.player2 !== sessionId) {
        statusMessage += ` | Загадывающий: другой игрок`;
    }
    document.getElementById('status-message').textContent = statusMessage;
    startBtn.disabled = !canStartGame();
}

function startGame() {
    if (canStartGame()) {
        console.log('Attempting to start 2.2 game in room:', room);
        
        socket.emit('start_game_2_2', { room }, (response) => {
            if (response && response.status === 'ok') {
                console.log('2.2 Game started successfully, waiting for redirect...');
                // Здесь не нужно делать ничего, сервер сам отправит redirect_2_2
            } else {
                console.error('Start error:', response?.message || 'Unknown error');
                alert(response?.message || 'Ошибка запуска игры');
            }
        });
    } else {
        alert('Необходимо чтобы один игрок был Угадывающим, а другой - Загадывающим!');
    }
}

function leaveGame() {
    if (confirm('Вы уверены, что хотите покинуть игру?')) {
        socket.emit('leave_game_2_2', { room, session_id: sessionId });
        window.location.href = `/game?room=${room}`;
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('role-player1').addEventListener('click', () => chooseRole('player1'));
    document.getElementById('role-player2').addEventListener('click', () => chooseRole('player2'));
    document.getElementById('start-game').addEventListener('click', startGame);
    document.getElementById('leave-game').addEventListener('click', leaveGame);
});