import json
import os

class ConfigManager:
    def __init__(self, filename="bridge_config.json"):
        """
        Initializes the Config Manager.
        It looks for a config file in the same directory as this script.
        """
        # Determine the absolute path of the script to ensure the config stays with it
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_path, filename)

        # Initial load
        self.settings = self.load_from_disk()

    def load_from_disk(self):
        """
        Reads the JSON file from disk.
        If the file doesn't exist, it returns a set of default values.
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                print(f"ERROR: Could not read config file: {e}")
                return self.get_defaults()
        else:
            return self.get_defaults()

    def get_defaults(self):
        """Standard default settings for a new Nobara Atmos Bridge setup."""
        return {
            "prefix": "~/.wine",
            "path": "",
            "res": "1920x1080",
            "last_profile": "Standard"
        }

    def save(self):
        """Writes the current settings dictionary to the JSON file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"ERROR: Could not save config: {e}")

    def get(self, key, default=None):
        """Retrieves a specific setting value."""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Updates a setting and automatically saves it to disk."""
        self.settings[key] = value
        self.save()

    def get_all(self):
        """Returns the entire settings dictionary."""
        return self.settings
