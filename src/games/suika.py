class SuikaGame(Game):
    def __init__(self, player1, player2):
        super().__init__(player1, player2)
        self.board = Board(10, 10)
        self.current_fruit = self.generateFruit()
        self.game_over = False
    
    def initializeBoard(self):
        print("Initializing Suika board...")
        self.board = Board(10, 20)
        self.current_fruit = self.generateFruit()
        self.game_over = False

    def update_board(self):
        if(self.game_over):
            return
        
        #fruit falling
        self._move_fruit_down()

        # collision and merge cheks
        self._check_collision()

        # Check for game over condition
        self._check_game_over()

    def gameLoop(self):
        print("Starting Suika game loop... (placeholder)")

    def _generateFruit(self):
        """Generate a random fruit to drop."""
        import random
        fruits = ["Cherry", "Strawberry", "Grape", "Orange", "Apple", "Pear", "Peach", "Pineapple", "Melon"]
        return random.choice(fruits)
