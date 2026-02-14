import customtkinter as ctk
import threading
import sys
import time
import keyboard
import pystray
from PIL import Image
import os
import winsound # For beep feedback

# Import backend
from src.audio_engine import AudioEngine
from src.speech_engine import SpeechEngine
from src.nlp_engine import NLPEngine
from src.os_controller import OSController
from src.security import SecurityLayer
from src.db_manager import DBManager
from config import Config

# --- THEME ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue") 
COLOR_BG = "#050505"
COLOR_SIDEBAR = "#0F0F0F"
COLOR_ACCENT = "#FF3333"
COLOR_SLEEP = "#444444"

class DailyVoiceOS(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{Config.ASSISTANT_NAME}")
        self.geometry("1000x650")
        self.configure(fg_color=COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        self.lbl_title = ctk.CTkLabel(self.sidebar, text="UMAIR'S\nASSISTANT", 
                                      font=ctk.CTkFont(family="Consolas", size=24, weight="bold"),
                                      text_color=COLOR_ACCENT)
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(40, 20))

        self.lbl_status = ctk.CTkLabel(self.sidebar, text="● BOOTING...", 
                                       font=ctk.CTkFont(family="Consolas", size=12), text_color="orange")
        self.lbl_status.grid(row=1, column=0, padx=20, pady=(0, 30))

        # MODE INDICATOR
        self.lbl_mode = ctk.CTkButton(self.sidebar, text="WAITING...",
                                     font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
                                     height=50, fg_color="transparent", border_width=2,
                                     border_color="gray", text_color="gray",
                                     state="disabled")
        self.lbl_mode.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.lbl_hint = ctk.CTkLabel(self.sidebar, text="Say 'SYSTEM WAKE UP'", 
                                     font=ctk.CTkFont(family="Consolas", size=10), text_color="#555")
        self.lbl_hint.grid(row=3, column=0, padx=20, pady=5)

        # --- CONSOLE ---
        self.main_area = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        self.console = ctk.CTkTextbox(self.main_area, font=ctk.CTkFont(family="Consolas", size=14),
                                      fg_color="#0A0A0A", text_color="#Dcdcdc")
        self.console.grid(row=0, column=0, sticky="nsew")
        
        # --- STATE VARIABLES ---
        self.backend_loaded = False
        self.is_active = False # False = Sleep Mode, True = Obeying Commands
        self.keep_running = True
        self.tray_icon = None

        self.log("System", "Initializing. Please wait for model load...")
        threading.Thread(target=self._load_backend, daemon=True).start()

    def _load_backend(self):
        try:
            import pyttsx3
            self.audio = AudioEngine()
            self.speech = SpeechEngine()
            self.nlp = NLPEngine()
            self.controller = OSController()
            self.security = SecurityLayer()
            self.db = DBManager()
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', 150)
            
            # Hotkey fallback
            keyboard.add_hotkey('ctrl+alt+space', self.manual_wake)

            self.backend_loaded = True
            self.after(0, self._set_sleep_mode)
            
            # START THE EARS AUTOMATICALLY
            threading.Thread(target=self.always_listening_loop, daemon=True).start()

            welcome = f"{Config.ASSISTANT_NAME} is listening for Wake Word."
            self.tts.say(welcome)
            self.tts.runAndWait()

        except Exception as e:
            self.after(0, lambda: self.log("Error", str(e)))

    # --- LISTENING LOOP ---
    def always_listening_loop(self):
        stream = self.audio.get_stream()
        audio_queue = self.audio.get_queue()
        
        self.log("System", "Microphone Active. Waiting for 'System Wake Up'...")
        
        with stream:
            while self.keep_running:
                try:
                    data = audio_queue.get()
                    text = self.speech.process_audio(data)
                    
                    if text:
                        self.after(0, self.process_voice_input, text)
                        
                except Exception as e:
                    print(f"Error: {e}")

    def process_voice_input(self, text):
        intent, entity = self.nlp.extract_intent(text)

        # --- LOGIC GATE ---
        
        # 1. ALWAYS CHECK FOR WAKE WORD (Even if sleeping)
        if intent == "WAKE_UP":
            self.wake_up()
            return

        # 2. IF SLEEPING, IGNORE EVERYTHING ELSE
        if not self.is_active:
            # We ignore the command, maybe print to console only for debug
            # self.log("Ignored", text) 
            return

        # 3. IF ACTIVE, CHECK FOR SLEEP COMMAND
        if intent == "SLEEP":
            self.go_to_sleep()
            return
        
        # 4. CHECK FOR TERMINATE
        if intent == "TERMINATE":
            self.quit_app()
            return

        # 5. PROCESS NORMAL COMMANDS
        self.log("You", text)
        if intent != "UNKNOWN":
            self.log(Config.ASSISTANT_NAME, f"EXECUTING :: {intent}")
            self.controller.execute(intent, entity)
            winsound.Beep(800, 100) # Success Beep
        else:
            self.log("System", "Command not recognized.")

    # --- STATE SWITCHING ---
    def wake_up(self):
        if not self.is_active:
            self.is_active = True
            winsound.Beep(1000, 200)
            self.lbl_mode.configure(text="LISTENING", fg_color=COLOR_ACCENT, text_color="black")
            self.lbl_status.configure(text="● ONLINE", text_color=COLOR_ACCENT)
            self.log("System", ">> SYSTEM AWAKE <<")
            
            # Show Window if hidden
            self.show_window()
            
            # Speak feedback
            threading.Thread(target=lambda: self.tts.say("Online") or self.tts.runAndWait(), daemon=True).start()

    def go_to_sleep(self):
        if self.is_active:
            self.is_active = False
            winsound.Beep(400, 200)
            self.lbl_mode.configure(text="SLEEPING", fg_color="transparent", text_color="gray")
            self.lbl_status.configure(text="● STANDBY", text_color="gray")
            self.log("System", ">> SYSTEM SLEEPING <<")
            
            # Hide Window
            self.minimize_to_tray()

    def manual_wake(self):
        if self.is_active:
            self.go_to_sleep()
        else:
            self.wake_up()

    # --- UI HELPERS ---
    def _set_sleep_mode(self):
        self.lbl_mode.configure(state="normal", text="SLEEPING", border_color="gray", text_color="gray")
        self.lbl_status.configure(text="● STANDBY", text_color="gray")

    def log(self, source, message):
        self.console.configure(state="normal")
        ts = time.strftime("%H:%M")
        if source == "You":
            self.console.insert("end", f"\n[{ts}] >>> {message}\n")
        elif source == "System":
            self.console.insert("end", f"[{ts}] SYS: {message}\n")
        else:
            self.console.insert("end", f"            {message}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    # --- TRAY ---
    def minimize_to_tray(self):
        self.withdraw()
        image = Image.new('RGB', (64, 64), color=(255, 50, 50)) 
        menu = pystray.Menu(pystray.MenuItem('Show', self.show_window), pystray.MenuItem('Exit', self.quit_app))
        self.tray_icon = pystray.Icon("UmairOS", image, "Umair's Assistant", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self, icon=None, item=None):
        if self.tray_icon: self.tray_icon.stop()
        self.after(0, self.deiconify)

    def quit_app(self, icon=None, item=None):
        self.keep_running = False
        if self.tray_icon: self.tray_icon.stop()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = DailyVoiceOS()
    app.mainloop()