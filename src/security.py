from config import Config

class SecurityLayer:
    @staticmethod
    def is_safe(text):
        for blocked in Config.BLOCKED_COMMANDS:
            if blocked in text.lower():
                return False
        return True

    @staticmethod
    def confirm_critical_action(action):
        """In a real GUI, this would pop up a dialog. Here we assume caution."""
        # For shutdown/restart, we could add a voice confirmation loop
        critical = ["shutdown", "restart", "delete"]
        if any(c in action for c in critical):
            return True # Flag that this is critical
        return False