import os

class Config:
    # Path to your downloaded Vosk model folder
    MODEL_PATH = "model" 
    SAMPLE_RATE = 16000
    DB_PATH = os.path.join("database", "logs.db")
    
    ASSISTANT_NAME = "Umair's Assistant"

    # Fixes for words the AI frequently mishears
    # Key = The CORRECT intent/app, Value = What the AI actually hears
    APP_ALIASES = {
        "youtube": ["you do", "u tube", "you tube"],
        "whatsapp": ["whats app", "watsup", "what is up"],
        "spotify": ["sportify", "spot if i"],
        "chrome": ["google", "browser"]
    }

    # Security: Commands that will ALWAYS be blocked
    BLOCKED_COMMANDS = [
        "rm -rf", "format", "del /s", "system32", "mkfs", "reset pc"
    ]