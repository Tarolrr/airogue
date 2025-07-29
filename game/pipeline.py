
class Signal:
    def emit(self, *args, **kwargs):
        pass


class Action:
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.function = get_action_function(name)

    def execute(self):
        # Execute the corresponding function from slots.py
        self.function(**self.args)

