import pandas as pd
from pynput import keyboard
from datetime import datetime

card_data = ""

# Path to the log file
LOG_FILE = "Tech_Demo_One/card_swipes.csv"

card_swipe_df = pd.DataFrame(columns=["timestamp", "card id"])

def log_card_data(swipe_id):
    global card_swipe_df
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if (card_swipe_df["card id"] == swipe_id).any():
        print(f"Card {swipe_id} already logged")
    else:
        print(f"Card {swipe_id} not logged, logging now")
        
        # Prepare the new row data
        card_swipe_new = {"timestamp": timestamp, "card id": swipe_id}
        
        # Create a temporary DataFrame for the new row
        card_swipe_new_df = pd.DataFrame([card_swipe_new])
        
        # Concatenate and assign the new DataFrame back to the global variable
        card_swipe_df = pd.concat([card_swipe_df, card_swipe_new_df], ignore_index=True)

        card_swipe_df.to_csv(LOG_FILE, index=False)

        print(f"Card logged: {swipe_id}")

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