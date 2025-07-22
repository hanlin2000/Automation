import json
import time
import pyautogui
from pynput import keyboard as kb
from pynput.keyboard import Controller, Key
import itertools
import string

stop_requested = False

txt_path = input('.txt File path:\n')
json_path = input('.json File path:\n')


def on_global_key_press(key):
    global stop_requested
    if key == Key.esc:
        stop_requested = True
        # stop listening for further keys
        return False  

# start a listener thread that watches for Esc  
kb.Listener(on_press=on_global_key_press).start()

time.sleep(3)
print("Replaying recorded actions...")

# Load recorded actions + roll entries
with open(json_path, "r") as f:
    recorded_actions = json.load(f)


def dynamic_string_generator(custom_entries, length=1, infinity=False):
    """
    Yields combinations of strings:
      - Uses a base set of elements made up of ascii_letters, digits, and custom_entries
      - Generates all combinations of increasing length starting from min_length
    """
    # base_elements = list(custom_entries) + list(string.ascii_letters + string.digits)
    base_elements = list(custom_entries)
    if infinity:
        curr_length = length
        while True:
            for combo in itertools.product(base_elements, repeat=curr_length):
                yield ''.join(combo)
            curr_length += 1
    else:
        fixed_length = length 
        for combo in itertools.product(base_elements, repeat=fixed_length):
            yield ''.join(combo)



with open(txt_path, 'r') as file:
    custom = [line.strip() for line in file]
gen = dynamic_string_generator(custom, length=1, infinity=False)

#############
# Robo Time #
#############

keyboard = Controller()

def execute_action(action):
    t = action["type"]
    if t == "click":
        # Optional: Implement the if-else if dynamic clicking (image recognition) is desired
        if "image" in action:
            # try to find the button on‑screen
            loc = pyautogui.locateOnScreen(action["image"], confidence=0.9)
            if not loc:
                print(f"⚠️  Couldn’t find {action['image']} on screen — skipping click.")
                return

            cx, cy = pyautogui.center(loc)

            # special offsets per image
            if action["image"] == "Screenshots\Screenshot_dataset_button.jpg":
                px, py = cx, cy
            elif action["image"] == "Screenshots\Screenshot_sample_search.jpg":
                px, py = cx + 200, cy
            elif action["image"] == "Screenshots\Screenshot_simdist_loc.jpg" or "Screenshots\Screenshot_ghc_loc.jpg":
                px, py = cx - 35, cy
            elif action["image"] == "Screenshots\Screenshot_xlsx_export.jpg":
                px, py = cx, cy

            else:
                # default to center for any other image
                px, py = cx, cy

            pyautogui.click(px, py)
            print(f"Clicked {action['image']} at {(px, py)}")
            # time.sleep(5)
        else:
            # fall back to hard‑coded coordinates
            pyautogui.click(x=action["x"], y=action["y"])
            print(f"Clicked coords {(action['x'], action['y'])}")

    elif t == "scroll":
        pyautogui.scroll(action["dy"], x=action["x"], y=action["y"])
    elif t == "key_press":
        key = action.get("key")
        if not key:
            return
        if len(key) == 1:
            keyboard.press(key)
        elif key.startswith("Key."):
            name = key.split('.', 1)[1]
            special = getattr(Key, name, None)
            if special:
                keyboard.press(special)
    elif t == "key_release":
        key = action.get("key")
        if not key:
            return
        if len(key) == 1:
            keyboard.release(key)
        elif key.startswith("Key."):
            name = key.split('.', 1)[1]
            special = getattr(Key, name, None)
            if special:
                keyboard.release(special)

# UPDATE Jan 22, 2025: Use of ctrl_l to toggle when to replace, in case multiple replacements are required in one iteration
def replay_iteration(replacement_string):
    start = time.time()
    switch_on = False

    for i, action in enumerate(recorded_actions):
        # 1) allow immediate abort
        if stop_requested:
            raise KeyboardInterrupt

        # 2) preserve timing
        delay = action["time"] - (time.time() - start)
        if delay > 0:
            time.sleep(delay)

        # 3) toggle replacement mode on every 'replace' action
        if action["type"] == "replace":
            switch_on = not switch_on
            state = "Entering" if switch_on else "Exiting"
            print(f"{state} replacement mode")

            # when switching ON, inject the replacement string immediately
            if switch_on:
                for ch in replacement_string:
                    keyboard.press(ch)
                    keyboard.release(ch)
                    # time.sleep(0.05)
            continue  # skip any further handling of this action

        # 4) if in replacement mode, skip original alphanumeric key events
        if switch_on and action["type"] in ("key_press", "key_release"):
            k = action.get("key", "")
            if len(k) == 1:
                continue

        # 5) otherwise replay the action as before
        execute_action(action)
        print(f"Executed {i+1}/{len(recorded_actions)}: {action}")

    print(f"Iteration complete using “{replacement_string}”.")



try:
    i = 0
    while True:
        if stop_requested:
            raise KeyboardInterrupt
        
        next_string = next(gen)
        print(f"--- Iteration {i+1}: using {next_string} ---")
        replay_iteration(next_string)
        i += 1
        time.sleep(1)
except KeyboardInterrupt:
    print('exiting')

print("All iterations complete.")
