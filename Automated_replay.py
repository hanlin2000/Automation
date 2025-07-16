import json
import time
import pyautogui
from pynput import keyboard as kb
from pynput.keyboard import Controller, Key
import itertools
import string

stop_requested = False

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
with open("recorded_actions_LIMS.json", "r") as f:
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



with open('roll.txt', 'r') as file:
    custom = [line.strip() for line in file]
gen = dynamic_string_generator(custom, length=1, infinity=True)

#############
# Robo Time #
#############

keyboard = Controller()

def execute_action(action):
    t = action["type"]
    if t == "click":
        pyautogui.click(x=action["x"], y=action["y"])
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

        # 3) handle potential standalone Ctrl_L toggle
        if action["type"] == "key_press" and action.get("key") == "Key.ctrl_l":
            # peek at the very next event
            next_idx = i + 1
            if next_idx < len(recorded_actions):
                next_action = recorded_actions[next_idx]
                # if next event is the matching Ctrl_L release, treat as toggle
                if ( next_action["type"] == "key_release"
                     and next_action.get("key") == "Key.ctrl_l" ):
                    switch_on = not switch_on
                    print(f"{'Entering' if switch_on else 'Exiting'} replacement mode")
                    # only inject when turning ON
                    if switch_on:
                        for ch in replacement_string:
                            keyboard.press(ch)
                            keyboard.release(ch)
                            time.sleep(0.05)
                    # skip both this press and the next release
                    continue

            # otherwise it’s part of a chord—just replay it
            execute_action(action)
            print(f"Executed chord key_press: {action}")
            continue

        # 4) skip the Ctrl_L release if it was consumed by toggle logic
        if action["type"] == "key_release" and action.get("key") == "Key.ctrl_l":
            # but only skip if the previous press was treated as toggle
            # (we know toggle-releases are always immediately after the toggle-press)
            # so if switch mode just flipped, we’ll have skipped the press and now skip this.
            # Otherwise we fall through to replay below.
            prev_idx = i - 1
            if prev_idx >= 0:
                prev = recorded_actions[prev_idx]
                if ( prev["type"] == "key_press"
                     and prev.get("key") == "Key.ctrl_l"
                     and (recorded_actions.index(action) == recorded_actions.index(prev) + 1) ):
                    continue

        # 5) if in replacement mode, skip alphanumeric key events
        if switch_on and action["type"] in ("key_press", "key_release"):
            k = action.get("key", "")
            if len(k) == 1 and k.isalnum():
                continue

        # 6) otherwise replay
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
