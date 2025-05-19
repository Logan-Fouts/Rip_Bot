import pulsectl
import pydbus
import random
import subprocess
import time
import os
from .libclicker import click as lclick
from .libclicker import move_mouse
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook
import click
load_dotenv()

recording_process = None
bus = pydbus.SessionBus()

def start_recording(audio_device: str, output_file: str, win_loc: str):
    global recording_process
    command = ['wf-recorder', '-D', '--audio=' + audio_device, '-f', output_file, '-g', win_loc]
    recording_process = subprocess.Popen(command)
    click.echo(f"Recording started: {output_file}")

def stop_recording():
    global recording_process
    if recording_process:
        click.echo("Stopping recording...")
        recording_process.terminate() 
        recording_process.wait() 
        recording_process = None
    else:
        click.echo("No recording is currently running.")

def is_audio_playing() -> bool:
    result = subprocess.run(["pactl", "list", "sink-inputs"], capture_output=True, text=True)
    return "Corked: no" in result.stdout

def check_valid_stop(min_media_length, start_time) -> int:
    record_time = 0 
    while record_time < min_media_length: 
        while is_audio_playing():
            time.sleep(1)
        click.echo("Invalid stop time. Continuing...")
        record_time = time.perf_counter() - start_time
    return record_time 
    
def anti_ayw(win_loc, media_player_name):
    player = bus.get(media_player_name, '/org/mpris/MediaPlayer2')
    win_loc = win_loc.strip().split(" ")
    offset = win_loc[0].split(",")
    x_offset, y_offset = int(offset[0]), int(offset[1])
    dimensions = win_loc[1].split("x")
    width, height = int(dimensions[0]), int(dimensions[1])
    x, y = (width >> 1) + x_offset + 500, (height >> 1) + y_offset + random.randint(10, 100)
    move_mouse(9000, 540 + random.randint(10, 100))  # Changed to lclick
    player.PlayPause()
    time.sleep(2)
    player.PlayPause()
    
def send_notification(message: str):
    webhook = DiscordWebhook(url=os.getenv("DISCORD_WEBHOOK_URL"), content=message)
    webhook.execute()

def get_audio_device() -> str:
    click.echo("Audio Devices:")
    result = subprocess.run("pactl list sources | grep Name", shell=True, capture_output=True, text=True)
    click.echo(result.stdout)
    return click.prompt("Copy and paste the full audio device name", type=str)

def get_win_loc() -> str:
    return subprocess.run("slurp", capture_output=True, text=True).stdout

def get_media_source() -> str:
    command = 'dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep "org.mpris.MediaPlayer2"'
    subprocess.run(command, shell=True)
    return click.prompt("Copy and paste the media player inside the quotes that you are recording", type=str)

def get_num_recordings() -> int:
    return int(input("How many recordings do you want to make? "))

@click.command()
@click.option('--ayw/--no-ayw', default=None, help="Enable anti 'are you watching'")
@click.option('--media-player', help="Media player name (e.g., 'org.mpris.MediaPlayer2.spotify')")
@click.option('--min-length', type=float, help="Minimum recording length in minutes")
@click.option('--win-loc', help="Window location coordinates")
@click.option('--audio-device', help="Audio device name")
@click.option('--num-recordings', type=int, help="Number of recordings to make")
def main(ayw, media_player, min_length, win_loc, audio_device, num_recordings):
    """Automated media recording tool with anti-AYW protection"""
    
    if media_player is None:
        media_player = get_media_source()
    if min_length is None:
        min_length = click.prompt("Minimum length of content (minutes)", type=float) * 60
    else:
        min_length *= 60
    if win_loc is None:
        win_loc = get_win_loc()
    if audio_device is None:
        audio_device = get_audio_device()
    if num_recordings is None:
        num_recordings = get_num_recordings()
    if ayw is None:
        ayw = click.confirm("Enable anti 'are you watching'?")

    for i in range(1, num_recordings + 1):
        while not is_audio_playing():
            time.sleep(0.5)
        
        if ayw:
            anti_ayw(win_loc, media_player)
        time.sleep(2)

        start_recording(audio_device, f"recording{i}.mkv", win_loc)
        record_time = check_valid_stop(min_length, time.perf_counter())
        stop_recording()
        
        send_notification(f"🏴‍☠️ Recording {i}/{num_recordings} finished ({round(record_time/60, 2)} mins)")
        time.sleep(6)

if __name__ == '__main__':
    main()