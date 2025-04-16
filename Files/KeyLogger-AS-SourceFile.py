import tkinter as tk
from pynput import keyboard
import threading
import time
import sys
from datetime import datetime
from pathlib import Path

# Global variables
log = []
duration = 60
log_box = None
timer_label = None
log_window = None

# ----------------- KEY LOGGER ----------------- #
def on_press(key):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        entry = f"[{timestamp}] {key.char}"
    except AttributeError:
        entry = f"[{timestamp}] [{key.name}]"
    log.append(entry)
    update_log_window(entry)

def write_log():
    try:
        desktop = Path.home() / "Desktop"
        filename = desktop / "KeyLogger-AS-Output.txt"
        with open(filename, "w") as f:
            f.write("\n".join(log))
        print(f"✅ Log saved to: {filename}")
    except Exception as e:
        print("❌ Failed to write log:", e)

# ----------------- GUI FUNCTIONS ----------------- #
def update_log_window(entry):
    if log_box:
        log_box.config(state="normal")
        log_box.insert("end", entry + "\n")
        log_box.see("end")
        log_box.config(state="disabled")

def show_log_window():
    def countdown():
        remaining = duration
        while remaining > 0:
            time.sleep(1)
            remaining -= 1
            try:
                timer_label.config(text=f"Recording... {remaining}s left")
            except:
                break
        try:
            log_window.destroy()
        except:
            pass

    global log_box, timer_label, log_window
    log_window = tk.Tk()
    log_window.title("Live Keylogger Monitor")
    log_window.geometry("600x400")
    log_window.configure(bg="#121212")

    timer_label = tk.Label(log_window, text="", fg="lime", bg="#121212", font=("Courier", 12, "bold"))
    timer_label.pack(pady=5)

    log_box = tk.Text(log_window, width=70, height=20, bg="black", fg="lime", font=("Courier", 10))
    log_box.pack(padx=10, pady=10)
    log_box.config(state="disabled")

    # Start countdown in background, GUI in main thread
    threading.Thread(target=countdown, daemon=True).start()
    log_window.mainloop()

    # After GUI ends, write log
    write_log()

# ----------------- DISCLAIMER ----------------- #
def show_disclaimer():
    def on_accept():
        disclaimer.destroy()
        threading.Thread(target=keyboard.Listener(on_press=on_press).run, daemon=True).start()
        show_log_window()

    def on_decline():
        disclaimer.destroy()
        sys.exit()

    def toggle_accept():
        accept_btn.config(state="normal" if agree_var.get() else "disabled")

    disclaimer = tk.Tk()
    disclaimer.title("Disclaimer")
    disclaimer.geometry("550x440")
    disclaimer.configure(bg="#1e1e1e")

    title = tk.Label(disclaimer, text="⚠ EDUCATIONAL USE ONLY ⚠", font=("Arial", 14, "bold"),
                     bg="#1e1e1e", fg="#ff5555")
    title.pack(pady=10)

    msg = (
        "This is a demonstration keylogger tool created for cybersecurity education only.\n\n"
        "By clicking 'Accept', you acknowledge:\n\n"
        "• All keystrokes will be recorded for 60 seconds\n"
        "• The output will be saved to your Desktop as 'KeyLogger-AS-Output.txt'\n\n"
        "⚠ Do NOT use this on devices you do not own or without explicit permission.\n"
        "⚠ This program is legal ONLY when used ethically and responsibly."
    )

    label = tk.Label(disclaimer, text=msg, wraplength=500, justify="left",
                     bg="#1e1e1e", fg="#ffffff", font=("Arial", 10))
    label.pack(pady=10)

    agree_var = tk.IntVar()
    check = tk.Checkbutton(disclaimer, text="I understand and accept the terms", variable=agree_var,
                           command=toggle_accept, bg="#1e1e1e", fg="white", selectcolor="#1e1e1e")
    check.pack(pady=5)

    btn_frame = tk.Frame(disclaimer, bg="#1e1e1e")
    btn_frame.pack(pady=20)

    accept_btn = tk.Button(btn_frame, text="Accept", command=on_accept, state="disabled",
                           bg="#4caf50", fg="white", width=12, font=("Arial", 10, "bold"))
    accept_btn.pack(side="left", padx=10)

    decline_btn = tk.Button(btn_frame, text="Decline", command=on_decline,
                            bg="#f44336", fg="white", width=12, font=("Arial", 10, "bold"))
    decline_btn.pack(side="right", padx=10)

    credit = tk.Label(disclaimer, text="Created by Adriel Sanchez.",
                      bg="#1e1e1e", fg="#888888", font=("Arial", 9, "italic"))
    credit.pack(side="bottom", pady=10)

    disclaimer.mainloop()

# ----------------- START PROGRAM ----------------- #
show_disclaimer()
