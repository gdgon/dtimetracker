import tkinter as tk
from tkinter import ttk


class ChildWindow(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.transient(root)
        self.grab_set()
        # self.configure(bg='#33393B')

    def init_scrollbar(self, **frame_options):
        # Scrollbar stuff
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(frame_options)
        self.canvas = tk.Canvas(self.main_frame)
        # self.canvas.configure(bg='#33393B')
        self.subframe = ttk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(
            self.main_frame,
            orient='vertical',
            command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.subframe,
                                  anchor="nw", tags="subframe")

        self.subframe.bind(
            '<Configure>',
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))

        return {
            'main_frame': self.main_frame,
            'subframe': self.subframe,
            'canvas': self.canvas,
            'scrollbar': self.scrollbar
        }
