import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import schedule
import time
import os
from main import run_specific_search, run_all_searches, update_global_index

class SystemTranscriptExtractorGUI:
    def __init__(self, master):
        self.master = master
        master.title("System Transcript Extractor")
        master.geometry("1200x700")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=1, fill="both")

        self.systems_frame = ttk.Frame(self.notebook)
        self.scheduler_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.systems_frame, text="System Types")
        self.notebook.add(self.scheduler_frame, text="Scheduler")

        self.create_systems_tab()
        self.create_scheduler_tab()

        self.load_config()

    def create_systems_tab(self):
        # Left frame for systems
        left_frame = ttk.Frame(self.systems_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(left_frame, text="System Types").pack()
        self.systems_frame = ttk.Frame(left_frame)
        self.systems_frame.pack(fill=tk.BOTH, expand=True)
        self.systems_canvas = tk.Canvas(self.systems_frame)
        self.systems_scrollbar = ttk.Scrollbar(self.systems_frame, orient="vertical", command=self.systems_canvas.yview)
        self.systems_scrollable_frame = ttk.Frame(self.systems_canvas)

        self.systems_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.systems_canvas.configure(
                scrollregion=self.systems_canvas.bbox("all")
            )
        )

        self.systems_canvas.create_window((0, 0), window=self.systems_scrollable_frame, anchor="nw")
        self.systems_canvas.configure(yscrollcommand=self.systems_scrollbar.set)

        self.systems_frame.pack(fill=tk.BOTH, expand=True)
        self.systems_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        self.systems_scrollbar.pack(side="right", fill="y")

        system_buttons_frame = ttk.Frame(left_frame)
        system_buttons_frame.pack(pady=10)

        ttk.Button(system_buttons_frame, text="Add System", command=self.add_system).pack(side=tk.LEFT, padx=5)
        ttk.Button(system_buttons_frame, text="Remove System", command=self.remove_system).pack(side=tk.LEFT, padx=5)

        # Right frame for searches
        right_frame = ttk.Frame(self.systems_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(right_frame, text="Search Queries").pack()
        self.searches_frame = ttk.Frame(right_frame)
        self.searches_frame.pack(fill=tk.BOTH, expand=True)
        self.searches_canvas = tk.Canvas(self.searches_frame)
        self.searches_scrollbar = ttk.Scrollbar(self.searches_frame, orient="vertical", command=self.searches_canvas.yview)
        self.searches_scrollable_frame = ttk.Frame(self.searches_canvas)

        self.searches_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.searches_canvas.configure(
                scrollregion=self.searches_canvas.bbox("all")
            )
        )

        self.searches_canvas.create_window((0, 0), window=self.searches_scrollable_frame, anchor="nw")
        self.searches_canvas.configure(yscrollcommand=self.searches_scrollbar.set)

        self.searches_frame.pack(fill=tk.BOTH, expand=True)
        self.searches_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        self.searches_scrollbar.pack(side="right", fill="y")

        search_buttons_frame = ttk.Frame(right_frame)
        search_buttons_frame.pack(pady=10)

        ttk.Button(search_buttons_frame, text="Add Search", command=self.add_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_buttons_frame, text="Edit Search", command=self.edit_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_buttons_frame, text="Remove Search", command=self.remove_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_buttons_frame, text="Run Selected Searches", command=self.run_selected_searches).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_buttons_frame, text="Update Global Index", command=self.update_global_index).pack(side=tk.LEFT, padx=5)

        # Search details frame
        self.search_details_frame = ttk.LabelFrame(right_frame, text="Search Details")
        self.search_details_frame.pack(fill=tk.X, pady=10)

        ttk.Label(self.search_details_frame, text="Query:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.query_entry = ttk.Entry(self.search_details_frame, width=80)
        self.query_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)

        ttk.Label(self.search_details_frame, text="YouTube Channel:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.channel_entry = ttk.Entry(self.search_details_frame, width=80)
        self.channel_entry.grid(row=1, column=1, padx=5, pady=5, columnspan=2)

        ttk.Label(self.search_details_frame, text="Output Directory:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.output_entry = ttk.Entry(self.search_details_frame, width=80)
        self.output_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.search_details_frame, text="Browse", command=self.browse_directory).grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(self.search_details_frame, text="Number of Videos:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.num_videos_entry = ttk.Entry(self.search_details_frame, width=10)
        self.num_videos_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(self.search_details_frame, text="Save Changes", command=self.save_search_changes).grid(row=4, column=1, pady=10)

    def create_scheduler_tab(self):
        self.schedule_var = tk.StringVar(value="02:00")
        ttk.Label(self.scheduler_frame, text="Schedule Time (HH:MM):").pack(pady=10)
        ttk.Entry(self.scheduler_frame, textvariable=self.schedule_var).pack(pady=5)

        self.scheduler_status_var = tk.StringVar(value="Scheduler is not running")
        ttk.Label(self.scheduler_frame, textvariable=self.scheduler_status_var).pack(pady=10)

        ttk.Button(self.scheduler_frame, text="Start Scheduler", command=self.start_scheduler).pack(pady=5)
        ttk.Button(self.scheduler_frame, text="Stop Scheduler", command=self.stop_scheduler).pack(pady=5)

    def load_config(self):
        try:
            with open('system_config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {"systems": [], "schedule_time": "02:00"}

        for widget in self.systems_scrollable_frame.winfo_children():
            widget.destroy()

        self.system_vars = []
        for system in self.config['systems']:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.systems_scrollable_frame, text=system['name'], variable=var, command=self.on_system_select)
            cb.pack(anchor="w")
            self.system_vars.append((var, system['name']))

        self.schedule_var.set(self.config.get('schedule_time', "02:00"))

    def save_config(self):
        with open('system_config.json', 'w') as f:
            json.dump(self.config, f, indent=2)

    def on_system_select(self):
        for widget in self.searches_scrollable_frame.winfo_children():
            widget.destroy()

        self.search_vars = []
        for system_var, system_name in self.system_vars:
            if system_var.get():
                system = next(s for s in self.config['systems'] if s['name'] == system_name)
                for search in system['searches']:
                    var = tk.BooleanVar()
                    cb = ttk.Checkbutton(self.searches_scrollable_frame, text=f"{system_name}: {search['query']}", variable=var)
                    cb.pack(anchor="w")
                    self.search_vars.append((var, system_name, search['query']))

        self.clear_search_details()

    def clear_search_details(self):
        self.query_entry.delete(0, tk.END)
        self.channel_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)
        self.num_videos_entry.delete(0, tk.END)

    def add_system(self):
        system_name = tk.simpledialog.askstring("Add System", "Enter system name:")
        if system_name:
            self.config['systems'].append({"name": system_name, "searches": []})
            self.save_config()
            self.load_config()
        messagebox.showinfo("Operation Complete", "System added successfully.")

    def remove_system(self):
        selected_systems = [name for var, name in self.system_vars if var.get()]
        if selected_systems:
            if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected systems?"):
                self.config['systems'] = [s for s in self.config['systems'] if s['name'] not in selected_systems]
                self.save_config()
                self.load_config()
                self.on_system_select()
                messagebox.showinfo("Operation Complete", "Selected systems removed successfully.")
        else:
            messagebox.showwarning("Warning", "Please select at least one system to remove.")

    def add_search(self):
        selected_systems = [name for var, name in self.system_vars if var.get()]
        if not selected_systems:
            messagebox.showwarning("Warning", "Please select at least one system first.")
            return
        self.clear_search_details()

    def edit_search(self):
        selected_searches = [search for var, _, search in self.search_vars if var.get()]
        if len(selected_searches) != 1:
            messagebox.showwarning("Warning", "Please select exactly one search to edit.")
            return
        system_name, search_query = next((system_name, search) for var, system_name, search in self.search_vars if var.get())
        system = next(s for s in self.config['systems'] if s['name'] == system_name)
        search = next(s for s in system['searches'] if s['query'] == search_query)
        
        self.query_entry.delete(0, tk.END)
        self.query_entry.insert(0, search['query'])
        self.channel_entry.delete(0, tk.END)
        self.channel_entry.insert(0, search.get('channel', ''))
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, search['output_directory'])
        self.num_videos_entry.delete(0, tk.END)
        self.num_videos_entry.insert(0, str(search['num_videos']))

    def remove_search(self):
        selected_searches = [(system_name, search) for var, system_name, search in self.search_vars if var.get()]
        if not selected_searches:
            messagebox.showwarning("Warning", "Please select at least one search to remove.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected searches?"):
            for system_name, search_query in selected_searches:
                system = next(s for s in self.config['systems'] if s['name'] == system_name)
                system['searches'] = [s for s in system['searches'] if s['query'] != search_query]
            self.save_config()
            self.on_system_select()
            self.clear_search_details()
            messagebox.showinfo("Operation Complete", "Selected searches removed successfully.")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, directory)
            update_global_index(directory)

    def save_search_changes(self):
        selected_systems = [name for var, name in self.system_vars if var.get()]
        if not selected_systems:
            messagebox.showwarning("Warning", "Please select at least one system first.")
            return

        query = self.query_entry.get()
        channel = self.channel_entry.get()
        output_dir = self.output_entry.get()
        try:
            num_videos = int(self.num_videos_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Number of videos must be an integer.")
            return

        search_data = {
            "query": query,
            "channel": channel,
            "output_directory": output_dir,
            "num_videos": num_videos
        }

        selected_searches = [(system_name, search) for var, system_name, search in self.search_vars if var.get()]
        if selected_searches:
            # Update existing searches
            for system_name, search_query in selected_searches:
                system = next(s for s in self.config['systems'] if s['name'] == system_name)
                for s in system['searches']:
                    if s['query'] == search_query:
                        s.update(search_data)
        else:
            # Add new search to selected systems
            for system_name in selected_systems:
                system = next(s for s in self.config['systems'] if s['name'] == system_name)
                system['searches'].append(search_data)

        self.save_config()
        self.on_system_select()
        update_global_index(output_dir)
        messagebox.showinfo("Operation Complete", "Search details saved successfully.")

    def run_selected_searches(self):
        selected_searches = [(system_name, search) for var, system_name, search in self.search_vars if var.get()]
        if not selected_searches:
            messagebox.showwarning("Warning", "Please select searches to run.")
            return

        searches_to_run = []
        for system_name, search_query in selected_searches:
            system = next(s for s in self.config['systems'] if s['name'] == system_name)
            search = next(s for s in system['searches'] if s['query'] == search_query)
            searches_to_run.append(search)

        threading.Thread(target=self.run_searches_thread, args=(searches_to_run,), daemon=True).start()

    def run_searches_thread(self, searches):
        for search in searches:
            run_specific_search(search['query'], search['output_directory'], search['num_videos'], search.get('channel', ''))
        self.master.after(0, lambda: messagebox.showinfo("Operation Complete", "Selected searches have been completed."))

    def update_global_index(self):
        for system in self.config['systems']:
            for search in system['searches']:
                update_global_index(search['output_directory'])
        messagebox.showinfo("Operation Complete", "Global index has been updated.")

    def start_scheduler(self):
        schedule_time = self.schedule_var.get()
        self.config['schedule_time'] = schedule_time
        self.save_config()

        schedule.clear()
        schedule.every().day.at(schedule_time).do(self.run_all_searches)
        
        self.scheduler_status_var.set(f"Scheduler is running. Next run at {schedule_time}")
        
        def scheduler_loop():
            while True:
                schedule.run_pending()
                time.sleep(60)

        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        messagebox.showinfo("Operation Complete", "Scheduler has been started.")

    def stop_scheduler(self):
        schedule.clear()
        self.scheduler_status_var.set("Scheduler is not running")
        messagebox.showinfo("Operation Complete", "Scheduler has been stopped.")

    def run_all_searches(self):
        run_all_searches()
        self.master.after(0, lambda: messagebox.showinfo("Operation Complete", "All scheduled searches have been completed."))

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemTranscriptExtractorGUI(root)
    root.mainloop()