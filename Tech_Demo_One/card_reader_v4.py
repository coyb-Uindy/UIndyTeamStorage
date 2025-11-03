#!/usr/bin/env python3
import pandas as pd
from pynput import keyboard
from datetime import datetime
from pathlib import Path
import RPi.GPIO as GPIO
import time

# -------------------- CONFIG --------------------
PIN_NUMBER = 12  # Change to your GPIO pin number
CSV_FILENAME = "card_swipes.csv"
# ------------------------------------------------

# --- Get path to this script’s folder (Tech_Demo_One) ---
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE_PATH = SCRIPT_DIR / CSV_FILENAME

print(f"[INFO] Script directory: {SCRIPT_DIR}")
print(f"[INFO] CSV file path: {LOG_FILE_PATH}")

# --- Check for CSV file ---
if LOG_FILE_PATH.exists():
    print(f"[INFO] File {LOG_FILE_PATH.name} found.")
else:
    print(f"[INFO] File not found — creating a new one.")
    pd.DataFrame(columns=["timestamp", "card id"]).to_csv(LOG_FILE_PATH, index=False)

# --- Read the CSV file ---
card_swipe_df = pd.read_csv(LOG_FILE_PATH)

# --- GPIO setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_NUMBER, GPIO.OUT)
GPIO.output(PIN_NUMBER, GPIO.LOW)

card_data = ""
accepting_input = True  # Prevent input during 10-sec lockout

# --- Function to block input and activate GPIO ---
def activate_pin_for_10s_blocking():
    global accepting_input
    accepting_input = False
    GPIO.output(PIN_NUMBER, GPIO.HIGH)
    print(f"[GPIO] Pin {PIN_NUMBER} HIGH — locked for 10 seconds...")
    time.sleep(10)
    GPIO.output(PIN_NUMBER, GPIO.LOW)
    print(f"[GPIO] Pin {PIN_NUMBER} LOW — unlocked.")
    accepting_input = True

# --- Log card swipes ---
def log_card_data(swipe_id):
    global card_swipe_df

    swipe_id = swipe_id.strip()
    if not swipe_id:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if (card_swipe_df["card id"] == swipe_id).any():
        print(f"[INFO] Card {swipe_id} already logged — activating GPIO.")
        activate_pin_for_10s_blocking()
    else:
        print(f"[INFO] Card {swipe_id} not logged — logging now.")
        card_swipe_df.loc[len(card_swipe_df)] = {"timestamp": timestamp, "card id": swipe_id}
        card_swipe_df.to_csv(LOG_FILE_PATH, index=False)
        print(f"[INFO] Card logged: {swipe_id}")

    print("Swipe your card (Press ESC to exit)...")

# --- Keyboard listener for swipes ---
def on_press(key):
    global card_data, accepting_input

    if not accepting_input:
        return  # Ignore input during GPIO activation

    try:
        if key.char:
            card_data += key.char
    except AttributeError:
        if key == keyboard.Key.enter:
            if card_data.strip():
                log_card_data(card_data)
            card_data = ""  # Clear buffer
        elif key == keyboard.Key.esc:
            print("[INFO] Exiting...")
            GPIO.cleanup()
            return False

print("Swipe your card (Press ESC to exit)...")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
