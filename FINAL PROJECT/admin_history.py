import tkinter as tk
from tkinter import messagebox
import db
from colors import PINK, LIGHT_PINK, WHITE, DARK_GRAY

class AdminHistoryWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Orders History & Earnings")
        self.resizable(True, True)
        try:
            self.state('zoomed')
        except Exception:
            pass
        self.configure(bg=LIGHT_PINK)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_widgets()
        self.load_summary()

    def create_widgets(self):
        header = tk.Frame(self, bg=PINK, height=64)
        self.frm = tk.Frame(self)
        self.frm.grid(sticky="nsew", padx=12, pady=12)
        tk.Label(self.frm, text="🕒Orders Summary & Earnings", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")
        self.listbox = tk.Listbox(self.frm, height=10)
        self.listbox.grid(row=1, column=0, sticky="nsew", pady=(8,8))
        self.frm.rowconfigure(1, weight=1)
        btnf = tk.Frame(self.frm)
        btnf.grid(row=2, column=0, sticky="ew", pady=(4,0))
        tk.Button(btnf, text="Refresh", command=self.load_summary).pack(side="left", padx=4)
        tk.Button(btnf, text="Close", command=self.destroy).pack(side="right", padx=4)

    def load_summary(self):
        try:
            summary = db.get_orders_summary()
            self.listbox.delete(0, "end")
            for key in ("today","yesterday","week","month","year"):
                s = summary.get(key, {"count":0,"total":0.0})
                self.listbox.insert("end", f"{key.title():<10}  Orders: {s['count']:<4}   Earned: ₱{s['total']:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load summary: {e}")