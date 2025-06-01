// static/script_2_2.js
const socket = io();
const room = window.room;
const sessionId = window.session_id;

let myRole = null;
let currentRoles = { guesser: null, creator: null };

// Подключение к комнате
socket.emit('join_game_room_2_2', { room, session_id: sessionId });

socket.on('redirect_2_2', (data) => {
    console.log('Redirecting (2.2) to:', data.url);
    window.location.href = data.url;
});

socket.on('roles_updated_2_2', (data) => {
    console.log('Получены обновленные роли:', data);
    currentRoles = data.roles || { guesser: null, creator: null };
    myRole = null;
    for (const [role, sid] of Object.entries(currentRoles)) {
        if (sid === sessionId) {
            myRole = role;
            break;
        }
    }
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
    return role === 'guesser' ? 'Угадывающий' : 'Загадывающий';
}

function chooseRole(role) {
    if (myRole === role) return;
    socket.emit('select_role_2_2', { 
        room: room, 
        session_id: sessionId, 
        role: role 
    });
}

function canStartGame() {
    return currentRoles.guesser && 
           currentRoles.creator && 
           currentRoles.guesser !== currentRoles.creator;
}

function updateUI() {
    const guesserBtn = document.getElementById('role-guesser');
    const creatorBtn = document.getElementById('role-creator');
    const startBtn = document.getElementById('start-game');
    
    guesserBtn.classList.toggle('selected', myRole === 'guesser');
    creatorBtn.classList.toggle('selected', myRole === 'creator');
    guesserBtn.disabled = !!currentRoles.guesser && currentRoles.guesser !== sessionId;
    creatorBtn.disabled = !!currentRoles.creator && currentRoles.creator !== sessionId;
    
    let statusMessage = myRole ? `Ваша роль: ${getRoleName(myRole)}` : 'Выберите роль';
    if (currentRoles.guesser && currentRoles.guesser !== sessionId) {
        statusMessage += ` | Угадывающий: другой игрок`;
    }
    if (currentRoles.creator && currentRoles.creator !== sessionId) {
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
    document.getElementById('role-guesser').addEventListener('click', () => chooseRole('guesser'));
    document.getElementById('role-creator').addEventListener('click', () => chooseRole('creator'));
    document.getElementById('start-game').addEventListener('click', startGame);
    document.getElementById('leave-game').addEventListener('click', leaveGame);
});