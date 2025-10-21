from pynput import keyboard
from datetime import datetime

card_data = ""

# Path to the log file
LOG_FILE = "Tech_Demo_One/card_swipes.txt"

def log_card_data(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {data}\n")
    print(f"Card logged: {data}")

def on_press(key):
    global card_data
    try:
        if key.char:
            card_data += key.char
    except AttributeError:
        if key == keyboard.Key.enter:
            if card_data.strip():  # Avoid logging empty swipes
                log_card_data(card_data)
            card_data = ""  # Clear buffer
        elif key == keyboard.Key.esc:
            print("Exiting...")
            return False

print("Swipe your card (Press ESC to exit)...")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
