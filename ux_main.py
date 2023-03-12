# -*- coding: utf-8 -*-
# Copyright (c) 2023 by wen-Huan.
# Date: 2023-03.01
#   - Ich, Liam und google :) ==> tío, esto es para ti
import os.path
import tkinter as tk
import tkinter.ttk as ttk
import windnd
import tkinter.messagebox as messagebox
from database_handle import FileDatabase
from file_identification import FileIdentification

class AnotarTodo:
    def __init__(self, master):
        # ========================================== tk root
        self.master = master
        self.version = "1.1.0"
        self.master.title(f"Anotar todo_{self.version}")
        self.master.geometry("1000x400")

        # Define the frame
        self.frame_top = ttk.Frame(self.master)
        self.frame_listbox = ttk.Frame(self.master)
        self.frame_buttons = ttk.Frame(self.master)
        self.frame_top.grid(row=0, column=0, sticky="nswe")
        self.frame_listbox.grid(row=0, column=0, sticky="nswe")
        self.frame_buttons.grid(row=1, column=0, sticky="nswe")


        # ========================================== tk weights
        # Define the left Treeview
        self.tree = ttk.Treeview(self.frame_listbox, columns=("filename", "path"))
        self.tree.heading("#0", text="item")
        self.tree.heading("filename", text="File Name")
        self.tree.heading("path", text="Path")
        self.tree.column("#0", width=50)
        self.tree.column("path", width=400)
        self.tree_label = ttk.Label(self.frame_listbox, text="drag file")
        self.tree_label.grid(row=0, column=0, sticky="nsew")
        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<ButtonRelease-1>", self.on_select)

        # Define the right Textbox
        self.text_label = ttk.Label(self.frame_listbox, text="comment")
        self.text_label.grid(row=0, column=1, sticky="nsew")
        self.text = tk.Text(self.frame_listbox, width=50)
        self.text.grid(row=1, column=1, sticky="nsew")
        self.text.bind("<KeyRelease>", self.update_file_note)

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

        # Define events
        windnd.hook_dropfiles(self.master, func=self.drag_files)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # ========================================== create database
        self.db = FileDatabase('catches_archivos.db')
        if not os.path.exists("catches_archivos.db"):
            self.db.add_file()

        # ========================================== function and callback
        # Read the Caches_archivos.json file and update the file_map dictionary and treeview.
        self.load_file_map()

    def get_file_info(self, file_path):
        if os.path.isfile(file_path):
            md5_hash = FileIdentification.get_file_md5(file_path)
            uuid = FileIdentification.get_file_id(file_path)
        else:
            md5_hash = file_path
            uuid = file_path
        return md5_hash, uuid, file_path

    def remove_file(self):
        """Removes the selected file from the treeview and from file_map."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to remove.")
            return

        for item in selection:
            filename = self.tree.item(item, "value")[1]
            md5 = self.file_map.get(filename).get("md5")
            uuid = self.file_map.get(filename).get("uuid")
            note = self.file_map.get(filename).get("note")
            self.db.update_file(md5, uuid, filename, note, show="F")
            del self.file_map[filename]
            self.tree.delete(item)
        self.text.delete("1.0", tk.END)


    def on_closing(self):
        """executed when the window is closed."""
        # Save files
        self.save_file_map()
        self.db.close_db()
        # Display prompt message
        if True: # messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.master.destroy()

    def load_file_map(self):
        """ Read cache when starting."""
        try:
            self.file_map = self.db.read_db_to_dict()
        except Exception as error:
            if DEBUG:
                raise error
            self.file_map = dict()
            messagebox.showerror("Error", f"oooops！an error occurred: {error}")

        for path, file_info in self.file_map.items():
            if os.path.exists(path):
                if not self.tree.exists(file_info['display']):
                    is_file = "F" if os.path.isfile(path) else "D"
                    self.tree.insert("", "end", text=is_file, values=(file_info['display'], path))

    def save_file_map(self):
        """save file map."""
        try:
            for val in self.file_map.values():
                md5 = val.get("md5")
                uuid = val.get("uuid")
                file_path = val.get("path")
                note = val.get("note", "")
                self.db.update_file(md5, uuid, file_path, note)
        except Exception as error:
            if DEBUG:
                raise error
            messagebox.showerror("Error", f"oooops！an error occurred: {error}")

    def drag_files(self, files):
        """drag files."""
        old_comment = ""
        for file in files:
            try:
                path = str(file.decode('gbk'))
                if path not in self.file_map:
                    display_name = os.path.basename(path)
                    is_file = "F" if os.path.isfile(path) else "D"
                    self.tree.insert("", "end", text=is_file, values=(display_name, path))
                    md5, uuid, file_path = self.get_file_info(path)
                    old_comment = self.db.update_file(md5, uuid, file_path)
                    self.file_map.update({path:{
                        'display': display_name, 'note': old_comment, "md5":md5, "uuid":uuid, "path":file_path}})
            except Exception as error:
                if DEBUG:
                    raise error
                messagebox.showerror("Error", f"oooops！an error occurred: {error}")
        self.show_comment(old_comment)
        return True

    def show_comment(self, note):
        if not note:
            note = ""
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, note)

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
        self.show_comment(note)

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
    DEBUG = False
    root = tk.Tk()
    # Set the grid layout to expand horizontally and vertically
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)
    anotar_todo = AnotarTodo(root)
    anotar_todo.run()
