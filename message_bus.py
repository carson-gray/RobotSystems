class Bus:
    def __init__(self):
        self.message = None

    def write(self, msg):
        self.message = msg

    def read(self):
        return self.message
