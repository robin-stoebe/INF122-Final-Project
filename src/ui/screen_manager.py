class ScreenManager:
    def __init__(self):
        self.screens = {}   # Store all screens
        self.current_screen = None  # The active screen

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def set_screen(self, name):
        """Switches to the new screen, terminating the last one."""
        if self.current_screen:
            self.current_screen.running = False  # Stop current screen loop

        self.current_screen = self.screens.get(name)
        if self.current_screen:
            self.current_screen.running = True  # Ensure new screen runs

    def run(self):
        while self.current_screen:
            self.current_screen.run()
