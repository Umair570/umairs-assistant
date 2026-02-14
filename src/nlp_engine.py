import re
from config import Config

class NLPEngine:
    def __init__(self):
        self.intents = {
            # --- VOICE CONTROL COMMANDS ---
            'WAKE_UP': [r"system wake up", r"wake up", r"initialize system", r"start listening"],
            'SLEEP': [r"go to sleep", r"stop listening", r"standby mode", r"mute microphone"],
            'TERMINATE': [r"terminate system", r"close assistant", r"exit program", r"shutdown assistant"],
            
            # --- STANDARD COMMANDS ---
            'OPEN_APP': [r"open (.*)", r"start (.*)", r"launch (.*)"],
            'WEB_SEARCH': [r"search for (.*)", r"google (.*)", r"look up (.*)"],
            'CREATE_FOLDER': [r"create (?:a )?folder (?:named )?(.*)", r"make directory (.*)"],
            'CREATE_FILE': [r"create (?:a )?file (?:named )?(.*)", r"make (?:a )?file (?:named )?(.*)"],
            'SYSTEM_CONTROL': [r"shutdown laptop", r"restart system"],
            'YOUTUBE': [r"open chrome and go to youtube", r"play youtube"]
        }

    def extract_intent(self, text):
        text = text.lower().strip()
        
        # 1. Check Config Aliases (Misheard words)
        for correct, misheard_list in Config.APP_ALIASES.items():
            if any(m in text for m in misheard_list):
                if correct == "youtube": return "YOUTUBE", None
                return "OPEN_APP", correct

        # 2. Check Regex Patterns
        for intent, patterns in self.intents.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    entity = match.group(1) if match.groups() else None
                    return intent, entity
        
        return "UNKNOWN", None

    def resolve_app_name(self, app_name):
        return app_name