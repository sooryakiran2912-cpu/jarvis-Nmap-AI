# JARVIS 🤖

> AI-powered voice & text assistant for Kali Linux, built on Groq's LLaMA 3.3

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Kali%20Linux-557C94)
![LLM](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

JARVIS is a terminal-based AI assistant for Kali Linux that pairs LLM reasoning (via Groq's LLaMA 3.3) with speech recognition and built-in security tooling. Control it with your voice or with plain text, and trigger network scans directly through conversation.

## Features

- 🎙️ **Voice Mode** — wake-word activated ("JARVIS"), hands-free command input
- ⌨️ **Text Mode** — type commands directly when voice isn't convenient
- 🧠 **LLM-Powered Reasoning** — Groq-hosted LLaMA 3.3 for natural conversation and command interpretation
- 🎯 **Voice Training** — calibrate recognition to your voice
- 🔊 **Auto Noise Calibration** — detects ambient noise and sets an energy threshold on startup
- 🛰️ **Nmap Integration** — run network scans via `nmap_scanner.py`
- 🐧 **Built for Kali Linux** — tested against Kali's default PulseAudio/ALSA stack

## Demo

```
==================================================
      ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
      ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
      ██║███████║██████╔╝██║   ██║██║███████╗
 ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
 ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
  ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
==================================================
  Powered by Groq LLaMA 3.3 | Kali Linux
==================================================

📋 Available Microphones:
   [0] Intel 82801AA-ICH: - (hw:0,0)
   [11] pulse
✅ Selected mic [11]: pulse

🔧 Calibrating microphone for background noise...
✅ Calibrated! Energy threshold: 7

🤖 JARVIS: JARVIS online. All systems operational.
```

## Prerequisites

- Kali Linux (or another Debian-based distro)
- Python 3.10+
- A working microphone with PulseAudio
- A [Groq API key](https://console.groq.com)

## Installation

```bash
git clone https://github.com/<your-username>/jarvis-ai.git
cd jarvis-ai

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

> No `requirements.txt` yet? Generate one from your working environment:
> ```bash
> pip freeze > requirements.txt
> ```

## Configuration

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_api_key_here
```

## Usage

```bash
source venv/bin/activate
python3 jarvis.py
```

On launch, JARVIS lists available microphones, lets you select one, and calibrates for background noise. You'll then see the mode menu:

| Command  | Description |
|----------|--------------|
| `voice`  | Voice mode — say "JARVIS" followed by your command |
| `train`  | Run voice training to improve recognition accuracy |
| `listen` | Capture a single voice command |
| *(text)* | Type a command directly |
| `exit`   | Quit JARVIS |

## Project Structure

```
jarvis-ai/
├── jarvis.py         # Main assistant entry point
├── mic_debug.py       # Microphone diagnostics/testing utility
├── nmap_scanner.py    # Nmap-based network scanning module
├── test.wav            # Sample audio file
├── requirements.txt
└── venv/                 # Python virtual environment (not committed)
```

## Troubleshooting

**ALSA / JACK errors on startup**
Messages like `ALSA lib ... Unknown PCM` and `jack server is not running` are harmless — Linux's audio stack is probing devices (HDMI, surround, JACK) that aren't present. They don't affect functionality as long as a working input device (e.g. `pulse`) is selected successfully.

**No microphone detected / permission errors**
Confirm PulseAudio is running:
```bash
pulseaudio --check
```
And that your user is in the `audio` group:
```bash
sudo usermod -aG audio $USER
```
(log out/in for the change to take effect)

## Roadmap

- [ ] Spoken (text-to-speech) responses
- [ ] Additional recon/security tool integrations
- [ ] Wake-word sensitivity tuning
- [ ] Persistent conversation context

## License

Licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Groq](https://groq.com) for LLaMA 3.3 inference
- Kali Linux
