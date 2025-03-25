import pulsectl
import pydbus
import random
import subprocess
import time
import os
import libclicker
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook
 
load_dotenv() 

recording_process = None
bus = pydbus.SessionBus()

def start_recording(audio_device: str, output_file: str, win_loc: str):
    command = ['wf-recorder', '-D', '--audio=' + audio_device, '-f', output_file, '-g', win_loc]
    recording_process = subprocess.Popen(command)
    print(f"Recording started: {output_file}")

def stop_recording():
    global recording_process
    if recording_process:
        print("Stopping recording...")
        recording_process.terminate() 
        recording_process.wait() 
        recording_process = None
    else:
        print("No recording is currently running.")

def is_audio_playing() -> bool:
    result = subprocess.run(["pactl", "list", "sink-inputs"], capture_output=True, text=True)

    if "Corked: no" in result.stdout:
        return True

    return False

def check_valid_stop(min_media_length, start_time) -> int:
    record_time = 0 
    while record_time < min_media_length: 
        while is_audio_playing():
            time.sleep(0.5)
        print("Invalid stop time. Continuing...")

        record_time = time.perf_counter() - start_time

    return record_time 
    
def anti_ayw(win_loc):
    win_loc = win_loc.strip().split(" ")

    offset = win_loc[0].split(",")
    x_offset, y_offset = int(offset[0]), int(offset[1])

    dimensions = win_loc[1].split("x")
    width, height = int(dimensions[0]), int(dimensions[1])
    x, y = (width >> 1) + x_offset + 500, (height >> 1) + y_offset + random.randint(10, 100)

    libclicker.move_mouse(x, y)
    libclicker.click(x, y)
    time.sleep(1)
    libclicker.click(x, y)
    
def send_notification(message: str):
    webhook = DiscordWebhook(url=os.getenv("DISCORD_WEBHOOK_URL"), content=message)
    _ = webhook.execute()

def get_audio_device() -> str:
    print("Audio Devices:")
    result = subprocess.run("pactl list sources | grep Name", shell=True, capture_output=True, text=True)
    print(result.stdout)
    print("Copy and paste the full audio device name here")
    usr_choice = input("--> ").strip()
    return usr_choice

def get_win_loc() -> str:
    return subprocess.run("slurp", capture_output=True, text=True).stdout

def get_min_media_length() -> int:
    return float(input("What is the minimum length of the content you are recording in mins: ")) * 60

def get_media_source() -> str:
    command = 'dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep "org.mpris.MediaPlayer2"'
    subprocess.run(command, shell=True)

    return input("Copy and paste the media player inside the quotes that you are recording: ") 
    
def get_num_recodings() -> int:
    return int(input("How many recordings do you want to make? "))

# Main script
min_media_length, win_loc, audio_device, num_recordings = get_min_media_length(), get_win_loc(), get_audio_device(), get_num_recordings()

for i in range(1, num_recordings + 1):
    while not is_audio_playing(): # Wait for audio before start recording
        time.sleep(0.5)
    
    anti_ayw(win_loc)

    start_recording(audio_device, f"recording{i}.mkv", win_loc)
    record_time = check_valid_stop(min_media_length, time.perf_counter())
    stop_recording()
    
    send_notification(f"🏴‍☠️ARGH! Recording {i}/{num_recordings} just finished at {round((record_time / 60), 2)} mins.") 
    time.sleep(5)
