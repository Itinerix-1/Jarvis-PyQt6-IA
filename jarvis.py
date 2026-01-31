import sys
import random
import winsound
import subprocess
import requests
import win32com.client
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
import speech_recognition as sr

# === Applications disponibles ===
APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "discord": r"C:\Users\%USERNAME%\AppData\Local\Discord\Update.exe --processStart Discord.exe",
    "calculatrice": "calc.exe",
    "notepad": "notepad.exe"
}

OLLAMA_API = "http://localhost:11434/api/chat"
MODEL = "llama3"

# === Synthèse vocale naturelle ===
speaker = win32com.client.Dispatch("SAPI.SpVoice")

# Choisir une voix moins robotique (ex: Hortense / David)
for v in speaker.GetVoices():
    if "Hortense" in v.GetDescription() or "David" in v.GetDescription():
        speaker.Voice = v
        break

speaker.Rate = 0    # vitesse normale
speaker.Volume = 90 # volume 0-100

def speak(text):
    phrases = text.replace('!', '.').replace('?', '.').split('.')
    for phrase in phrases:
        phrase = phrase.strip()
        if phrase:
            prefix = random.choice(["Hmm… ", "D'accord, ", "Ah oui, ", "Très bien, "])
            speaker.Speak(prefix + phrase)

def stop_speaking():
    try:
        speaker.Speak("")
    except:
        pass

# === Thread reconnaissance vocale ===
class VoiceThread(QThread):
    heard = pyqtSignal(str)
    def run(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, 0.5)
            while True:
                audio = r.listen(source)
                try:
                    text = r.recognize_google(audio, language="fr-FR").lower()
                    print("🎙️", text)
                    self.heard.emit(text)
                except:
                    pass

# === Logo Jarvis futuriste amélioré ===
class JarvisLogo(QWidget):
    def __init__(self):
        super().__init__()
        self.active = False
        self.radius1 = 28.0
        self.radius2 = 20.0
        self.grow1 = True
        self.grow2 = False

        # Fenêtre flottante top-left
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setFixedSize(100, 100)
        self.move(10, 10)

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def animate(self):
        if self.active:
            # cercle principal
            self.radius1 += 0.5 if self.grow1 else -0.5
            if self.radius1 > 36: self.grow1 = False
            if self.radius1 < 28: self.grow1 = True
            # cercle secondaire
            self.radius2 += 0.3 if self.grow2 else -0.3
            if self.radius2 > 32: self.grow2 = False
            if self.radius2 < 20: self.grow2 = True
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        # Cercle glow secondaire
        if self.active:
            p.setBrush(QColor(0, 255, 180, 80))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(int(50 - self.radius2), int(50 - self.radius2), int(self.radius2*2), int(self.radius2*2))
            # Cercle glow principal
            p.setBrush(QColor(0, 255, 0, 100))
            p.drawEllipse(int(50 - self.radius1), int(50 - self.radius1), int(self.radius1*2), int(self.radius1*2))

        # Cercle central
        p.setBrush(QColor(0, 200, 0) if self.active else QColor(180, 0, 0))
        p.setPen(QColor(0, 255, 0) if self.active else QColor(255, 0, 0))
        p.setPen(Qt.PenStyle.SolidLine)
        p.drawEllipse(40, 40, 20, 20)

        # Texte HUD futuriste
        if self.active:
            p.setPen(QColor(0, 255, 0, 200))
            p.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            p.drawText(5, 90, "Jarvis")

    def on(self):
        if not self.active:
            self.active = True
            winsound.Beep(1200, 200)
            speak("Bonjour, Jarvis activé")

    def off(self):
        if self.active:
            self.active = False
            winsound.Beep(600, 150)
            speak("Jarvis désactivé")

# === Lancer application ===
def launch_app(name):
    if name in APPS:
        phrases_app = [
            f"Ok, je lance {name} !",
            f"Très bien, ouverture de {name}.",
            f"Hum… {name} démarre maintenant !"
        ]
        speak(random.choice(phrases_app))
        subprocess.Popen(APPS[name], shell=True)
        print("🚀 Lancement :", name)

# === Interroger Ollama ===
def ask_ollama(prompt: str):
    try:
        data = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "stream": False}
        response = requests.post(OLLAMA_API, json=data, timeout=10)
        return response.json()["message"]["content"]
    except:
        return "Hum… je n'ai pas pu contacter l'IA."

# === Main ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    logo = JarvisLogo()
    logo.show()

    def handle(text):
        text = text.lower()
        print(f"🎙️ {text}")

        # Arrêt parole
        if any(word in text for word in ["ta gueule", "arrête de parler", "tais-toi", "stop jarvis"]):
            stop_speaking()
            print("🛑 Jarvis interrompu")
            return

        # Activation / désactivation
        if "ok jarvis" in text:
            logo.on()
            return
        if "merci jarvis" in text:
            logo.off()
            return

        # Commandes si actif
        if logo.active and text.startswith("jarvis"):
            command = text[7:].strip()

            for app_name in APPS:
                if app_name in command:
                    launch_app(app_name)
                    return

            if command:
                print("Envoi à Ollama :", command)
                response = ask_ollama(command)
                print("🤖 Jarvis:", response)
                speak(response)

    voice = VoiceThread()
    voice.heard.connect(handle)
    voice.start()

    sys.exit(app.exec())
