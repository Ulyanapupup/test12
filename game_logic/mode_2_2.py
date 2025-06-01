# game_logic/mode_2_2.py

class Game2_2:
    def __init__(self):
        self.pending_checks = {'creator': None, 'guesser': None}
        self.last_guesses = {'creator': None, 'guesser': None}
        self.secrets = {'creator': None, 'guesser': None}
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
                dimmed = list(range(-100, v + 1))
                self.dimmed_numbers[other_role].update(dimmed)
                return {'dim': dimmed, 'target': other_role}
            elif t == '>' and answer == 'нет':
                dimmed = list(range(v + 1, 101))
                self.dimmed_numbers[other_role].update(dimmed)
                return {'dim': dimmed, 'target': other_role}
            elif t == '<' and answer == 'да':
                dimmed = list(range(v, 101))
                self.dimmed_numbers[other_role].update(dimmed)
                return {'dim': dimmed, 'target': other_role}
            elif t == '<' and answer == 'нет':
                dimmed = list(range(-100, v))
                self.dimmed_numbers[other_role].update(dimmed)
                return {'dim': dimmed, 'target': other_role}
                
        elif role in self.last_guesses and self.last_guesses[role] is not None:
            correct = self.last_guesses[role] == self.secrets.get(other_role)
            return {
                'guess': self.last_guesses[role], 
                'correct': correct,
                'target': other_role
            }
        return {}