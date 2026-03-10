from flask import Flask, render_template, request
import json
import os
from urllib.parse import urlparse
from pathlib import Path
import threading
import time
import logging
import click
click.echo = lambda *args, **kwargs: None

log = logging.getLogger('werkzeug')
log.disabled = True

logging.getLogger('flask.app').disabled = True

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"

app = Flask(
    __name__,
    template_folder=str(TEMPLATE_DIR),
    static_folder=str(STATIC_DIR)
)

CONFIG_FILE = "config/config.json"
TASKS_FILE = "config/tasks.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
            return {
                "url_path": "" if cfg.get("url_path") == "null" else cfg.get("url_path", ""),
                "img_path": "" if cfg.get("img_path") == "null" else cfg.get("img_path", ""),
                "port": "" if cfg.get("port") == "null" else cfg.get("port", "")
            }

    return {
        "url_path": "",
        "img_path": "",
        "port": ""
    }

def is_valid_url(url):
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and result.netloc
    except:
        return False
    
def shutdown_server():
    def shutdown():
        time.sleep(1)
        os._exit(0)
    threading.Thread(target=shutdown).start()


@app.route("/", methods=["GET", "POST"])
def setup():

    error = None
    success = False

    cfg = load_config()

    if request.method == "POST":

        url = request.form.get("url_path", "").strip() or "null"
        img = request.form.get("img_path", "").strip() or "null"
        port = request.form.get("port", "").strip() or "null"

        if url != "null" and img != "null":
            error = "Only URL or Image can be specified."

        elif url == "null" and img == "null":
            error = "You must specify URL or Image."

        elif url != "null" and not is_valid_url(url):
            error = "Invalid URL."

        elif port != "null" and not port.isdigit():
            error = "Port must be numeric."

        else:
            config = {
                "url_path": url,
                "img_path": img,
                "port": port,
            }

            os.makedirs("config", exist_ok=True)

            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)

            success = True

            shutdown_server()


    return render_template(
        "setup.html",
        error=error,
        success=success,
        cfg=cfg
    )

@app.route("/tasks", methods=["GET", "POST"])
def task_editor():

    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            tasks = data.get("tasks", [])
    else:
        tasks = []

    if request.method == "POST":

        action = request.form.get("action")

        if action == "add":

            task_text = request.form.get("task", "").strip()
            task_type = request.form.get("type")

            if task_text:
                tasks.append({"task": task_text, "type": task_type})

        if action == "delete":

            index = int(request.form.get("index"))
            if 0 <= index < len(tasks):
                tasks.pop(index)

        data = {
            "task_types": {
                "bool": "True/False task",
                "numeric": "Number input task",
                "text": "Text input task",
            },
            "tasks": tasks,
        }

        os.makedirs("config", exist_ok=True)

        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return render_template("tasks.html", tasks=tasks)


if __name__ == "__main__":
    app.run(port=5001)