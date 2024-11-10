import json


# TODO: переделать
class StateManager:
    def __init__(self):
        self.state = {'Films': {},
                      'Janres': {},
                      'Persons': {}}
        self.listeners = []

    @state.setter
    def change_state(self, state):
        if state != self.state:
            self.state = state
            self.notify()

    def add_listener(self, listener):
        ...

    def notify(self):
        for listener in self.listeners:
            listener(self.state)

manager = StateManager()
def


class StateManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.state = self.load_state()

    def load_state(self):
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_state(self, key, value):
        self.state[key] = value
        with open(self.file_path, "w") as file:
            json.dump(self.state, file)

    def get_state(self, key, default=None):
        return self.state.get(key, default)
