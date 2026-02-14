# 🎙️ Umair's Assistant (Offline Voice OS Controller)

**Umair's Assistant** is a fully offline, privacy-focused voice assistant built in Python. It allows you to control your Windows/Linux laptop, launch applications, create files, and automate tasks using voice commands—without sending any data to the cloud.

## 🚀 Key Features

* **100% Offline:** Uses the **Vosk** neural network for speech recognition. No internet required.
* **Privacy First:** Your voice data never leaves your device.
* **Smart App Launching:** Automatically scans your system for installed apps (e.g., "Open WhatsApp", "Open VS Code").
* **System Control:** Create files/folders, search the web, and control system functions.
* **Modern GUI:** A sleek, dark-themed interface built with `CustomTkinter`.
* **Always-Listening Mode:** Runs in the background with a Wake Word ("System Wake Up").
* **Security Layer:** Blocks dangerous commands (like `rm -rf` or `format`) to prevent accidental damage.

## 🛠️ Tech Stack

* **Language:** Python 3.9+
* **Speech-to-Text:** Vosk (Offline Model)
* **Text-to-Speech:** pyttsx3
* **GUI:** CustomTkinter
* **Audio:** SoundDevice & NumPy
* **NLP:** Regex & Fuzzy Matching (TheFuzz)

---

## 📥 Installation

### 1. Clone the Repository

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the AI Model
This project requires a Vosk Model to work.
Go to alphacephei.com/vosk/models.
Download vosk-model-small-en-us-0.15 (Lightweight, fast) OR vosk-model-en-us-0.22 (More accurate, 1GB+).
Extract the zip file.
Rename the extracted folder to model.
Place the model folder inside the root directory of this project.


**Running the Assistant**

```bash
python main.py
```
Note: The first launch may take 30-60 seconds if you are using the large model.

**Voice Commands:**
1."System Wake Up"	Activates the assistant from Sleep Mode.
2."Go to Sleep"	Mutes the mic and minimizes to tray.
3."Open [App Name]"	Launches any app (e.g., "Open Chrome", "Open Calculator").
4."Create file [Name]"	Creates a file on your Desktop (e.g., "Create file notes").
5."Search for [Query]"	Googles the topic (e.g., "Search for Python tutorials").
6."Terminate System"	Completely closes the application.

**Safety & Privacy**
This assistant is designed with a Security Layer that intercepts commands before execution. It explicitly blocks destructive commands like file deletion or formatting drives.
