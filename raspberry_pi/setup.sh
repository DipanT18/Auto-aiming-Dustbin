#!/bin/bash
# setup.sh — install system and Python dependencies on Raspberry Pi
set -e

echo "[setup] Updating package list..."
sudo apt update

echo "[setup] Installing system packages..."
sudo apt install -y python3-pip python3-opencv

echo "[setup] Installing Python dependencies..."
pip3 install -r requirements.txt

echo "[setup] Done. Run './run.sh' to start the system."
