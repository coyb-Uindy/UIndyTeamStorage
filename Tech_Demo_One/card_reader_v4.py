import pandas as pd
from pynput import keyboard
from datetime import datetime
from pathlib import Path
import RPi.GPIO as GPIO
import time

card_data = ""
accepting_input = True  # Global flag to block input during GPIO activation

# --- GPIO Setup ---
PIN_NUMBER = 18  # Change this to your GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_NUMBER, GPIO.OUT)
GPIO.output(PIN_NUMBER, GPIO.LOW)

# --- File Setup ---
LOG_FILE_PATH = Path("Tech_Demo_One/card_swipes.csv")
LOG_FILE = "Tech_Demo_One/card_swipes.csv"

if LOG_FILE_PATH.exists():
    print(f"File {LOG_FILE} exists!")
else:
    print(f"File {LOG_FILE} does not exist, creating now.")
    card_swipe_df = pd.DataFrame(columns=["timestamp", "card id"])
    card_swipe_df.to_csv(LOG_FILE, index=False)

# Read .csv log file
card_swipe_df = pd.read_csv(LOG_FILE)

# --- Function to activate GPIO pin (Blocking) ---
def activate_pin_for_10s():
    global accepting_input

    accepting_input = False  # Disable new card swipes
    GPIO.output(PIN_NUMBER, GPIO.HIGH)
    print(f"GPIO pin {PIN_NUMBER} activated.")
    print("System is locked — waiting 10 seconds...")
    time.sleep(10)
    GPIO.output(PIN_NUMBER, GPIO.LOW)
    print(f"GPIO pin {PIN_NUMBER} deactivated. System unlocked.")
    accepting_input = True  # Allow new swipes again

# --- Function to log card data ---
def log_card_data(swipe_id):
    global card_swipe_df

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if (card_swipe_df["card id"] == swipe_id).any():
        print(f"Card {swipe_id} already logged — activating GPIO.")
        activate_pin_for_10s()
    else:
        print(f"Card {swipe_id} not logged, logging now")
        card_swipe_df.loc[len(card_swipe_df)] = {"timestamp": timestamp, "card id": swipe_id}
        card_swipe_df.to_csv(LOG_FILE, index=False)
        print(f"Card logged: {swipe_id}")

    print("Swipe your card (Press ESC to exit)...")

# --- Function to read swipe data ---
def on_press(key):
    global card_data, accepting_input

    if not accepting_input:
        # Ignore inputs while GPIO is active
        return

    try:
        if key.char:
            card_data += key.char
    except AttributeError:
        if key == keyboard.Key.enter:
            if card_data.strip():
                log_card_data(card_data)
            card_data = ""  # Clear buffer
        elif key == keyboard.Key.esc:
            print("Exiting...")
            GPIO.cleanup()
            return False

# --- Main Loop ---
print("Swipe your card (Press ESC to exit)...")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
