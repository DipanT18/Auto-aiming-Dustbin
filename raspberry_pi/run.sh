#!/bin/bash
# run.sh — start the Auto-Aiming Dustbin runtime on Raspberry Pi
set -e

echo "[run] Starting Auto-Aiming Dustbin..."
cd app
python3 main.py --config ../config/local.yaml --show
