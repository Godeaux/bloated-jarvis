from wake_word import wait_for_wake_word
from transcribe import record_and_transcribe
from pynput.keyboard import Controller
import os
from dotenv import load_dotenv
import requests
import pyttsx3
from datetime import datetime

########### Configs ###########
monitor_number = 2 # 1 is Windows monitor 1, etc.
textbox_x_padding = 300
textbox_y_padding = 50
discord_switch_delay_sec = 0.5
###############################

# Load environment variables from .env file
load_dotenv()

keyboard = Controller()

guild_id = os.getenv("GUILD_ID")
user_id = os.getenv("USER_ID")
voice_channel_id = os.getenv("VOICE_CHANNEL_ID")

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()

# Simple color-coded logger for nicer console output
COLORS = {
    "reset": "\033[0m",
    "blue": "\033[94m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "magenta": "\033[95m",
}

def log(message: str, color: str = "blue"):
    color_code = COLORS.get(color, "")
    reset = COLORS["reset"]
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color_code}[{timestamp}] {message}{reset}")

def speak(text: str):
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen_for_voice_commands():
    while True:
        log("Say \"Jarvis\" to wake...", "yellow")
        wait_for_wake_word()
        log("Wake word detected.", "green")
        transcript = record_and_transcribe()
        log(f"You said: {transcript}", "magenta")

        if ("now" in transcript and "playing" in transcript):
            log("Now playing command detected.")
            speak("Now playing.")
            send_command("now-playing")
        elif "played" in transcript:
            log("Play command detected.")
            song_name = transcript.replace("played", "", 1).strip()
            if song_name:
                speak(f"Playing {song_name}")
                send_play_command(song_name)
        elif "play" in transcript:
            log("Play command detected.")
            song_name = transcript.replace("play", "", 1).strip()
            if song_name:
                speak(f"Playing {song_name}")
                send_play_command(song_name)
        elif "stop" in transcript:
            log("Stop playback command detected.")
            speak("Stopping playback.")
            send_command("stop")
        elif "pause" in transcript:
            log("Pause playback command detected.")
            speak("Pausing playback.")
            send_command("pause")
        elif "resume" in transcript:
            log("Resume playback command detected.")
            speak("Resuming playback.")
            send_command("resume")
        elif "next" in transcript:
            log("Skip track command detected.")
            speak("Skipping track.")
            send_command("next")
        elif "clear" in transcript:
            log("Clear queue command detected.")
            speak("Clearing queue.")
            send_command("clear")
        elif ("kill" in transcript and "self" in transcript) or ("self" in transcript and "destruct" in transcript):
            log("Kill command detected.")
            speak("Goodbye.")
            quit()
        else:
            log("No known command found.")
            speak("Sorry, I didn't understand that command.")

def send_play_command(song_name: str):
    url = "https://vibesbot.no-vibes.com/command/play"
    payload = {
        "guildId": guild_id,
        "userId": user_id,
        "voiceChannelId": voice_channel_id,
        "options": {"query": song_name}
    }
    response = requests.post(url, json=payload)
    log(f"Packet sent to {url}: {payload}", "green")
    try:
        return response.json()
    except Exception:
        log(f"Non-JSON response: {response.status_code} {response.text}", "red")
        return None

def send_command(command: str):
    url = f"https://vibesbot.no-vibes.com/command/{command}"
    payload = {
        "guildId": guild_id,
        "userId": user_id,
        "voiceChannelId": voice_channel_id,
        "options": {}
    }
    response = requests.post(url, json=payload)
    log(f"Packet sent to {url}: {payload}", "green")
    try:
        return response.json()
    except Exception:
        log(f"Non-JSON response: {response.status_code} {response.text}", "red")
        return None

def main():
    log("Starting Jarvis...", "yellow")

    # for some reason you need to click the window first
    # to ensure Discord window can be activated on first run???
    # not even a manual click works...

    log("Starting voice command listener...", "yellow")
    listen_for_voice_commands()

if __name__ == "__main__":
    main()
