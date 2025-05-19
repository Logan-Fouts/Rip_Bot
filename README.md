# Rip Bot

Automated media recording tool with anti-"Are You Watching" protection for Linux.

## Features
- Automated screen recording triggered by audio playback
- Anti-AYW (Are You Watching) detection bypass
- Discord notifications for completed recordings
- Configurable recording parameters

## Installation
```bash
# Clone the repository
git clone https://github.com/Logan-Fouts/Rip_Bot.git
cd RIP_The_Tube

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

## Usage
```bash
screen-pirate [OPTIONS]

Options:
  --ayw/--no-ayw      Enable anti-AYW protection
  --media-player TEXT  Media player DBUS name
  --min-length FLOAT   Minimum recording length (minutes)
  --win-loc TEXT       Window coordinates (auto-detected if empty)
  --audio-device TEXT  Audio device name
  --num-recordings INT Number of recordings to make
```

## Requirements
- Linux with PulseAudio
- wf-recorder
- slurp
- python-uinput
- DBus-compatible media player

## Configuration
Create a `.env` file with:
```ini
DISCORD_WEBHOOK_URL=your_webhook_url
```
