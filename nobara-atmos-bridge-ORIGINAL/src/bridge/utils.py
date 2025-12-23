import os
import subprocess

class Utils:
    """Helper functions for system validation and path resolution."""

    @staticmethod
    def is_wine_installed():
        """Checks if Wine is present on the system path."""
        return subprocess.run(["which", "wine"], capture_output=True).returncode == 0

    @staticmethod
    def validate_path(path):
        """Checks if a file path exists and is readable."""
        expanded_path = os.path.expanduser(path)
        # Handle Windows-style paths if they are passed directly
        if "C:/" in expanded_path:
            # Simple validation: we assume if it has C:/, it's a Wine target
            return True
        return os.path.exists(expanded_path)

    @staticmethod
    def get_system_info():
        """Returns basic OS info for debugging/logs."""
        try:
            with open("/etc/os-release", "r") as f:
                return f.read()
        except:
            return "Linux (Generic)"
