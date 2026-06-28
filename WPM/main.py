import curses
from curses import wrapper
import time
import random
import json
import os

# --- Constants ---
CHARS_PER_WORD = 5
MIN_ELAPSED = 1
HIGH_SCORE_FILE = "high_scores.json"
FALLBACK_TEXT = "The quick brown fox jumps over the lazy dog."


# --- High Score Helpers ---

# Loads high scores from disk. Returns a default dict if missing or corrupt.
def load_high_scores():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"best_wpm": 0, "best_accuracy": 0.0, "sessions": []}


# Updates best WPM/accuracy if beaten, appends session to history, saves to disk.
def save_high_score(wpm, accuracy):
    scores = load_high_scores()
    scores["best_wpm"] = max(scores["best_wpm"], wpm)
    scores["best_accuracy"] = max(scores["best_accuracy"], accuracy)
    scores["sessions"].append({"wpm": wpm, "accuracy": accuracy})
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            json.dump(scores, f)
    except IOError:
        pass


# --- Text Loading ---

# Picks a random line from wpm_texts.txt. Falls back to FALLBACK_TEXT if missing or empty.
def load_text():
    try:
        with open("wpm_texts.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        if not lines:
            return FALLBACK_TEXT
        line = random.choice(lines)
        return line.split(". ", 1)[-1]
    except FileNotFoundError:
        return FALLBACK_TEXT


# --- Stats Calculation ---

# Returns (wpm, accuracy, elapsed) from typed characters, target, and start timestamp.
def calculate_stats(current_text, target_text, start_time):
    time_elapsed = max(time.time() - start_time, MIN_ELAPSED)
    correct_chars = sum(1 for a, b in zip(current_text, target_text) if a == b)
    wpm = round((correct_chars / (time_elapsed / 60)) / CHARS_PER_WORD)
    errors = sum(1 for a, b in zip(current_text, target_text) if a != b)
    accuracy = round((1 - errors / max(len(current_text), 1)) * 100, 1)
    return wpm, accuracy, round(time_elapsed)


# --- Rendering ---

# Draws target text, stats bar, and colored typed characters. Green = correct, magenta = wrong.
def display_text(stdscr, target, current, wpm=0, accuracy=100.0):
    max_x = curses.COLS - 1
    max_y = curses.LINES - 1

    wrapped = []
    for i in range(0, len(target), max_x):
        wrapped.append(target[i:i + max_x])

    for row, line in enumerate(wrapped):
        if row >= max_y - 1:
            break
        stdscr.addstr(row, 0, line)

    stats_row = min(len(wrapped), max_y - 1)
    stdscr.addstr(stats_row, 0, f"WPM: {wpm} | Accuracy: {accuracy}%")

    for i, char in enumerate(current):
        row = i // max_x
        col = i % max_x
        if row >= max_y - 1:
            break
        correct_char = target[i]
        color = curses.color_pair(1) if char == correct_char else curses.color_pair(2)
        stdscr.addstr(row, col, char, color)

    cursor_pos = len(current)
    cursor_row = cursor_pos // max_x
    cursor_col = cursor_pos % max_x
    if cursor_row < max_y - 1:
        stdscr.move(cursor_row, cursor_col)


# --- Screens ---

# Shows welcome screen with all-time bests. Returns True to start, False on ESC.
def start_screen(stdscr):
    scores = load_high_scores()
    stdscr.clear()
    stdscr.addstr(0, 0, "Welcome to the Speed Typing Test!")
    stdscr.addstr(1, 0, f"Best WPM: {scores['best_wpm']}  |  Best Accuracy: {scores['best_accuracy']}%")
    stdscr.addstr(2, 0, "Press any key to begin, or ESC to quit.")
    stdscr.refresh()
    key = stdscr.getkey()
    return key != "\x1b"


# Shows final stats and highlights a new best. Returns True to retry, False on ESC.
def results_screen(stdscr, wpm, accuracy, elapsed):
    stdscr.clear()
    stdscr.addstr(0, 0, "  *** Test Complete! ***")
    stdscr.addstr(2, 0, f"  Time     : {elapsed}s")
    stdscr.addstr(3, 0, f"  WPM      : {wpm}")
    stdscr.addstr(4, 0, f"  Accuracy : {accuracy}%")

    scores = load_high_scores()
    if wpm >= scores["best_wpm"]:
        stdscr.addstr(6, 0, "  New best WPM!", curses.color_pair(1))

    stdscr.addstr(8, 0, "  Press any key to try again, or ESC to quit.")
    stdscr.refresh()
    key = stdscr.getkey()
    return key != "\x1b"


# --- Core Test Loop ---

# Runs one full typing test. Timer starts on first keypress. Returns (completed, wpm, accuracy, elapsed).
def wpm_test(stdscr):
    target_text = load_text()
    current_text = []
    start_time = None
    stdscr.nodelay(True)

    while True:
        if start_time is not None:
            wpm, accuracy, elapsed = calculate_stats(current_text, target_text, start_time)
        else:
            wpm, accuracy, elapsed = 0, 100.0, 0

        stdscr.clear()
        display_text(stdscr, target_text, current_text, wpm, accuracy)
        stdscr.refresh()

        if "".join(current_text) == target_text:
            stdscr.nodelay(False)
            save_high_score(wpm, accuracy)
            return True, wpm, accuracy, elapsed

        try:
            key = stdscr.getkey()
        except curses.error:
            continue

        if key == "\x1b":
            return False, 0, 0.0, 0

        if key in ("KEY_BACKSPACE", '\b', "\x7f", "\x08"):
            if current_text:
                current_text.pop()
        elif len(current_text) < len(target_text) and len(key) == 1:
            if start_time is None:
                start_time = time.time()
            current_text.append(key)


# --- Entry Point ---

# Sets up color pairs, then loops through start -> test -> results until the user quits.
def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    if not start_screen(stdscr):
        return

    while True:
        result, wpm, accuracy, elapsed = wpm_test(stdscr)
        if not result:
            break
        if not results_screen(stdscr, wpm, accuracy, elapsed):
            break


wrapper(main)