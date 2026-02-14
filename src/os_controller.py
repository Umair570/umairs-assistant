import os
import subprocess
import platform
import webbrowser
import threading
from thefuzz import process

class OSController:
    def __init__(self):
        self.os_type = platform.system()
        self.app_cache = {} # Memory for app paths
        
        # Scan apps in background immediately when starting
        threading.Thread(target=self._build_app_cache, daemon=True).start()

    def _build_app_cache(self):
        """Scans the Windows Start Menu to find all installed apps."""
        print(">> [System] Indexing Start Menu shortcuts...")
        if self.os_type == "Windows":
            paths = [
                os.path.join(os.environ["PROGRAMDATA"], "Microsoft", "Windows", "Start Menu"),
                os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu")
            ]
            for path in paths:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(".lnk"):
                            # Clean the name: "Google Chrome.lnk" -> "google chrome"
                            name = file.lower().replace(".lnk", "")
                            self.app_cache[name] = os.path.join(root, file)
            print(f">> [System] Indexing complete. Found {len(self.app_cache)} apps.")

    def execute(self, intent, entity):
        try:
            if intent == "OPEN_APP":
                self._open_generic(entity)
            elif intent == "WEB_SEARCH":
                self._web_search(entity)
            elif intent == "CREATE_FOLDER":
                self._create_folder(entity)
            elif intent == "CREATE_FILE":
                self._create_file(entity)
            elif intent == "SYSTEM_CONTROL":
                print(">> [Safety] System control command blocked.")
            elif intent == "YOUTUBE":
                webbrowser.open("https://www.youtube.com")
            else:
                return "FAILED"
            return "SUCCESS"
        except Exception as e:
            print(f">> Execution Error: {e}")
            return "ERROR"

    def _open_generic(self, spoken_name):
        print(f">> Opening: {spoken_name}...")
        
        # 1. Check Cache (Fastest & Most Accurate)
        if self.app_cache:
            best_match = process.extractOne(spoken_name.lower(), self.app_cache.keys())
            if best_match and best_match[1] > 60: # 60% confidence
                real_name = best_match[0]
                path = self.app_cache[real_name]
                print(f">> Found cached app: {real_name}")
                os.startfile(path)
                return

        # 2. Fallback to Windows Run (for built-ins like 'notepad')
        try:
            subprocess.Popen(f"start {spoken_name}", shell=True)
        except:
            pass

    def _web_search(self, query):
        webbrowser.open(f"https://www.google.com/search?q={query}")

    def _create_folder(self, folder_name):
        try:
            # Create on Desktop
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            path = os.path.join(desktop, folder_name)
            os.makedirs(path, exist_ok=True)
            print(f">> Created folder: {path}")
            os.startfile(path) # Open it
        except:
            pass

    def _create_file(self, file_name):
        try:
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            if "." not in file_name: 
                file_name += ".txt"
            
            path = os.path.join(desktop, file_name)
            with open(path, 'w') as f:
                pass 
            print(f">> Created file: {path}")
            os.startfile(path) # Open it
        except Exception as e:
            print(f">> Error creating file: {e}")