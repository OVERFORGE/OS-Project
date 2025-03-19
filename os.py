import psutil
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque


class ProcessMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Process Monitoring Dashboard")
        self.root.geometry("900x700")  # Increased window size for graph
        self.root.resizable(False, False)  # Disable resizing

        # Apply a modern theme
        style = ttk.Style()
        style.theme_use("clam")  # Use a modern theme like 'clam'

        # Style configuration for Treeview
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        style.map("Treeview", background=[("selected", "#ececec")])

        # Style configuration for Labels
        style.configure("TLabel", font=("Arial", 12))

        # CPU and Memory Usage Labels
        self.cpu_label = ttk.Label(root, text="CPU Usage: 0%", style="TLabel")
        self.cpu_label.pack(pady=5)

        self.memory_label = ttk.Label(root, text="Memory Usage: 0%", style="TLabel")
        self.memory_label.pack(pady=5)

        # Process List
        self.tree = ttk.Treeview(root, columns=("PID", "Name", "CPU", "Memory"), show="headings", style="Treeview")
        self.tree.heading("PID", text="PID")
        self.tree.heading("Name", text="Process Name")
        self.tree.heading("CPU", text="CPU%")
        self.tree.heading("Memory", text="Memory%")
        self.tree.column("PID", width=50, anchor="center")
        self.tree.column("Name", width=200, anchor="w")
        self.tree.column("CPU", width=100, anchor="center")
        self.tree.column("Memory", width=100, anchor="center")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Refresh Button
        self.refresh_button = ttk.Button(root, text="Refresh", command=self.update_processes)
        self.refresh_button.pack(pady=5)

        # Add padding around widgets
        for widget in [self.cpu_label, self.memory_label, self.refresh_button]:
            widget.pack_configure(padx=10)

        # Graph for CPU and Memory Usage
        self.cpu_data = deque([0] * 60, maxlen=60)  # Store last 60 seconds of CPU data
        self.memory_data = deque([0] * 60, maxlen=60)  # Store last 60 seconds of Memory data

        self.fig, self.ax = plt.subplots(figsize=(8, 4))  # Increased graph size
        self.ax.set_title("CPU and Memory Usage Over Time")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Usage (%)")
        self.cpu_line, = self.ax.plot(self.cpu_data, label="CPU Usage", color="blue")
        self.memory_line, = self.ax.plot(self.memory_data, label="Memory Usage", color="green")
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=10, fill=tk.BOTH, expand=True)
        self.canvas_widget.update()  # Force layout update

        self.update_stats()
        self.update_processes()
        self.update_graph()

    def update_stats(self):
        """Update CPU and memory usage."""
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent

        self.cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
        self.memory_label.config(text=f"Memory Usage: {memory_usage}%")

        # Update graph data
        self.cpu_data.append(cpu_usage)
        self.memory_data.append(memory_usage)

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

    def update_graph(self):
        """Update the graph with new data."""
        self.cpu_line.set_ydata(self.cpu_data)
        self.memory_line.set_ydata(self.memory_data)
        self.ax.set_ylim(0, 100)  # Ensure the y-axis is always 0-100%
        self.ax.set_xlim(0, len(self.cpu_data))  # Adjust x-axis to fit data

        self.ax.relim()  # Recalculate limits
        self.ax.autoscale_view()  # Autoscale the view
        self.canvas.draw_idle()  # Explicitly refresh the canvas
        self.root.after(1000, self.update_graph)


if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessMonitor(root)
    root.mainloop()
