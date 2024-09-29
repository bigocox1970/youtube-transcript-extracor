import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import schedule
import time
import os
from main import run_specific_search, run_all_searches, update_global_index

class GenericTranscriptExtractorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Generic Transcript Extractor")
        master.geometry("1200x700")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=1, fill="both")

        self.things_frame = ttk.Frame(self.notebook)
        self.scheduler_frame = ttk.Frame(self.notebook)
        self.admin_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.things_frame, text="Things")
        self.notebook.add(self.scheduler_frame, text="Scheduler")
        self.notebook.add(self.admin_frame, text="Admin")

        self.create_things_tab()
        self.create_scheduler_tab()
        self.create_admin_tab()

        self.load_config()

    def create_things_tab(self):
        # Left frame for things
        left_frame = ttk.Frame(self.things_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.things_label = ttk.Label(left_frame, text="Things")
        self.things_label.pack()
        self.things_frame = ttk.Frame(left_frame)
        self.things_frame.pack(fill=tk.BOTH, expand=True)
        self.things_canvas = tk.Canvas(self.things_frame)
        self.things_scrollbar = ttk.Scrollbar(self.things_frame, orient="vertical", command=self.things_canvas.yview)
        self.things_scrollable_frame = ttk.Frame(self.things_canvas)

        self.things_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.things_canvas.configure(
                scrollregion=self.things_canvas.bbox("all")
            )
        )

        self.things_canvas.create_window((0, 0), window=self.things_scrollable_frame, anchor="nw")
        self.things_canvas.configure(yscrollcommand=self.things_scrollbar.set)

        self.things_frame.pack(fill=tk.BOTH, expand=True)
        self.things_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        self.things_scrollbar.pack(side="right", fill="y")

        thing_buttons_frame = ttk.Frame(left_frame)
        thing_buttons_frame.pack(pady=10)

        self.add_thing_button = ttk.Button(thing_buttons_frame, text="Add Thing", command=self.add_thing)
        self.add_thing_button.pack(side=tk.LEFT, padx=5)
        self.remove_thing_button = ttk.Button(thing_buttons_frame, text="Remove Thing", command=self.remove_thing)
        self.remove_thing_button.pack(side=tk.LEFT, padx=5)

        # Right frame for searches
        right_frame = ttk.Frame(self.things_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.searches_label = ttk.Label(right_frame, text="Search Queries")
        self.searches_label.pack()
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

        self.add_search_button = ttk.Button(search_buttons_frame, text="Add Search", command=self.add_search)
        self.add_search_button.pack(side=tk.LEFT, padx=5)
        self.edit_search_button = ttk.Button(search_buttons_frame, text="Edit Search", command=self.edit_search)
        self.edit_search_button.pack(side=tk.LEFT, padx=5)
        self.remove_search_button = ttk.Button(search_buttons_frame, text="Remove Search", command=self.remove_search)
        self.remove_search_button.pack(side=tk.LEFT, padx=5)
        self.run_searches_button = ttk.Button(search_buttons_frame, text="Run Selected Searches", command=self.run_selected_searches)
        self.run_searches_button.pack(side=tk.LEFT, padx=5)
        self.update_index_button = ttk.Button(search_buttons_frame, text="Update Global Index", command=self.update_global_index)
        self.update_index_button.pack(side=tk.LEFT, padx=5)

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

    def create_admin_tab(self):
        ttk.Label(self.admin_frame, text="Custom Labels").pack(pady=10)

        label_frame = ttk.Frame(self.admin_frame)
        label_frame.pack(pady=10)

        ttk.Label(label_frame, text="Things Label:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.things_label_entry = ttk.Entry(label_frame, width=30)
        self.things_label_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(label_frame, text="Add Thing Label:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.add_thing_label_entry = ttk.Entry(label_frame, width=30)
        self.add_thing_label_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(label_frame, text="Remove Thing Label:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.remove_thing_label_entry = ttk.Entry(label_frame, width=30)
        self.remove_thing_label_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(self.admin_frame, text="Save Labels", command=self.save_labels).pack(pady=10)

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "things": [],
                "schedule_time": "02:00",
                "labels": {
                    "things": "Things",
                    "add_thing": "Add Thing",
                    "remove_thing": "Remove Thing"
                }
            }

        self.update_labels()
        self.load_things()
        self.schedule_var.set(self.config.get('schedule_time', "02:00"))

        # Load labels into admin tab
        self.things_label_entry.delete(0, tk.END)
        self.things_label_entry.insert(0, self.config['labels']['things'])
        self.add_thing_label_entry.delete(0, tk.END)
        self.add_thing_label_entry.insert(0, self.config['labels']['add_thing'])
        self.remove_thing_label_entry.delete(0, tk.END)
        self.remove_thing_label_entry.insert(0, self.config['labels']['remove_thing'])

    def save_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=2)

    def update_labels(self):
        self.things_label.config(text=self.config['labels']['things'])
        self.add_thing_button.config(text=self.config['labels']['add_thing'])
        self.remove_thing_button.config(text=self.config['labels']['remove_thing'])
        self.notebook.tab(0, text=self.config['labels']['things'])

    def save_labels(self):
        self.config['labels']['things'] = self.things_label_entry.get()
        self.config['labels']['add_thing'] = self.add_thing_label_entry.get()
        self.config['labels']['remove_thing'] = self.remove_thing_label_entry.get()
        self.save_config()
        self.update_labels()
        messagebox.showinfo("Success", "Labels updated successfully")

    def load_things(self):
        for widget in self.things_scrollable_frame.winfo_children():
            widget.destroy()

        self.thing_vars = []
        for thing in self.config['things']:
            frame = ttk.Frame(self.things_scrollable_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(frame, variable=var)
            cb.pack(side=tk.LEFT)
            
            label = ttk.Label(frame, text=thing['name'])
            label.pack(side=tk.LEFT)
            label.bind("<Button-1>", lambda e, name=thing['name']: self.display_searches(name))
            
            self.thing_vars.append((var, thing['name']))

    def display_searches(self, thing_name):
        for widget in self.searches_scrollable_frame.winfo_children():
            widget.destroy()

        self.search_vars = []
        thing = next(t for t in self.config['things'] if t['name'] == thing_name)
        for search in thing['searches']:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.searches_scrollable_frame, text=f"{search['query']}", variable=var)
            cb.pack(anchor="w")
            self.search_vars.append((var, thing_name, search['query']))

        self.clear_search_details()

    def clear_search_details(self):
        self.query_entry.delete(0, tk.END)
        self.channel_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)
        self.num_videos_entry.delete(0, tk.END)

    def add_thing(self):
        thing_name = tk.simpledialog.askstring("Add Thing", f"Enter {self.config['labels']['things']} name:")
        if thing_name:
            self.config['things'].append({"name": thing_name, "searches": []})
            self.save_config()
            self.load_things()
        messagebox.showinfo("Operation Complete", f"{self.config['labels']['things']} added successfully.")

    def remove_thing(self):
        selected_things = [name for var, name in self.thing_vars if var.get()]
        if selected_things:
            if messagebox.askyesno("Confirm", f"Are you sure you want to remove the selected {self.config['labels']['things']}?"):
                self.config['things'] = [t for t in self.config['things'] if t['name'] not in selected_things]
                self.save_config()
                self.load_things()
                for widget in self.searches_scrollable_frame.winfo_children():
                    widget.destroy()
                messagebox.showinfo("Operation Complete", f"Selected {self.config['labels']['things']} removed successfully.")
        else:
            messagebox.showwarning("Warning", f"Please select at least one {self.config['labels']['things']} to remove.")

    def add_search(self):
        selected_things = [name for var, name in self.thing_vars if var.get()]
        if not selected_things:
            messagebox.showwarning("Warning", f"Please select at least one {self.config['labels']['things']} first.")
            return
        self.clear_search_details()

    def edit_search(self):
        selected_searches = [search for var, _, search in self.search_vars if var.get()]
        if len(selected_searches) != 1:
            messagebox.showwarning("Warning", "Please select exactly one search to edit.")
            return
        thing_name, search_query = next((thing_name, search) for var, thing_name, search in self.search_vars if var.get())
        thing = next(t for t in self.config['things'] if t['name'] == thing_name)
        search = next(s for s in thing['searches'] if s['query'] == search_query)
        
        self.query_entry.delete(0, tk.END)
        self.query_entry.insert(0, search['query'])
        self.channel_entry.delete(0, tk.END)
        self.channel_entry.insert(0, search.get('channel', ''))
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, search['output_directory'])
        self.num_videos_entry.delete(0, tk.END)
        self.num_videos_entry.insert(0, str(search['num_videos']))

    def remove_search(self):
        selected_searches = [(thing_name, search) for var, thing_name, search in self.search_vars if var.get()]
        if not selected_searches:
            messagebox.showwarning("Warning", "Please select at least one search to remove.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected searches?"):
            for thing_name, search_query in selected_searches:
                thing = next(t for t in self.config['things'] if t['name'] == thing_name)
                thing['searches'] = [s for s in thing['searches'] if s['query'] != search_query]
            self.save_config()
            self.display_searches(thing_name)
            self.clear_search_details()
            messagebox.showinfo("Operation Complete", "Selected searches removed successfully.")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, directory)
            update_global_index(directory)

    def save_search_changes(self):
        selected_things = [name for var, name in self.thing_vars if var.get()]
        if not selected_things:
            messagebox.showwarning("Warning", f"Please select at least one {self.config['labels']['things']} first.")
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

        selected_searches = [(thing_name, search) for var, thing_name, search in self.search_vars if var.get()]
        if selected_searches:
            # Update existing searches
            for thing_name, search_query in selected_searches:
                thing = next(t for t in self.config['things'] if t['name'] == thing_name)
                for s in thing['searches']:
                    if s['query'] == search_query:
                        s.update(search_data)
        else:
            # Add new search to selected things
            for thing_name in selected_things:
                thing = next(t for t in self.config['things'] if t['name'] == thing_name)
                thing['searches'].append(search_data)

        self.save_config()
        if selected_searches:
            self.display_searches(selected_searches[0][0])
        update_global_index(output_dir)
        messagebox.showinfo("Operation Complete", "Search details saved successfully.")

    def run_selected_searches(self):
        selected_searches = [(thing_name, search) for var, thing_name, search in self.search_vars if var.get()]
        if not selected_searches:
            messagebox.showwarning("Warning", "Please select searches to run.")
            return

        searches_to_run = []
        for thing_name, search_query in selected_searches:
            thing = next(t for t in self.config['things'] if t['name'] == thing_name)
            search = next(s for s in thing['searches'] if s['query'] == search_query)
            searches_to_run.append(search)

        threading.Thread(target=self.run_searches_thread, args=(searches_to_run,), daemon=True).start()

    def run_searches_thread(self, searches):
        for search in searches:
            run_specific_search(search['query'], search['output_directory'], search['num_videos'], search.get('channel', ''))
        self.master.after(0, lambda: messagebox.showinfo("Operation Complete", "Selected searches have been completed."))

    def update_global_index(self):
        for thing in self.config['things']:
            for search in thing['searches']:
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
    app = GenericTranscriptExtractorGUI(root)
    root.mainloop()