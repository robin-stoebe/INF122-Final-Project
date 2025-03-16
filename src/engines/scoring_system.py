class ScoringSystem:
    """Handles scoring for different games"""
    def __init__(self, scoring_rules=None):
        """
        scoring_rules: Dictionary where keys are event types (e.g., "line_clear"),
        and values are points awarded.
        """
        self.score = 0
        self.scoring_rules = scoring_rules if scoring_rules else {}

    def add_score(self, event_type, count=1):
        """Updates score based on an event"""
        if event_type in self.scoring_rules:
            self.score += self.scoring_rules[event_type] * count

    def get_score(self):
        """Returns the current score"""
        return self.score

    def reset_score(self):
        """Resets the score to zero"""
        self.score = 0