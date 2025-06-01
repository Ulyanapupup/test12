# game_logic/mode_2_2.py

class Game2_2:
    def __init__(self):
        self.pending_checks = {}  # {'creator': {'type': '>', 'value': 50}, 'guesser': {...}}
        self.last_guesses = {}    # {'creator': 42, 'guesser': 35}
        self.secrets = {}         # {'creator': None, 'guesser': None}
        self.dimmed_numbers = {'creator': set(), 'guesser': set()}

    def set_secret(self, role, number):
        self.secrets[role] = number

    def handle_question(self, role, message):
        import re
        msg = message.lower()
        self.pending_checks[role] = None
        self.last_guesses[role] = None

        if m := re.search(r"(число\s*)?больше\s*(-?\d+)", msg):
            self.pending_checks[role] = {'type': '>', 'value': int(m.group(2))}
        elif m := re.search(r"(число\s*)?меньше\s*(-?\d+)", msg):
            self.pending_checks[role] = {'type': '<', 'value': int(m.group(2))}
        elif m := re.search(r"(это\s*число\s*|число\s*это\s*|равно\s*)?(-?\d+)", msg):
            self.last_guesses[role] = int(m.group(2))

    def apply_answer(self, role, answer):
        answer = answer.lower()
        other_role = 'creator' if role == 'guesser' else 'guesser'
        
        if role in self.pending_checks and self.pending_checks[role]:
            t = self.pending_checks[role]['type']
            v = self.pending_checks[role]['value']
            
            if t == '>' and answer == 'да':
                self.dimmed_numbers[other_role].update(range(-1000, v + 1))
                return {'dim': list(range(-1000, v + 1)), 'target': other_role}
            elif t == '>' and answer == 'нет':
                self.dimmed_numbers[other_role].update(range(v + 1, 1001))
                return {'dim': list(range(v + 1, 1001)), 'target': other_role}
            elif t == '<' and answer == 'да':
                self.dimmed_numbers[other_role].update(range(v, 1001))
                return {'dim': list(range(v, 1001)), 'target': other_role}
            elif t == '<' and answer == 'нет':
                self.dimmed_numbers[other_role].update(range(-1000, v))
                return {'dim': list(range(-1000, v)), 'target': other_role}
                
        elif role in self.last_guesses and self.last_guesses[role] is not None:
            correct = self.last_guesses[role] == self.secrets.get(other_role)
            return {
                'guess': self.last_guesses[role], 
                'correct': correct,
                'target': other_role
            }
        return {}