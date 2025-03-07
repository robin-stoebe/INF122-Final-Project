class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]

    def add_tile(self, tile, x, y):
        """Places tile on the board at (x, y)"""    
        if (0 <= x < self.width and 0 <= y < self.height):
            self.grid[y][x] = tile

    def remove_tile(self, x, y):
        """Removes tile from (x, y)"""
        if (0 <= x < self.width and 0 <= y < self.height):
            self.grid[y][x] = None

    def check_collision(self, x, y):
        """Checks if tile exists at (x, y)"""
        return not (0 <= x < self.width and 0 <= y < self.height) or self.grid[y][x] is not None

    def display(self):
        """Prints text-based board"""
        for row in self.grid:
            print("".join(tile.symbol if tile else "." for tile in row))
        print("\n")