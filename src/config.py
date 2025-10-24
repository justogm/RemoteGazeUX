import json
import os
import subprocess
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from urllib.parse import urlparse


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except:
        return False


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config/config.json")


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
            cfg = {k: (None if v == "null" else v) for k, v in cfg.items()}
            return cfg
    return {"url_path": None, "img_path": None, "port": None}


def save_config():
    url = url_var.get().strip() or "null"
    img = img_var.get().strip() or "null"
    port = port_var.get().strip() or "null"

    if url != "null" and img != "null":
        messagebox.showerror("Error", "Only URL or Image can have a value, not both.")
        return
    if url == "null" and img == "null":
        messagebox.showerror("Error", "You must specify at least URL or Image.")
        return

    if url != "null" and not is_valid_url(url):
        messagebox.showerror(
            "Error", "Invalid URL. Must start with http:// or https://"
        )
        return

    if port != "null" and not port.isdigit():
        messagebox.showerror("Error", "Port must be a number.")
        return

    config = {"url_path": url, "img_path": img, "port": port}

    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    messagebox.showinfo("Saved", f"Configuration saved to {CONFIG_FILE}")

    app.destroy()


def open_task_editor():
    """Open the task editor"""
    try:
        script_dir = os.path.dirname(__file__)
        task_editor_path = os.path.join(script_dir, "task_editor.py")
        subprocess.run(["python", task_editor_path], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open task editor: {e}")


def select_image():
    filename = filedialog.askopenfilename(
        title="Select Image", filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")]
    )
    if filename:
        img_var.set(filename)
        url_var.set("")


# -------- GUI --------
app = ttk.Window(themename="superhero")
app.title("Prototype Configuration")
app.geometry("550x300")
app.minsize(500, 250)

style = ttk.Style()
style.configure(".", font=("Roboto", 11))

cfg = load_config()

frame = ttk.Frame(app, padding=20)
frame.place(relx=0.5, rely=0.5, anchor="center")

ttk.Label(frame, text="URL Path:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
url_var = ttk.StringVar(value=cfg.get("url_path") or "")
url_entry = ttk.Entry(frame, textvariable=url_var, width=40)
url_entry.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(frame, text="Image Path:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
img_var = ttk.StringVar(value=cfg.get("img_path") or "")
img_entry = ttk.Entry(frame, textvariable=img_var, width=40)
img_entry.grid(row=1, column=1, padx=10, pady=5)
ttk.Button(frame, text="Browse...", bootstyle="secondary", command=select_image).grid(
    row=1, column=2, padx=5, pady=5
)

ttk.Label(frame, text="Port:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
port_var = ttk.StringVar(value=cfg.get("port") if cfg.get("port") != None else "")
ttk.Entry(frame, textvariable=port_var, width=10).grid(
    row=2, column=1, padx=10, pady=5, sticky="w"
)

ttk.Button(
    frame, text="Save Configuration", bootstyle="success", command=save_config
).grid(row=3, column=0, columnspan=3, pady=20)

ttk.Button(frame, text="Task Editor", bootstyle="info", command=open_task_editor).grid(
    row=4, column=0, columnspan=3, pady=10
)


# -------- Mutual exclusion --------
def on_url_change(*args):
    if url_var.get().strip():
        img_entry.config(state="disabled")
    else:
        img_entry.config(state="normal")


def on_img_change(*args):
    if img_var.get().strip():
        url_entry.config(state="disabled")
    else:
        url_entry.config(state="normal")


url_var.trace_add("write", on_url_change)
img_var.trace_add("write", on_img_change)

on_url_change()
on_img_change()

app.mainloop()
