import os
import time
import pandas as pd
from datetime import datetime

# Check environment
WAYLAND = os.getenv("XDG_SESSION_TYPE") == "wayland"
DISPLAY = os.getenv("DISPLAY")

LOG_FILE = "Tech_Demo_One/card_swipes.csv"
card_swipe_df = pd.DataFrame(columns=["timestamp", "card id"])


def log_card_data(swipe_id):
    global card_swipe_df
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if (card_swipe_df["card id"] == swipe_id).any():
        print(f"Card {swipe_id} already logged")
    else:
        print(f"Logging new card: {swipe_id}")
        new_row = pd.DataFrame([{"timestamp": timestamp, "card id": swipe_id}])
        card_swipe_df = pd.concat([card_swipe_df, new_row], ignore_index=True)
        card_swipe_df.to_csv(LOG_FILE, index=False)
        print("✅ Card logged successfully")


# ==========================================================
# WAYLAND / HEADLESS VERSION (evdev)
# ==========================================================
if WAYLAND or not DISPLAY:
    from evdev import InputDevice, categorize, ecodes, list_devices

    def find_card_reader():
        for path in list_devices():
            dev = InputDevice(path)
            if any(keyword in dev.name.lower() for keyword in ["effron", "reader", "mag", "card"]):
                print(f"✅ Found card reader: {dev.name} ({path})")
                return dev
        raise RuntimeError("No card reader found. Try running with sudo or check connections.")

    print("Wayland detected — using evdev backend")
    dev = find_card_reader()

    card_data = ""
    print("Swipe your card (Ctrl+C to exit)...")

    try:
        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate == 1:  # key down
                    key = key_event.keycode.replace("KEY_", "")
                    # Handle ENTER (end of swipe)
                    if key in ["ENTER", "KPENTER"]:
                        swipe_id = card_data.strip(";?")
                        if swipe_id:
                            log_card_data(swipe_id)
                        card_data = ""
                    # Handle digits and symbols
                    elif len(key) == 1:
                        card_data += key
                    elif key.startswith("NUMERIC_"):
                        card_data += key[-1]  # NUMERIC_1 → 1
                    elif key in ["SEMICOLON", "SLASH", "QUESTION"]:
                        # Convert keycodes for typical magstripe symbols
                        if key == "SEMICOLON":
                            card_data += ";"
                        elif key == "QUESTION":
                            card_data += "?"
                        elif key == "SLASH":
                            card_data += "/"
    except KeyboardInterrupt:
        print("Exiting...")

# ==========================================================
# X11 VERSION (pynput)
# ==========================================================
else:
    from pynput import keyboard

    print("X11 detected — using pynput backend")

    card_data = ""

    def on_press(key):
        global card_data
        try:
            if key.char:
                card_data += key.char
                if key.char == "?":  # End sentinel
                    swipe_id = card_data.strip(";?")
                    if swipe_id:
                        log_card_data(swipe_id)
                    card_data = ""
        except AttributeError:
            if key == keyboard.Key.enter:
                if card_data.strip():
                    log_card_data(card_data.strip(";?"))
                card_data = ""
            elif key == keyboard.Key.esc:
                print("Exiting...")
                return False

    print("Swipe your card (Press ESC to exit)...")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
