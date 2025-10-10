PINK = "#E21B70"
LIGHT_PINK = "#FBE4F0"
WHITE = "#FFFFFF"
DARK_GRAY = "#333333"
BLACK = "#000000"
FONT = ("Helvetica", 11)

import tkinter as tk
class FoodFrameStyle(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=LIGHT_PINK, bd=0, highlightthickness=0, **kwargs)
        self.config(padx=18, pady=18)