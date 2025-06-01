// static/script_2_2.js
const socket = io();
const room = window.room;
const sessionId = window.session_id;

let myRole = null;
let currentRoles = {};
let secrets = { player1: null, player2: null };

// Подключение к комнате
socket.emit('join_game_room_2_2', { room, session_id: sessionId });

socket.on('redirect_2_2', (data) => {
    console.log('Redirecting (2.2) to:', data.url);
    window.location.href = data.url;
});

socket.on('roles_updated_2_2', (data) => {
    console.log('Получены обновленные роли:', data);
    currentRoles = data.roles || {};
    myRole = data.your_role || null;
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

socket.on('enable_start_button', () => {
    updateUI(); // Это активирует кнопку, если условия выполнены
});

// Вспомогательные функции
function getRoleName(role) {
    return role === 'player1' ? 'Игрок 1' : 'Игрок 2';
}

function chooseRole(role) {
    if (myRole === role) return;
    
    const button = document.getElementById(`role-${role}`);
    button.disabled = true;
    button.textContent = 'Выбираем...';
    
    socket.emit('select_role_2_2', { 
        room: room, 
        session_id: sessionId, 
        role: role 
    }, (response) => {
        button.textContent = role === 'player1' ? 'Игрок 1' : 'Игрок 2';
        if (response && response.error) {
            alert(response.error);
            button.disabled = false;
        }
    });
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
    const players = Object.values(currentRoles);
    return players.includes('player1') && 
           players.includes('player2') &&
           secrets.player1 !== null && 
           secrets.player2 !== null;
}

function updateUI() {
    const player1Btn = document.getElementById('role-player1');
    const player2Btn = document.getElementById('role-player2');
    const startBtn = document.getElementById('start-game');
    
    if (player1Btn && player2Btn) {
        player1Btn.classList.toggle('selected', myRole === 'player1');
        player2Btn.classList.toggle('selected', myRole === 'player2');
        player1Btn.disabled = !!currentRoles.player1 && currentRoles.player1 !== sessionId;
        player2Btn.disabled = !!currentRoles.player2 && currentRoles.player2 !== sessionId;
    }
    
    let statusMessage = myRole ? `Ваша роль: ${getRoleName(myRole)}` : 'Выберите роль';
    if (currentRoles.player1 && currentRoles.player1 !== sessionId) {
        statusMessage += ` | Игрок 1: другой игрок`;
    }
    if (currentRoles.player2 && currentRoles.player2 !== sessionId) {
        statusMessage += ` | Игрок 2: другой игрок`;
    }
    
    const statusElement = document.getElementById('status-message');
    if (statusElement) {
        statusElement.textContent = statusMessage;
    }
    
    if (startBtn) {
        startBtn.disabled = !canStartGame();
        if (!startBtn.disabled) {
            startBtn.style.backgroundColor = '#4CAF50';
        } else {
            startBtn.style.backgroundColor = '#cccccc';
        }
    }
}

function startGame() {
    if (canStartGame()) {
		const issues = [];
		if (!currentRoles.player1 || !currentRoles.player2) issues.push("не все роли выбраны");
		if (currentRoles.player1 === currentRoles.player2) issues.push("роли должны быть разными");
		if (!secrets.player1 || !secrets.player2) issues.push("не все числа загаданы");
		
		alert(`Нельзя начать игру: ${issues.join(", ")}`);
		return;
	
        console.log('Attempting to start 2.2 game in room:', room);
        
        socket.emit('start_game_2_2', { room }, (response) => {
            if (response && response.status === 'ok') {
                console.log('2.2 Game started successfully, waiting for redirect...');
            } else {
                console.error('Start error:', response?.message || 'Unknown error');
                alert(response?.message || 'Ошибка запуска игры');
            }
        });
    } else {
        const missing = [];
        if (!currentRoles.player1 || !currentRoles.player2) missing.push("не выбраны роли");
        if (!secrets.player1 || !secrets.player2) missing.push("не загаданы числа");
        alert(`Нельзя начать игру: ${missing.join(" и ")}`);
    }
}

function leaveGame() {
    if (confirm('Вы уверены, что хотите покинуть игру?')) {
        socket.emit('leave_game', { room, session_id: sessionId });
        window.location.href = `/game?room=${room}`;
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('role-player1')?.addEventListener('click', () => chooseRole('player1'));
    document.getElementById('role-player2')?.addEventListener('click', () => chooseRole('player2'));
    document.getElementById('set-secret-btn')?.addEventListener('click', setSecretNumber);
    document.getElementById('start-game')?.addEventListener('click', startGame);
    document.getElementById('leave-game')?.addEventListener('click', leaveGame);
    
    // Инициализация UI
    updateUI();
});