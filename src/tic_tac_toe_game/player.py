class AIPlayer:
    def __init__(self, AI_algo, name="AI"):
        self.AI_algo = AI_algo
        self.name = name
        self.move = {}

    def ask_move(self, game):
        return self.AI_algo(game)
