import psutil
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
import threading
import time


class ProcessMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Process Monitoring Dashboard")
        self.root.geometry("950x750")  
        self.root.configure(bg="#1e1e1e")  # Dark background
        self.root.resizable(False, False)

        # Theme colors
        self.dark_mode = True
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#0078D7"

        # Title Label
        self.title_label = tk.Label(root, text="🔍 Process Monitor", font=("Arial", 18, "bold"), fg=self.fg_color, bg=self.bg_color)
        self.title_label.pack(pady=10)

        # CPU and Memory Usage Labels
        self.cpu_label = tk.Label(root, text="CPU Usage: 0%", font=("Arial", 12), fg=self.fg_color, bg=self.bg_color)
        self.cpu_label.pack(pady=5)

        self.memory_label = tk.Label(root, text="Memory Usage: 0%", font=("Arial", 12), fg=self.fg_color, bg=self.bg_color)
        self.memory_label.pack(pady=5)

        # Search Bar
        self.search_frame = tk.Frame(root, bg=self.bg_color)
        self.search_frame.pack(pady=5)

        self.search_entry = tk.Entry(self.search_frame, font=("Arial", 12), width=30)
        self.search_entry.grid(row=0, column=0, padx=5)

        self.search_button = tk.Button(self.search_frame, text="🔍 Search", command=self.search_process, bg=self.accent_color, fg="white", font=("Arial", 11, "bold"), relief="ridge", padx=10)
        self.search_button.grid(row=0, column=1, padx=5)

        # Process List
        self.tree_frame = tk.Frame(root, bg=self.bg_color)
        self.tree_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.tree_frame, columns=("PID", "Name", "CPU", "Memory"), show="headings")
        self.tree.heading("PID", text="PID", anchor="center")
        self.tree.heading("Name", text="Process Name", anchor="w")
        self.tree.heading("CPU", text="CPU%", anchor="center")
        self.tree.heading("Memory", text="Memory%", anchor="center")

        self.tree.column("PID", width=70, anchor="center")
        self.tree.column("Name", width=250, anchor="w")
        self.tree.column("CPU", width=100, anchor="center")
        self.tree.column("Memory", width=100, anchor="center")

        # Add striped rows
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background=self.accent_color, foreground="white")
        style.map("Treeview", background=[("selected", "#444444")])

        self.tree.pack(pady=5, fill=tk.BOTH, expand=True)

        # Buttons Frame
        self.button_frame = tk.Frame(root, bg=self.bg_color)
        self.button_frame.pack(pady=5)

        self.refresh_button = tk.Button(self.button_frame, text="🔄 Refresh", command=self.update_processes, bg=self.accent_color, fg="white", font=("Arial", 11, "bold"), relief="ridge", padx=10)
        self.refresh_button.grid(row=0, column=0, padx=5)

        self.terminate_button = tk.Button(self.button_frame, text="❌ Kill Process", command=self.terminate_process, bg="#D9534F", fg="white", font=("Arial", 11, "bold"), relief="ridge", padx=10)
        self.terminate_button.grid(row=0, column=1, padx=5)

        self.sort_button = tk.Button(self.button_frame, text="📊 Sort by CPU%", command=self.sort_by_cpu, bg="#28A745", fg="white", font=("Arial", 11, "bold"), relief="ridge", padx=10)
        self.sort_button.grid(row=0, column=2, padx=5)

        self.toggle_theme_button = tk.Button(self.button_frame, text="🌙 Toggle Theme", command=self.toggle_theme, bg="#FFA500", fg="white", font=("Arial", 11, "bold"), relief="ridge", padx=10)
        self.toggle_theme_button.grid(row=0, column=3, padx=5)

        # Graph for CPU and Memory Usage
        self.cpu_data = deque([0] * 60, maxlen=60)
        self.memory_data = deque([0] * 60, maxlen=60)

        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.cpu_line, = self.ax.plot(self.cpu_data, label="CPU Usage", color="blue", linewidth=2)
        self.memory_line, = self.ax.plot(self.memory_data, label="Memory Usage", color="green", linewidth=2)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Usage (%)")
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=10, fill=tk.BOTH, expand=True)

        # Start threads for updating stats and processes
        self.update_stats_thread = threading.Thread(target=self.update_stats, daemon=True)
        self.update_processes_thread = threading.Thread(target=self.update_processes, daemon=True)
        self.update_graph_thread = threading.Thread(target=self.update_graph, daemon=True)

        self.update_stats_thread.start()
        self.update_processes_thread.start()
        self.update_graph_thread.start()

    def update_stats(self):
        """Update CPU and memory usage."""
        while True:
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent

            self.cpu_label.config(text=f"CPU Usage: {cpu_usage}%", fg=self.fg_color, bg=self.bg_color)
            self.memory_label.config(text=f"Memory Usage: {memory_usage}%", fg=self.fg_color, bg=self.bg_color)

            self.cpu_data.append(cpu_usage)
            self.memory_data.append(memory_usage)

            time.sleep(1)

    def update_processes(self):
        """Update the process list."""
        while True:
            current_processes = {proc.info['pid']: proc.info for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])}

            for row in self.tree.get_children():
                pid = int(self.tree.item(row, "values")[0])
                if pid in current_processes:
                    self.tree.item(row, values=(
                        pid, current_processes[pid]['name'], current_processes[pid]['cpu_percent'], f"{current_processes[pid]['memory_percent']:.2f}"))
                    del current_processes[pid]
                else:
                    self.tree.delete(row)

            for pid, proc_info in current_processes.items():
                self.tree.insert("", "end", values=(
                    pid, proc_info['name'], proc_info['cpu_percent'], f"{proc_info['memory_percent']:.2f}"))

            time.sleep(5)

    def update_graph(self):
        """Update the graph with new data."""
        while True:
            self.cpu_line.set_ydata(self.cpu_data)
            self.memory_line.set_ydata(self.memory_data)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw_idle()
            time.sleep(1)

    def terminate_process(self):
        """Terminate selected process."""
        selected = self.tree.selection()
        if selected:
            pid = self.tree.item(selected, "values")[0]
            try:
                psutil.Process(int(pid)).terminate()
                messagebox.showinfo("Success", f"Process {pid} terminated!")
                self.update_processes()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def sort_by_cpu(self):
        """Sort processes by CPU usage."""
        rows = [(self.tree.item(row, "values"), row) for row in self.tree.get_children()]
        rows.sort(key=lambda x: float(x[0][2]), reverse=True)
        for index, (_, row) in enumerate(rows):
            self.tree.move(row, "", index)

    def toggle_theme(self):
        """Toggle between light and dark mode."""
        if self.dark_mode:
            self.bg_color, self.fg_color = "#ffffff", "#000000"
        else:
            self.bg_color, self.fg_color = "#1e1e1e", "#ffffff"

        self.dark_mode = not self.dark_mode
        self.root.configure(bg=self.bg_color)

    def search_process(self):
        """Search for a process by name or PID."""
        search_term = self.search_entry.get().lower()
        for row in self.tree.get_children():
            pid, name, cpu, memory = self.tree.item(row, "values")
            if search_term in name.lower() or search_term == pid:
                self.tree.selection_set(row)
                self.tree.focus(row)
                self.tree.see(row)
                break
#New commit

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessMonitor(root)
    root.mainloop()
