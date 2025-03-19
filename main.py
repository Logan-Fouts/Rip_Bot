import pulsectl
import subprocess
import time
from inputimeout import inputimeout, TimeoutOccurred 


recording_process = None

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

# Main script
win_loc = get_win_loc()
audio_device = get_audio_device()

try:
    num_recordings = int(input("How many recordings do you want to make? "))
except ValueError:
    print("Invalid input. Defaulting to 1 recording.")
    num_recordings = 1

i = 1
while i <= num_recordings:

    while not is_audio_playing():
        time.sleep(0.5)

    start_recording(audio_device, f"recording{i}.mkv", win_loc)

    while is_audio_playing():
        time.sleep(0.1)

    stop_recording()
    
    if i < num_recordings:
        try:
            user_input = inputimeout(
                prompt="Do you want to record another video? (yes/no): ",
                timeout=5 # Wait for 5
            ).strip().lower()
        except TimeoutOccurred:
            print("No input received. Continuing to the next recording...")
            user_input = "yes" 
    else:
        user_input = "no" 
  
    if user_input != 'yes':
        print("Exiting...")
        break
        
    while not is_audio_playing():
        time.sleep(1)

    i += 1
