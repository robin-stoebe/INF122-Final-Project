import json
import os

class ProfileManager:
    def __init__(self, filename="profiles.json"):
        self.filename = filename

        # if the path exists,
        # read the file and store the profiles
        # otherwise, we initialize an empty dictionary
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                self.profiles = json.load(file)
        else:
            self.profiles = {}

    def get_profile(self, username):
        # if the username exists, return it
        if username in self.profiles:
            return self.profiles[username]
        else:
            # Only keeping track of total score
            # If it doesn't exist, initialize with score of 0
            self.profiles[username] = {"score": 0}
            return self.profiles[username]

    def update_profile_score(self, username, score):
        # update score if the username exists
        if username in self.profiles:
            self.profiles[username]["score"] = score

    def save_profiles(self):
        # save the profiles to the file
        with open(self.filename, "w") as file:
            json.dump(self.profiles, file, indent=4)
