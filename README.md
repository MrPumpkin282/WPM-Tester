# WPM-Tester

A lightweight, terminal-based speed typing test written in Python using the `curses` library. Test your typing speed, track your accuracy, and try to beat your highest Words Per Minute (WPM) directly from your command line.

## Features

* **Real-time Statistics:** Live calculation of your WPM and accuracy as you type.
* **Color-Coded Feedback:** Instant visual feedback (Green for correct keystrokes, Magenta for errors).
* **Persistent High Scores:** Automatically saves your best WPM and accuracy to a local JSON file to track your progress over time.
* **Dynamic Text Loading:** Randomly selects sentences from a custom text file, allowing you to easily add your own typing prompts.

---

## Prerequisites

This program uses Python's built-in `curses` library, which comes pre-installed on Linux and macOS. 

**For Windows Users:**
The standard Python installation on Windows does not include `curses`. You will need to install the `windows-curses` package to run this application.

```bash
pip install windows-curses
```

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MrPumpkin282/WPM-Tester.git
   cd WPM-Tester
   ```

2. **Run the script:**
   ```bash
   python main.py
   ```

---

## Customization

By default, the program looks for a file named `wpm_texts.txt` in the same directory to pull random typing prompts. 

To add your own text:
1. Create a file named `wpm_texts.txt` in the root directory.
2. Add your desired sentences or paragraphs, separating each prompt with a new line.
3. If the file is missing or empty, the program will automatically default to a standard fallback sentence: *"The quick brown fox jumps over the lazy dog."*

---

## File Structure

* `main.py` — The main application script containing the UI and game logic.
* `high_scores.json` — Auto-generated file that stores your best WPM, accuracy, and past session data.
* `wpm_texts.txt` — (Optional) User-created file containing custom typing prompts separated by new lines.

---

## How to Play

1. Launch the script from your terminal.
2. Press any key on the welcome screen to start the timer.
3. Type the text exactly as it appears on the screen. The timer starts the moment you press your first key.
4. If you make a mistake, you can use the `Backspace` key to correct it.
5. Finish the sentence to view your final stats. Press any key to play again, or `ESC` to quit at any time.

---

## License

This project is open-source and available under the [MIT License](LICENSE). Feel free to fork, modify, and improve it!
