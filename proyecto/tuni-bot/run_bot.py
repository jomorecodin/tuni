#!/usr/bin/env python3
"""Entry point for the TUNI Telegram bot."""
import sys
from pathlib import Path

# Ensure the project root is on the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.bot.main import run_bot

if __name__ == "__main__":
    run_bot()
