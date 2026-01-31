# Jarvis-PyQt6-IA

Un assistant vocal futuriste inspiré de Jarvis avec **PyQt6**, reconnaissance vocale et voix naturelle SAPI5.  
Le petit logo flottant en haut à gauche de l’écran pulse avec un glow futuriste et indique si Jarvis est actif.

---

## Fonctionnalités

- **Logo flottant top-left** avec glow vert et texte HUD “Jarvis”
- **Reconnaissance vocale** via microphone (SpeechRecognition)
- **Réponses AI** via Ollama Llama3
- **Lancement d’applications Windows** par commandes vocales (`chrome`, `discord`, `notepad`, `calculatrice`)
- **Voix française naturelle** grâce à SAPI5
- **Commandes vocales pour activer/désactiver** Jarvis ou stopper la parole

---

## Dépendances

Assurez-vous d’avoir **Python 3.11+** installé.

Installez les modules nécessaires :

```bash
pip install pyqt6 speechrecognition pywin32 requests
