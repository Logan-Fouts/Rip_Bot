#!/bin/bash

# Auto-setup script for Linux multimedia tools
# Supports Ubuntu/Debian and Fedora/RHEL systems

set -e  # Exit on any error

echo "=== Linux Multimedia Tools Setup ==="
echo "Installing: PulseAudio, wf-recorder, slurp, python-uinput, DBus media player"
echo

# Detect distribution
if command -v apt &> /dev/null; then
    DISTRO="debian"
    PKG_MANAGER="apt"
elif command -v dnf &> /dev/null; then
    DISTRO="fedora"
    PKG_MANAGER="dnf"
elif command -v yum &> /dev/null; then
    DISTRO="rhel"
    PKG_MANAGER="yum"
else
    echo "Unsupported distribution. This script supports Debian/Ubuntu and Fedora/RHEL systems."
    exit 1
fi

echo "Detected distribution: $DISTRO"
echo "Using package manager: $PKG_MANAGER"
echo

# Update package lists
echo "Updating package lists..."
if [ "$DISTRO" = "debian" ]; then
    sudo apt update
else
    sudo $PKG_MANAGER update
fi

# Install packages based on distribution
echo "Installing packages..."
if [ "$DISTRO" = "debian" ]; then
    # Ubuntu/Debian packages
    sudo apt install -y \
        pulseaudio \
        pulseaudio-utils \
        wf-recorder \
        slurp \
        python3-pip \
        python3-dev \
        dbus \
        vlc \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad \
        gstreamer1.0-plugins-ugly
else
    # Fedora/RHEL packages
    sudo $PKG_MANAGER install -y \
        pulseaudio \
        pulseaudio-utils \
        wf-recorder \
        slurp \
        python3-pip \
        python3-devel \
        dbus \
        vlc \
        gstreamer1-plugins-good \
        gstreamer1-plugins-bad-free \
        gstreamer1-plugins-ugly-free
fi

# Install python-uinput
echo "Installing python-uinput..."
pip3 install --user python-uinput

# Add user to input group for uinput access
echo "Adding user to input group..."
sudo usermod -a -G input $USER

# Create udev rule for uinput device
echo "Setting up uinput permissions..."
sudo tee /etc/udev/rules.d/99-uinput.rules > /dev/null << EOF
KERNEL=="uinput", MODE="0664", GROUP="input"
EOF

# Load uinput module
echo "Loading uinput kernel module..."
sudo modprobe uinput
echo "uinput" | sudo tee /etc/modules-load.d/uinput.conf > /dev/null

# Start PulseAudio if not running
echo "Starting PulseAudio..."
pulseaudio --start --log-target=syslog || true

# Install additional packages for Rip Bot
echo "Installing additional packages for Rip Bot..."
if [ "$DISTRO" = "debian" ]; then
    sudo apt install -y git python3-venv
else
    sudo $PKG_MANAGER install -y git python3-virtualenv
fi

# Clone and setup Rip Bot
echo "Setting up Rip Bot..."
cd ~/
if [ -d "Rip_Bot" ]; then
    echo "Rip_Bot directory already exists, updating..."
    cd Rip_Bot
    git pull
else
    echo "Cloning Rip Bot repository..."
    git clone https://github.com/Logan-Fouts/Rip_Bot.git
    cd Rip_Bot
fi

# Create virtual environment and install dependencies
echo "Creating virtual environment..."
python3 -m venv venv

echo "Installing Rip Bot dependencies..."
source venv/bin/activate
pip install -e .
deactivate

# Create convenience script
echo "Creating Rip Bot launcher script..."
cat > ~/rip-bot.sh << 'EOF'
#!/bin/bash
cd ~/Rip_Bot
source venv/bin/activate
screen-pirate "$@"
EOF
chmod +x ~/rip-bot.sh

# Add to PATH
if ! grep -q 'export PATH="$HOME:$PATH"' ~/.bashrc; then
    echo 'export PATH="$HOME:$PATH"' >> ~/.bashrc
fi

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
echo "Please log out and log back in (or reboot) for group changes to take effect."
echo
echo "After relogging, you can use Rip Bot with:"
echo "  ~/rip-bot.sh --help                    # Show help"
echo "  ~/rip-bot.sh --ayw --min-length 5     # Record with anti-AYW protection"
echo
echo "Configuration:"
echo "  - Edit ~/Rip_Bot/.env to add Discord webhook URL"
echo "  - Rip Bot installed in: ~/Rip_Bot"
echo
echo "Test the tools:"
echo "  - PulseAudio: pulseaudio --check -v"
echo "  - Screen recording: wf-recorder -g \"\$(slurp)\" output.mp4"
echo "  - Python uinput: python3 -c 'import uinput; print(\"uinput OK\")'"
echo
