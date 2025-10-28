import pandas as pd
from pynput import keyboard
from datetime import datetime
from pathlib import Path

card_data = ""

# Path to the log file
LOG_FILE = Path("Tech_Demo_One/card_swipes.csv")

# Verify a log file exists
if LOG_FILE.exists():

    # Notify of existance
    print(f"File '{LOG_FILE}' exists!")

else:

    # Notify of nonexistance and file creation
    print(f"File '{LOG_FILE}' does not exist, creating now.")

    # Name columns and create file
    card_swipe_df = pd.DataFrame(columns=["timestamp", "card id"])
    pd.to_csv(card_swipe_df)

# Read .csv log file
card_swipe_df = pd.read_csv(LOG_FILE)

# Function to log card data
def log_card_data(swipe_id):
    global card_swipe_df
    
    # Save date and time of locker use
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if swipe is already in log file
    if (card_swipe_df["card id"] == swipe_id).any():

        # Notify swipe is already logged
        print(f"Card {swipe_id} already logged")

    # If swipe is not in log file
    else:

        # Notifiy swipes is not logged, but will now be logged
        print(f"Card {swipe_id} not logged, logging now")
        
        # Prepare new row data with timestap and card id
        card_swipe_df.loc[len(card_swipe_df)] = {"timestamp": timestamp, "card id": swipe_id}

        # Save new card to log file
        card_swipe_df.to_csv(LOG_FILE, index=False)

        # Notify that card is now logged
        print(f"Card logged: {swipe_id}")

        # Notify system ready for new input
        print("Swipe your card (Press ESC to exit)...")

# Function to read swipe data
def on_press(key):
    global card_data

    try:
        # Det card data variable to new card swipe string
        if key.char:
            card_data += key.char
    
    # Excecute exceptions
    except AttributeError:
        if key == keyboard.Key.enter:
            if card_data.strip():  # Avoid logging empty swipes
                log_card_data(card_data)
            card_data = ""  # Clear buffer
        elif key == keyboard.Key.esc:
            print("Exiting...")
            return False

# Listen for cardswipe, save to listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()