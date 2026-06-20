# JARVIS 🤖

> AI-powered voice & text assistant for Kali Linux, built on Groq's LLaMA 3.3, with Nmap-based network recon on the way.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Kali%20Linux-557C94)
![LLM](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

JARVIS is a terminal-based AI assistant for Kali Linux that pairs LLM reasoning (via Groq's LLaMA 3.3) with speech recognition, system control, and security tooling. Talk to it with your voice or type commands directly — it handles everything from "what's the weather" to "what's my IP address" to open-ended conversation, falling back to the LLM whenever a command doesn't match a built-in skill.

## Features

- 🎙️ **Voice Mode** — wake-word activated ("JARVIS"), hands-free command input
- ⌨️ **Text Mode** — type commands directly when voice isn't convenient
- 🧠 **LLM-Powered Reasoning** — Groq-hosted LLaMA 3.3 handles open-ended conversation, jokes, quotes, and anything outside the built-in commands, with short-term memory of the conversation
- 🎯 **Voice Training** — calibrate recognition against a few sample phrases
- 🔊 **Auto Noise Calibration** — detects ambient noise and sets an energy threshold on startup, with retry logic and an en-IN → en-US recognition fallback
- 🌦️ **Weather Lookups** — live conditions via OpenWeatherMap (falls back to an LLM estimate if no API key is set)
- 🖥️ **System Info & Control** — local IP, disk usage, RAM, CPU model, active network, and volume up/down/mute
- 🚀 **App Launching & Search** — open Firefox, the terminal, Spotify, YouTube, or Google, and run web/YouTube searches by voice or text
- 🎲 **Small Utilities** — coin flips, dice rolls, and a "remember that..." command to pin facts into conversation context
- 🛰️ **Nmap Scanning Module** — a host-discovery and port-scanning module (`nmap_scanner`) ships alongside the assistant; wiring it fully into voice/text commands is in progress (see [Roadmap](#roadmap))

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
- A [Groq API key](https://console.groq.com) (required)
- An [OpenWeatherMap API key](https://openweathermap.org/api) (optional — weather falls back to an LLM estimate without one)

## Installation

```bash
git clone https://github.com/sooryakiran2912-cpu/jarvis-Nmap-AI.git
cd jarvis-Nmap-AI

# System dependencies (mic input, TTS fallback, audio control)
sudo apt update
sudo apt install -y python3-venv portaudio19-dev espeak alsa-utils nmap

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

> No `requirements.txt` in your checkout yet? Create one with:
> ```bash
> pip install groq python-dotenv pyttsx3 SpeechRecognition PyAudio requests
> pip freeze > requirements.txt
> ```

## Configuration

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
WEATHER_API_KEY=your_openweathermap_key_here   # optional
```

## Usage

```bash
source venv/bin/activate
python3 jarvis.py
```

On launch, JARVIS lists available microphones, auto-selects the best one (preferring `pulse`), and calibrates for background noise. You'll then land in text mode with these options:

| Command       | Description |
|---------------|--------------|
| `voice`       | Switch to voice mode — say "JARVIS" followed by your command |
| `train`       | Run a short voice training/calibration check |
| `listen`      | Capture a single voice command without entering voice mode |
| `recalibrate` | Re-run ambient noise calibration |
| *(text)*      | Type any command directly |
| `exit`        | Quit JARVIS |

Try things like *"what time is it"*, *"weather in Kochi"*, *"open youtube"*, *"my ip address"*, *"volume up"*, or just chat — anything not recognized as a built-in command is sent to the LLM.

## Project Structure

```
jarvis-Nmap-AI/
├── jarvis.py     # Main assistant: voice/text I/O, command handling, Groq integration
├── nmap_scanner   # Host discovery / port scanning helpers (find_devices, scan_host_ports)
└── README.md
```

`requirements.txt`, `.env`, and `venv/` are expected locally but not committed — see [Installation](#installation) and [Configuration](#configuration) above.

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

**Voice recognition errors / no internet**
Speech-to-text uses Google's free recognition API and needs an internet connection. If it's unreachable, JARVIS will tell you and switch back to text mode for that command.

## Roadmap

- [ ] Fully wire `nmap_scanner` into voice/text commands (e.g. "scan network", "scan ports on 192.168.1.1")
- [ ] Commit `requirements.txt` and a `LICENSE` file
- [ ] Clean up duplicate/legacy code paths in `jarvis.py`
- [ ] Persistent conversation context across sessions
- [ ] Wake-word sensitivity tuning

## License

Licensed under the MIT License.

## Acknowledgments

- [Groq](https://groq.com) for LLaMA 3.3 inference
- Kali Linux
