# -*- coding: utf-8 -*-
# Copyright (c) 2023 by wen-Huan.
# Date: 2023-03.01
#   - Ich, Liam und google :) ==> tío, esto es para ti
import tkinter as tk
import tkinter.ttk as ttk
import windnd
import json
import tkinter.messagebox as messagebox


class AnotarTodo:
    def __init__(self, master):
        # ========================================== tk root
        self.master = master
        self.version = "1.0"
        self.master.title(f"Anotar todo_{self.version}")
        self.master.geometry("1000x400")

        # ========================================== tk weights
        # Define the left Treeview
        self.tree = ttk.Treeview(self.master, columns=("path",))
        self.tree.heading("#0", text="File Name")
        self.tree.heading("path", text="Path")
        self.tree.column("path", width=400)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<ButtonRelease-1>", self.on_select)

        # Define the right Textbox
        self.text = tk.Text(self.master, width=50)
        self.text.grid(row=0, column=1, sticky="nsew")
        self.text.bind("<KeyRelease>", self.update_file_note)

        # Define the frame of buttons
        self.frame_buttons = ttk.Frame(self.master)
        self.frame_buttons.grid(row=1, column=0, sticky="we")

        # Define the remove button
        self.delete_button = ttk.Button(self.frame_buttons, text="–", command=self.remove_file)
        self.delete_button.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="e")

        # Define the save button
        self.save_button = ttk.Button(self.frame_buttons, text="Save File Map", command=self.save_file_map)
        self.save_button.grid(row=0, column=3, columnspan=3, padx=5, pady=5, sticky="e")

        # Set weight
        self.frame_buttons.grid_columnconfigure(0, weight=1)

        # Define the global file dictionary
        self.file_map = dict()

        # ========================================== function and callback
        # Read the Caches_archivos.json file and update the file_map dictionary and treeview.
        self.load_file_map()

        # Define events
        windnd.hook_dropfiles(self.master, func=self.drag_files)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def remove_file(self):
        """Removes the selected file from the treeview and from file_map."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to remove.")
            return

        for item in selection:
            filename = self.tree.item(item, "value")[1]
            del self.file_map[filename]
            self.tree.delete(item)

    def on_closing(self):
        """executed when the window is closed."""
        # Save files
        self.save_file_map()

        # Display prompt message
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.master.destroy()

    def load_file_map(self):
        """ Read cache when starting."""
        try:
            with open('Caches_archivos.json', 'r') as f:
                self.file_map = json.load(f)
        except FileNotFoundError:
            print("no such file ==> Caches_archivos.json")
            return
        except Exception as error:
            messagebox.showerror("Error", f"oooops！an error occurred: {error}")

        for path, file_info in self.file_map.items():
            if not self.tree.exists(file_info['display']):
                self.tree.insert("", "end", text=file_info['display'], values=(file_info['display'], path))

    def save_file_map(self):
        """save file map."""
        try:
            with open('Caches_archivos.json', 'w') as f:
                json.dump(self.file_map, f, indent=4)
        except Exception as error:
            messagebox.showerror("Error", f"oooops！an error occurred: {error}")

    def drag_files(self, files):
        """drag files."""
        for file in files:
            try:
                path = str(file.decode('gbk'))
                if path not in self.file_map:
                    display_name = path.split('\\')[-1]
                    self.file_map.update({path:{'display': display_name, 'note': ''}})
                    self.tree.insert("", "end", text=display_name, values=(display_name, path))
            except Exception as error:
                messagebox.showerror("Error", f"oooops！an error occurred: {error}")
        return True

    def on_select(self, event):
        """Select an item to add notes and delete."""
        # Get the selected item
        if not self.tree.selection():
            return
        item = self.tree.selection()[0]
        # Get the full path of the item
        path = self.tree.item(item, "values")[1]
        # Display the note in the textbox
        note = self.file_map.get(path, {}).get("note", "")
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, note)

    def update_file_note(self, event=None):
        """Updates the dictionary when any character is entered."""

        # Get the currently selected item
        cur_item = self.tree.focus()

        # If no item is selected, do nothing
        if not cur_item:
            return

        # Get the full path of the currently selected item
        file_path = self.tree.item(cur_item)['values'][1]

        # Get all the characters in the textbox
        note_text = self.text.get("1.0", "end-1c")

        # Update the note for the corresponding file in the file_map
        self.file_map.get(file_path, {}).update({"note": note_text})

    def run(self):
        self.master.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    # Set the grid layout to expand horizontally and vertically
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)
    anotar_todo = AnotarTodo(root)
    anotar_todo.run()
