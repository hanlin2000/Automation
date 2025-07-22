import time
import sys

# Attempt to import pyautogui for cross-platform cursor position detection
try:
    import pyautogui
except ImportError:
    print("Error: pyautogui library is required. Install it with 'pip install pyautogui'.")
    sys.exit(1)

# Hide the cursor in the terminal (works on most Unix terminals)
def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

# Show the cursor again
def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

# Main loop to display cursor position
def main(poll_interval=0.1):
    try:
        hide_cursor()
        print("Press Ctrl-C to exit.")
        while True:
            x, y = pyautogui.position()
            # Move cursor to start of line and print coordinates
            sys.stdout.write(f"\rCursor position -> X: {x:4d}, Y: {y:4d}")
            sys.stdout.flush()
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        pass
    finally:
        # Ensure the cursor is shown again
        show_cursor()
        print("\nExiting...")

if __name__ == '__main__':
    main()
