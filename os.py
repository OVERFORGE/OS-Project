import psutil
import tkinter as tk
from tkinter import ttk


class ProcessMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Process Monitoring Dashboard")

        # CPU and Memory Usage Labels
        self.cpu_label = ttk.Label(root, text="CPU Usage: 0%", font=("Arial", 12))
        self.cpu_label.pack(pady=5)

        self.memory_label = ttk.Label(root, text="Memory Usage: 0%", font=("Arial", 12))
        self.memory_label.pack(pady=5)

        # Process List
        self.tree = ttk.Treeview(root, columns=("PID", "Name", "CPU", "Memory"), show="headings")
        self.tree.heading("PID", text="PID")
        self.tree.heading("Name", text="Process Name")
        self.tree.heading("CPU", text="CPU%")
        self.tree.heading("Memory", text="Memory%")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Refresh Button
        self.refresh_button = ttk.Button(root, text="Refresh", command=self.update_processes)
        self.refresh_button.pack(pady=5)

        self.update_stats()
        self.update_processes()

    def update_stats(self):
        """Update CPU and memory usage."""
        self.cpu_label.config(text=f"CPU Usage: {psutil.cpu_percent()}%")
        self.memory_label.config(text=f"Memory Usage: {psutil.virtual_memory().percent}%")
        self.root.after(1000, self.update_stats)

    def update_processes(self):
        """Update the process list."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                self.tree.insert("", "end", values=(
                proc.info['pid'], proc.info['name'], proc.info['cpu_percent'], f"{proc.info['memory_percent']:.2f}"))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        self.root.after(5000, self.update_processes)


if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessMonitor(root)
    root.mainloop()