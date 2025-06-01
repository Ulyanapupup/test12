# game_logic/mode_2_2.py

class Game2_2:
    def __init__(self):
        self.secrets = {'player1': None, 'player2': None}
        self.current_player = 'player1'
        self.pending_checks = {'player1': None, 'player2': None}
        self.last_guesses = {'player1': None, 'player2': None}

    def set_secret(self, player, number):
        self.secrets[player] = number

    def handle_question(self, player, message):
        import re
        msg = message.lower()
        self.pending_checks[player] = None
        self.last_guesses[player] = None

        if m := re.search(r"(число\s*)?больше\s*(-?\d+)", msg):
            self.pending_checks[player] = {'type': '>', 'value': int(m.group(2))}
        elif m := re.search(r"(число\s*)?меньше\s*(-?\d+)", msg):
            self.pending_checks[player] = {'type': '<', 'value': int(m.group(2))}
        elif m := re.search(r"(это\s*число\s*|число\s*это\s*|равно\s*)?(-?\d+)", msg):
            self.last_guesses[player] = int(m.group(2))

        # Переключаем ход
        self.current_player = 'player2' if player == 'player1' else 'player1'
        return self.current_player

    def apply_answer(self, answering_player, answer):
        answer = answer.lower()
        asking_player = 'player2' if answering_player == 'player1' else 'player1'
        result = {}
        
        if self.pending_checks[asking_player]:
            t = self.pending_checks[asking_player]['type']
            v = self.pending_checks[asking_player]['value']
            
            if t == '>' and answer == 'да':
                result = {'dim': list(range(-1000, v + 1)), 'for_player': asking_player}
            elif t == '>' and answer == 'нет':
                result = {'dim': list(range(v + 1, 1001)), 'for_player': asking_player}
            elif t == '<' and answer == 'да':
                result = {'dim': list(range(v, 1001)), 'for_player': asking_player}
            elif t == '<' and answer == 'нет':
                result = {'dim': list(range(-1000, v)), 'for_player': asking_player}
                
        elif self.last_guesses[asking_player] is not None:
            correct = self.last_guesses[asking_player] == self.secrets[answering_player]
            result = {
                'guess': self.last_guesses[asking_player], 
                'correct': correct,
                'for_player': asking_player
            }
            
        # Переключаем ход обратно
        self.current_player = asking_player
        return result, self.current_player