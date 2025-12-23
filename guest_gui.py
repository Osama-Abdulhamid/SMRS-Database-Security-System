import tkinter as tk
from tkinter import ttk
import db_helper

class GuestWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Guest - Public Info")
        
        tree = ttk.Treeview(self, columns=("Course", "Info"), show='headings')
        tree.heading("Course", text="Course")
        tree.heading("Info", text="Public Description")
        tree.pack(fill='both', expand=True)

        rows = db_helper.execute_query("SELECT CourseName, PublicInfo FROM Course")
        for r in rows:
            tree.insert("", "end", values=(r['CourseName'], r['PublicInfo']))