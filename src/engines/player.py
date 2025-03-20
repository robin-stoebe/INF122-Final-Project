class Player:
    def __init__(self, name=""):
        self.name = name
        self.score = 0

    def updateScore(self, points):
        self.score += points

    def __repr__(self):
        return f"Player(name={self.name}, score={self.score})"