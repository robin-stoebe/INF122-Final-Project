class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)] #Initializes grid

    def check_collision(self, x, y):
        """Checks if tile exists at (x, y)"""
        return not (0 <= x < self.width and 0 <= y < self.height) or self.grid[y][x] is not None

    def display(self): # This should probably change when the UI is implemented
        """Prints text-based board"""
        for row in self.grid:
            print("".join(tile.symbol if tile else "." for tile in row))
        print("\n")