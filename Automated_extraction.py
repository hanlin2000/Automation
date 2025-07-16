import json
import time
from pynput import mouse, keyboard
from pynput.keyboard import Key, KeyCode

# Give 5 s to switch to the target window
time.sleep(5)
print("Start")

# Storage for events
recorded_actions = []
start_time = None

def get_timestamp():
    return time.time() - start_time

# Mouse event handlers
def on_click(x, y, button, pressed):
    if pressed:
        recorded_actions.append({
            "type": "click",
            "x": x, "y": y,
            "button": str(button),
            "time": get_timestamp()
        })

def on_scroll(x, y, dx, dy):
    recorded_actions.append({
        "type": "scroll",
        "x": x, "y": y,
        "dx": dx, "dy": dy,
        "time": get_timestamp()
    })


def on_press(key):
    # Stop recording on Esc
    if key == Key.esc:
        mouse_listener.stop()
        return False

    # Determine a sane string for every key
    if isinstance(key, KeyCode) and key.char is not None:
        key_str = key.char
    else:
        key_str = str(key)  

    recorded_actions.append({
        "type": "key_press",
        "key": key_str,
        "time": get_timestamp()
    })

def on_release(key):
    if key == Key.esc:
        return

    if isinstance(key, KeyCode) and key.char is not None:
        key_str = key.char
    else:
        key_str = str(key)

    recorded_actions.append({
        "type": "key_release",
        "key": key_str,
        "time": get_timestamp()
    })


# Initialize and start listeners
start_time = time.time()
mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

mouse_listener.start()
keyboard_listener.start()

# Block here until Esc triggers keyboard_listener to stop
keyboard_listener.join()

# At this point both listeners are stopped
with open("recorded_actions.json", "w") as f:
    json.dump(recorded_actions, f, indent=4)

print("Recording complete. Actions saved to recorded_actions.json")
