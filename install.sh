#!/bin/bash

set -e  # Exit on any error

echo "=== Linux Multimedia Tools Setup ==="
echo "Installing: PulseAudio, wf-recorder, slurp, python-uinput, DBus media player"
echo

sudo pacman -S \
    wf-recorder \
    slurp \
    vlc \
    git \
    --noconfirm || {
        echo "Failed to install required packages. Please check your package manager."
        exit 1
    }

# Clone and setup Rip Bot
echo "Setting up Rip Bot..."
cd ~/
if [ -d "Rip_Bot" ]; then
    echo "Rip_Bot directory already exists, updating..."
    cd Rip_Bot
    git pull
else
    echo "Cloning Rip Bot repository..."
    git clone https://github.com/Logan-Fouts/Rip_Bot.git --depth 1
    cd Rip_Bot
fi

# Create virtual environment and install dependencies
echo "Creating virtual environment..."
python3 -m venv venv

echo "Installing Rip Bot dependencies..."
source venv/bin/activate
pip install -e .
deactivate

echo "Creating .env template..."
if [ ! -f ~/Rip_Bot/.env ]; then
    cat > ~/Rip_Bot/.env << 'EOF'
# Discord webhook URL for notifications (optional)
# DISCORD_WEBHOOK_URL=your_webhook_url_here
EOF
fi

# Verify installations
echo
echo "=== Verification ==="
echo "Checking installed tools..."

command -v pulseaudio >/dev/null && echo "✓ PulseAudio installed" || echo "✗ PulseAudio missing"
command -v wf-recorder >/dev/null && echo "✓ wf-recorder installed" || echo "✗ wf-recorder missing"
command -v slurp >/dev/null && echo "✓ slurp installed" || echo "✗ slurp missing"
python3 -c "import uinput" 2>/dev/null && echo "✓ python-uinput installed" || echo "✗ python-uinput missing"
command -v vlc >/dev/null && echo "✓ VLC (DBus media player) installed" || echo "✗ DBus media player missing"
command -v git >/dev/null && echo "✓ Git installed" || echo "✗ Git missing"
[ -d ~/Rip_Bot ] && echo "✓ Rip Bot cloned" || echo "✗ Rip Bot missing"
[ -f ~/Rip_Bot/venv/bin/activate ] && echo "✓ Virtual environment created" || echo "✗ Virtual environment missing"

echo
echo "=== Setup Complete! ==="
echo
