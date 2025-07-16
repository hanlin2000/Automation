# Automated Action Recorder and Replayer

This project provides tools to record and replay keyboard and mouse actions using Python.

## Features

- **Automated_extraction.py**  
  Records mouse movements, clicks, and keyboard inputs. All actions are logged in `recorded_actions.json`.  
  - To start recording, simply run the script.
  - Recording will continue indefinitely until manually stopped.
  - Press the `Esc` key to terminate the recording session.

- **Automated_replay.py**  
  Reads from `recorded_actions.json` and replays the recorded sequence of actions exactly as captured.

- **Replacement Mode**

This project includes a *replacement mode* that allows users to insert variable content during replay.

#### How It Works

1. **During Recording (`Automated_extraction.py`)**:
   - The `Ctrl` key is used as a **toggle** for *replacement mode*.
   - By default, replacement mode is **off**.
   - To insert a replaceable section:
     - Press and release `Ctrl` → replacement mode turns **on**
     - Type any placeholder or dummy content
     - Press and release `Ctrl` again → replacement mode turns **off**
   - The script will log this section as a replaceable block.

2. **During Replay (`Automated_replay.py`)**:
   - The script will detect replacement sections and substitute them with actual content.
   - Replacement values are read from `roll.txt`, which should contain **one replacement value per line**.
   - The script will iterate through the recorded actions for each line in `roll.txt`, producing multiple unique replays with varying inputs.


## Setup Instructions

1. **Install Dependencies**

   Before running the scripts, make sure to install the required Python packages:

   ```bash
   pip install -r requirements.txt
