import os
import sys
import time
import datetime
import webbrowser
import subprocess
import requests
import pyttsx3
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv

# ── Load API Keys ─────────────────────────────────────────
load_dotenv()
GROQ_API_KEY    = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WAKE_WORD       = "jarvis"

# ── Init Groq AI ──────────────────────────────────────────
client = Groq(api_key=GROQ_API_KEY)

# ── Init TTS ──────────────────────────────────────────────
engine = pyttsx3.init()
engine.setProperty("rate", 165)
engine.setProperty("volume", 1.0)
for v in engine.getProperty("voices"):
    if "english" in v.name.lower():
        engine.setProperty("voice", v.id)
        break

# ── Conversation Memory ───────────────────────────────────
conversation_history = []

SYSTEM_PROMPT = """You are JARVIS, an advanced AI assistant like Iron Man's JARVIS.
Rules:
- Always respond in 1-3 short sentences unless detail is needed
- Be helpful, intelligent, slightly formal
- Never say you are an AI model or mention Groq/LLaMA
- You run on Kali Linux
- Remember what the user tells you in the conversation
- If asked personal questions about the user, recall from history
- Never break character as JARVIS"""

# ═══════════════════════════════════════════════════════════
#  SPEAK
# ═══════════════════════════════════════════════════════════
def speak(text):
    print(f"\n🤖 JARVIS: {text}\n")
    try:
        engine.say(text)
        engine.runAndWait()
    except:
        try:
            subprocess.run(["espeak", "-s", "165", text],
                         capture_output=True)
        except:
            pass

# ═══════════════════════════════════════════════════════════
#  MICROPHONE SETUP
# ═══════════════════════════════════════════════════════════
def find_best_mic():
    """Find the best working microphone automatically."""
    mics = sr.Microphone.list_microphone_names()
    if not mics:
        return None

    print("\n📋 Available Microphones:")
    for i, name in enumerate(mics):
        print(f"   [{i}] {name}")

    # Priority: pulse > default > hw:0 > first available
    priority = ["pulse", "default", "hw:0,0", "usb", "mic"]
    for keyword in priority:
        for i, name in enumerate(mics):
            if keyword.lower() in name.lower():
                print(f"✅ Selected mic [{i}]: {name}")
                return i

    print(f"✅ Using mic [0]: {mics[0]}")
    return 0

def calibrate_mic(mic_index):
    """Calibrate microphone for background noise."""
    r = sr.Recognizer()
    print("\n🔧 Calibrating microphone for background noise...")
    print("   Please stay quiet for 2 seconds...")
    try:
        with sr.Microphone(device_index=mic_index) as source:
            r.adjust_for_ambient_noise(source, duration=2)
            threshold = r.energy_threshold
            print(f"✅ Calibrated! Energy threshold: {threshold:.0f}")
            return threshold
    except Exception as e:
        print(f"⚠️  Calibration error: {e}")
        return 300

# ═══════════════════════════════════════════════════════════
#  LISTEN - TRAINED FOR ACCURACY
# ═══════════════════════════════════════════════════════════
def listen(mic_index, energy_threshold=300, retries=3):
    """
    Trained listener with retry logic and noise handling.
    Returns recognized text or empty string.
    """
    r = sr.Recognizer()
    r.energy_threshold         = energy_threshold
    r.dynamic_energy_threshold = True
    r.dynamic_energy_adjustment_damping    = 0.15
    r.dynamic_energy_adjustment_multiplier = 1.5
    r.pause_threshold          = 0.8   # seconds of silence = phrase end
    r.operation_timeout        = None
    r.phrase_threshold         = 0.3
    r.non_speaking_duration    = 0.5

    for attempt in range(retries):
        try:
            with sr.Microphone(device_index=mic_index) as source:
                if attempt == 0:
                    print("🎤 Listening...", end=" ", flush=True)
                else:
                    print(f"🎤 Retry {attempt}/{retries}...",
                          end=" ", flush=True)

                # Quick noise adjust on retries
                if attempt > 0:
                    r.adjust_for_ambient_noise(source, duration=0.3)

                audio = r.listen(
                    source,
                    timeout=6,
                    phrase_time_limit=15
                )

            print("🔄 Processing...", end=" ", flush=True)

            # Try Google Speech (best accuracy, free)
            try:
                text = r.recognize_google(
                    audio,
                    language="en-IN",   # Indian English
                    show_all=False
                )
                print(f"\n👤 You said: \"{text}\"")
                return text.lower().strip()
            except sr.UnknownValueError:
                pass

            # Fallback: try with different language
            try:
                text = r.recognize_google(
                    audio,
                    language="en-US",
                    show_all=False
                )
                print(f"\n👤 You said: \"{text}\"")
                return text.lower().strip()
            except sr.UnknownValueError:
                print(f"\n❓ Couldn't understand. ", end="")
                if attempt < retries - 1:
                    print("Please repeat...")
                continue

        except sr.WaitTimeoutError:
            print(f"\n⏱️  No speech detected.", end=" ")
            if attempt < retries - 1:
                print("Listening again...")
            continue
        except sr.RequestError as e:
            print(f"\n🌐 Internet error: {e}")
            speak("I'm having trouble connecting to the internet.")
            return ""
        except OSError as e:
            print(f"\n🎙️  Mic error: {e}")
            speak("Microphone error. Please check your audio settings.")
            return ""
        except Exception as e:
            print(f"\n[Listen Error]: {e}")
            return ""

    print("\n⚠️  Could not understand after retries.")
    return ""

# ═══════════════════════════════════════════════════════════
#  WAKE WORD LISTENER
# ═══════════════════════════════════════════════════════════
def wait_for_wake_word(mic_index, energy_threshold):
    """
    Continuously listens for wake word 'JARVIS'.
    Returns the command after the wake word.
    """
    r = sr.Recognizer()
    r.energy_threshold         = energy_threshold
    r.dynamic_energy_threshold = True
    r.pause_threshold          = 0.6
    r.phrase_threshold         = 0.2
    r.non_speaking_duration    = 0.3

    print(f"\n👂 Waiting for wake word '{WAKE_WORD.upper()}'...", end="\r")

    while True:
        try:
            with sr.Microphone(device_index=mic_index) as source:
                # Short listen for wake word detection
                audio = r.listen(
                    source,
                    timeout=None,
                    phrase_time_limit=6
                )

            try:
                text = r.recognize_google(
                    audio,
                    language="en-IN"
                ).lower().strip()

                print(f"👂 Heard: \"{text}\"              ")

                if WAKE_WORD in text:
                    # Extract command after wake word
                    command = text.split(WAKE_WORD, 1)[-1].strip()

                    # If command already in same phrase
                    if command and len(command) > 2:
                        return command

                    # Wake word alone - listen for command
                    speak("Yes, how can I help you?")
                    command = listen(mic_index, energy_threshold)
                    return command

                print(f"👂 Waiting for '{WAKE_WORD.upper()}'...", end="\r")

            except sr.UnknownValueError:
                print(f"👂 Waiting for '{WAKE_WORD.upper()}'...", end="\r")
                continue

        except sr.RequestError as e:
            print(f"\n🌐 API error: {e}")
            time.sleep(2)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"\n[Wake Error]: {e}")
            time.sleep(1)

# ═══════════════════════════════════════════════════════════
#  AI BRAIN
# ═══════════════════════════════════════════════════════════
def ask_jarvis(user_input):
    """Send to Groq LLaMA and get smart response."""
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + conversation_history[-20:],  # keep last 20 messages
            max_tokens=300,
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()
        conversation_history.append({
            "role": "assistant",
            "content": reply
        })
        return reply
    except Exception as e:
        return f"I encountered an error: {e}"

# ═══════════════════════════════════════════════════════════
#  COMMAND HANDLER
# ═══════════════════════════════════════════════════════════
def handle_command(command):
    if not command:
        return "I didn't catch that. Could you repeat?"

    cmd = command.lower().strip()

    # ── Greetings ────────────────────────────────────────
    if cmd in ["hi", "hello", "hey", "hi jarvis", "hello jarvis"]:
        return ask_jarvis("Greet me as JARVIS would.")

    # ── Time / Date ──────────────────────────────────────
    if any(w in cmd for w in ["what time", "current time", "tell me the time"]):
        t = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {t}, sir."

    if any(w in cmd for w in ["what date", "today's date", "what day", "what is today"]):
        d = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {d}."

    # ── Weather ──────────────────────────────────────────
    if "weather" in cmd:
        city = "Kochi"
        if " in " in cmd:
            city = cmd.split(" in ")[-1].strip()
        elif " at " in cmd:
            city = cmd.split(" at ")[-1].strip()
        return get_weather(city)

    # ── Open Applications ────────────────────────────────
    if "open firefox" in cmd or "open browser" in cmd:
        subprocess.Popen(["firefox"])
        return "Opening Firefox browser."
    if "open youtube" in cmd:
        webbrowser.open("https://youtube.com")
        return "Opening YouTube."
    if "open google" in cmd:
        webbrowser.open("https://google.com")
        return "Opening Google."
    if "open terminal" in cmd:
        subprocess.Popen(["x-terminal-emulator"])
        return "Opening a new terminal."
    if "open spotify" in cmd:
        subprocess.Popen(["spotify"])
        return "Opening Spotify."

    # ── System Info ──────────────────────────────────────
    if any(w in cmd for w in ["my ip", "ip address", "what is my ip"]):
        ip = subprocess.getoutput("hostname -I | awk '{print $1}'")
        return f"Your local IP address is {ip}."

    if any(w in cmd for w in ["disk space", "storage", "hard drive"]):
        out = subprocess.getoutput(
            "df -h / | tail -1 | awk '{print $3\"/\"$2\" used, \"$4\" available\"}'"
        )
        return f"Disk usage: {out}."

    if any(w in cmd for w in ["ram", "memory usage", "how much memory"]):
        out = subprocess.getoutput(
            "free -h | awk '/^Mem:/ {print $3\" used out of \"$2}'"
        )
        return f"Memory usage: {out}."

    if any(w in cmd for w in ["cpu", "processor", "how fast"]):
        out = subprocess.getoutput("lscpu | grep 'Model name' | cut -d: -f2").strip()
        return f"Your processor is {out}."

    if any(w in cmd for w in ["wifi", "network", "internet", "connection"]):
        out = subprocess.getoutput(
            "nmcli -t -f NAME con show --active 2>/dev/null | head -1"
        )
        return f"Active network: {out}." if out else "No active network found."

    # ── Volume Control ───────────────────────────────────
    if "volume up" in cmd or "increase volume" in cmd:
        subprocess.run(["amixer", "-q", "sset", "Master", "10%+"])
        return "Volume increased."
    if "volume down" in cmd or "decrease volume" in cmd:
        subprocess.run(["amixer", "-q", "sset", "Master", "10%-"])
        return "Volume decreased."
    if "mute" in cmd:
        subprocess.run(["amixer", "-q", "sset", "Master", "toggle"])
        return "Audio muted."
    if "unmute" in cmd:
        subprocess.run(["amixer", "-q", "sset", "Master", "unmute"])
        return "Audio unmuted."

    # ── Search ───────────────────────────────────────────
    if cmd.startswith("search for ") or cmd.startswith("google "):
        query = cmd.replace("search for ", "").replace("google ", "")
        webbrowser.open(f"https://google.com/search?q={query}")
        return f"Searching Google for {query}."

    if cmd.startswith("youtube ") or "search youtube" in cmd:
        query = cmd.replace("youtube ", "").replace("search youtube for ", "")
        webbrowser.open(f"https://youtube.com/results?search_query={query}")
        return f"Searching YouTube for {query}."

    # ── Fun ──────────────────────────────────────────────
    if "joke" in cmd:
        return ask_jarvis("Tell me a short funny tech or science joke.")

    if "quote" in cmd or "motivation" in cmd:
        return ask_jarvis("Give me a short motivational quote.")

    if "flip a coin" in cmd:
        import random
        return f"It's {'heads' if random.random() > 0.5 else 'tails'}!"

    if "roll a dice" in cmd or "roll dice" in cmd:
        import random
        return f"You rolled a {random.randint(1, 6)}!"

    # ── Reminders ────────────────────────────────────────
    if "remember" in cmd:
        fact = cmd.replace("remember", "").replace("that", "").strip()
        conversation_history.append({
            "role": "user",
            "content": f"Please remember this: {fact}"
        })
        conversation_history.append({
            "role": "assistant",
            "content": f"I'll remember that {fact}."
        })
        return f"I'll remember that {fact}."

    # ── Exit ─────────────────────────────────────────────
    if any(w in cmd for w in ["exit", "quit", "goodbye", "bye", "shutdown", "turn off"]):
        speak("Shutting down all systems. Goodbye, sir!")
        sys.exit(0)

    # ── Fallback → Groq AI ───────────────────────────────
    return ask_jarvis(command)

# ═══════════════════════════════════════════════════════════
#  WEATHER
# ═══════════════════════════════════════════════════════════
def get_weather(city="Kochi"):
    if not WEATHER_API_KEY:
        return ask_jarvis(f"What's the typical weather like in {city}?")
    url = (f"http://api.openweathermap.org/data/2.5/weather"
           f"?q={city}&appid={WEATHER_API_KEY}&units=metric")
    try:
        d     = requests.get(url, timeout=5).json()
        if d.get("cod") != 200:
            return f"Could not find weather for {city}."
        desc  = d["weather"][0]["description"].capitalize()
        temp  = d["main"]["temp"]
        feels = d["main"]["feels_like"]
        humid = d["main"]["humidity"]
        return (f"Weather in {city.title()}: {desc}. "
                f"{temp}°C, feels like {feels}°C. "
                f"Humidity {humid}%.")
    except Exception as e:
        return f"Weather service unavailable: {e}"

# ═══════════════════════════════════════════════════════════
#  TRAINING TEST - checks if voice is working
# ═══════════════════════════════════════════════════════════
def run_voice_training(mic_index, energy_threshold):
    """Train and test the voice recognition system."""
    print("\n" + "="*50)
    print("  🎓 JARVIS VOICE TRAINING MODE")
    print("="*50)
    print("I will ask you to say some phrases to train the")
    print("voice recognition system.\n")

    training_phrases = [
        "Say: 'Hello JARVIS'",
        "Say: 'What time is it'",
        "Say: 'Open YouTube'",
    ]

    for phrase in training_phrases:
        speak(f"Please {phrase}")
        result = listen(mic_index, energy_threshold, retries=2)
        if result:
            speak(f"Got it! I heard: {result}")
        else:
            speak("I couldn't hear you. Let's continue anyway.")
        time.sleep(0.5)

    speak("Voice training complete. I am ready to assist you.")

# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
def main():
    print("="*50)
    print("      ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗")
    print("      ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝")
    print("      ██║███████║██████╔╝██║   ██║██║███████╗")
    print(" ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║")
    print(" ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║")
    print("  ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝")
    print("="*50)
    print("  Powered by Groq LLaMA 3.3 | Kali Linux")
    print("="*50)

    # Setup mic
    mic_index       = find_best_mic()
    energy_threshold = calibrate_mic(mic_index)

    speak("JARVIS online. All systems operational.")
    time.sleep(0.5)

    print("\n📖 MODES:")
    print("  Type 'voice'    → Voice mode (say JARVIS + command)")
    print("  Type 'train'    → Run voice training")
    print("  Type 'listen'   → One voice command")
    print("  Type a command  → Text mode")
    print("  Type 'exit'     → Quit\n")

    mode = "text"

    while True:
        try:
            if mode == "text":
                user_input = input("👤 You: ").strip()
                if not user_input:
                    continue

                if user_input.lower() == "voice":
                    mode = "voice"
                    speak("Voice mode activated. Say JARVIS followed by your command.")
                    print(f"\n💡 Say '{WAKE_WORD.upper()} stop' to exit voice mode\n")
                    continue

                if user_input.lower() == "train":
                    run_voice_training(mic_index, energy_threshold)
                    continue

                if user_input.lower() == "listen":
                    speak("Listening for your command.")
                    user_input = listen(mic_index, energy_threshold)
                    if not user_input:
                        speak("I didn't catch that.")
                        continue

                if user_input.lower() == "recalibrate":
                    energy_threshold = calibrate_mic(mic_index)
                    speak("Microphone recalibrated.")
                    continue

            elif mode == "voice":
                # Wait for wake word then get command
                command = wait_for_wake_word(mic_index, energy_threshold)

                if not command:
                    continue

                # Exit voice mode
                if any(w in command for w in ["stop", "text mode", "cancel voice"]):
                    mode = "text"
                    speak("Switching to text mode.")
                    continue

                user_input = command

            # Process the command
            print(f"🧠 Processing: \"{user_input}\"")
            response = handle_command(user_input)
            speak(response)

        except KeyboardInterrupt:
            print("\n")
            speak("Interrupted. Goodbye, sir!")
            sys.exit(0)
        except Exception as e:
            print(f"\n[System Error]: {e}")
            speak("I encountered a system error.")
            continue

if __name__ == "__main__":
    main()
from nmap_scanner import find_devices, scan_host_ports
def handle_command(command, speak):
    if "scan network" in command:
        devices = find_devices()
        speak(f"Found {len(devices)} devices.")
        for d in devices:
            print(d)
    elif "scan ports" in command:
        ip = extract_ip_from_command(command)  # write this helper yourself
        ports = scan_host_ports(ip)
        speak(f"Open ports on {ip}: {ports}")
import speech_recognition as sr
import pyttsx3
import re
from nmap_scanner import find_devices, scan_host_ports

# --- TTS setup ---
engine = pyttsx3.init()

def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

# --- Speech recognition setup ---
recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Speech service is unavailable right now.")
        return ""

# --- Helper to pull an IP out of a spoken command ---
def extract_ip(command):
    match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', command)
    return match.group(0) if match else None

# --- Command handling ---
def handle_command(command):
    if "scan network" in command or "find devices" in command:
        speak("Scanning the network, this may take a moment.")
        devices = find_devices()
        if devices:
            speak(f"Found {len(devices)} devices.")
            for d in devices:
                print(d)
        else:
            speak("No devices found.")

    elif "scan ports" in command or "check ports" in command:
        ip = extract_ip(command)
        if not ip:
            speak("Please tell me the IP address to scan.")
            return
        speak(f"Scanning ports on {ip}.")
        ports = scan_host_ports(ip)
        if ports:
            speak(f"Open ports on {ip} are: {', '.join(map(str, ports))}")
        else:
            speak(f"No open ports found on {ip}, or host is unreachable.")

    elif "exit" in command or "stop" in command:
        speak("Goodbye.")
        return False

    else:
        speak("I didn't understand that command.")

    return True

# --- Main loop ---
def main():
    speak("Jarvis is online.")
    running = True
    while running:
        command = listen()
        if command:
            running = handle_command(command)

if __name__ == "__main__":
    main()
