#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Blinka dependencies (CircuitPython)
pip install --upgrade adafruit-python-shell

# Download and run the Blinka installer
wget -O raspi-blinka.py https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo -E env PATH=$PATH python3 raspi-blinka.py
