import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

TASKS_FILE = os.path.join(os.path.dirname(__file__), "config/tasks.json")


class TaskEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Task Editor")
        self.root.geometry("600x400")
        self.root.minsize(500, 300)

        self.tasks = self.load_tasks()
        self.setup_ui()

    def load_tasks(self):
        """Load existing tasks"""
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("tasks", [])
        return []

    def save_tasks(self):
        """Save tasks to JSON file"""
        data = {
            "task_types": {
                "bool": "True/False task",
                "numeric": "Number input task",
                "text": "Text input task",
            },
            "tasks": self.tasks,
        }

        os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        messagebox.showinfo("Saved", f"Tasks saved successfully")

    def setup_ui(self):
        """Configure user interface"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        title = ttk.Label(main_frame, text="Task Editor", font=("Arial", 14, "bold"))
        title.grid(row=0, column=0, pady=(0, 10))

        list_frame = ttk.LabelFrame(main_frame, text="Existing Tasks", padding="5")
        list_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.task_tree = ttk.Treeview(
            list_frame, columns=("Type",), show="tree headings", height=6
        )
        self.task_tree.heading("#0", text="Task")
        self.task_tree.heading("Type", text="Type")
        self.task_tree.column("#0", width=400)
        self.task_tree.column("Type", width=100)
        self.task_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.task_tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(list_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0))

        ttk.Button(btn_frame, text="Delete", command=self.delete_task).pack(
            side="left", padx=(0, 5)
        )

        form_frame = ttk.LabelFrame(main_frame, text="New Task", padding="5")
        form_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        form_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Task:").grid(
            row=0, column=0, sticky="nw", padx=(0, 5), pady=(0, 5)
        )
        self.task_text = scrolledtext.ScrolledText(form_frame, height=3, width=50)
        self.task_text.grid(row=0, column=1, sticky="ew", pady=(0, 5))

        ttk.Label(form_frame, text="Type:").grid(
            row=1, column=0, sticky="w", padx=(0, 5)
        )
        self.type_var = tk.StringVar(value="bool")
        type_combo = ttk.Combobox(
            form_frame,
            textvariable=self.type_var,
            values=["bool", "numeric", "text"],
            state="readonly",
            width=15,
        )
        type_combo.grid(row=1, column=1, sticky="w")

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(10, 0))

        ttk.Button(button_frame, text="Add Task", command=self.add_task).pack(
            side="left", padx=(0, 10)
        )
        ttk.Button(button_frame, text="Save All", command=self.save_tasks).pack(
            side="left"
        )

        self.refresh_task_list()

    def refresh_task_list(self):
        """Update task list"""
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        for task in self.tasks:
            self.task_tree.insert("", "end", text=task["task"], values=(task["type"],))

    def add_task(self):
        """Add new task"""
        task_text = self.task_text.get("1.0", "end-1c").strip()
        if not task_text:
            messagebox.showerror("Error", "Task description is required")
            return

        new_task = {"task": task_text, "type": self.type_var.get()}

        self.tasks.append(new_task)
        self.refresh_task_list()

        self.task_text.delete("1.0", "end")

        messagebox.showinfo("Success", "Task added successfully")

    def delete_task(self):
        """Delete selected task"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a task to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            index = self.task_tree.index(selection[0])
            del self.tasks[index]
            self.refresh_task_list()

    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    editor = TaskEditor()
    editor.run()
