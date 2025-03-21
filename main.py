import pulsectl
import pydbus
import subprocess
import time
from inputimeout import inputimeout, TimeoutOccurred 
from dotenv import load_dotenv
import os
 
load_dotenv() 

recording_process = None
bus = pydbus.SessionBus()

def is_audio_playing() -> bool:
    """Check if audio is actively playing by checking for uncorked sink inputs."""
    command = ["pactl", "list", "sink-inputs"]
    result = subprocess.run(command, capture_output=True, text=True)

    if "Corked: no" in result.stdout:
        return True
    return False

def get_audio_device() -> str:
    """List audio devices and let the user select one."""
    print("Audio Devices:")
    result = subprocess.run("pactl list sources | grep Name", shell=True, capture_output=True, text=True)
    print(result.stdout)
    print("Copy and paste the full audio device name here")
    usr_choice = input("--> ").strip()
    return usr_choice

def get_win_loc() -> str:
    return subprocess.run("slurp", capture_output=True, text=True).stdout

def start_recording(audio_device: str, output_file: str, win_loc: str):
    """Start recording audio and video."""
    global recording_process
    command = ['wf-recorder', '-D', '--audio=' + audio_device, '-f', output_file, '-g', win_loc]
    recording_process = subprocess.Popen(command)
    print(f"Recording started: {output_file}")

def stop_recording():
    """Stop the current recording."""
    global recording_process
    if recording_process:
        print("Stopping recording...")
        recording_process.terminate() 
        recording_process.wait() 
        recording_process = None
        print("Recording stopped.")
    else:
        print("No recording is currently running.")

def get_min_media_length() -> int:
    return float(input("What is the minimum length of the content you are recording in mins: ")) * 60

def get_media_source() -> str:
    command = 'dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep "org.mpris.MediaPlayer2"'
    subprocess.run(command, shell=True)

    return input("Copy and paste the media player inside the quotes that you are recording: ") 
    
def check_valid_stop(min_media_length, start_time) -> int:
    record_time = 0 
    while record_time < min_media_length: 
        while is_audio_playing():
            time.sleep(0.5)
        print("Invalid stop time. Continuing...")

        end_time = time.perf_counter()
        record_time = end_time - start_time

    return record_time 
    
def anti_ayw(media_player_name):
    player = bus.get(media_player_name, '/org/mpris/MediaPlayer2')
    player.PlayPause()
    time.sleep(2)
    player.PlayPause()
    
def send_notification(message: str):
    from discord_webhook import DiscordWebhook
    WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    webhook = DiscordWebhook(url=WEBHOOK_URL, content=message)
    response = webhook.execute()

# Main script
media_player_name = get_media_source()
min_media_length = get_min_media_length()
win_loc = get_win_loc()
audio_device = get_audio_device()

try:
    num_recordings = int(input("How many recordings do you want to make? "))
except ValueError:
    print("Invalid input. Try Again.")
    exit()

i = 1
while i <= num_recordings:

    # Wait for audio before start recording
    while not is_audio_playing():
        time.sleep(0.5)
    
    # Make sure are you watching doesn't show up 
    anti_ayw(media_player_name)

    start_recording(audio_device, f"recording{i}.mkv", win_loc)
    start_time = time.perf_counter()
    # Make sure audio stop is at a valid time not in the middle of movie 
    record_time = check_valid_stop(min_media_length, start_time)    
    stop_recording()
    
    message = f"🏴‍☠️ARGH! Recording {i}/{num_recordings} just finished at {round((record_time / 60), 2)} mins." 
    send_notification(message) 

    if i > num_recordings:
        print("Exiting...")
        break

    i += 1
