class Tile:
    """Represents a single tile in a tile-matching game"""
    def __init__(self, symbol: str, color: tuple, tile_type: str = "default"):
        """
        Initializes a tile
        :param symbol: String representing the tile (e.g. "O" for Tetris, "🍎" for Suika)
        :param color: RGB tuple representing tile color
        :param tile_type: Category for the tile (e.g. "fruit" for Suika, "block" for Tetris)
        """
        """
        This class in its current state does not fit in exactly with the way Suika is coded, so I will likely have to make a subclass specifically for Suika
        Probably something like this:

        class PhysicsTile(Tile):
            A tile with physics properties for Suika-like games
            def __init__(self, symbol, color, tile_type="fruit", radius=20):
                super().__init__(symbol, color, tile_type)
                self.radius = radius
                self.body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)  # Suika uses dynamic bodies
                self.shape = pymunk.Circle(self.body, self.radius)
        """

        self.symbol = symbol
        self.color = color
        self.tile_type = tile_type
        self.matched = False # Whether the tile has been matched (Mainly for Suika)

        def mark_matched(self):
            """Marks the tile as matched"""
            self.matched = True

        def __repr__(self):
            base_repr = f"Tile(symbol={self.symbol}, color={self.color}, type={self.tile_type})"
            return base_repr if self.tile_type == "block" else base_repr + f", matched={self.matched}"