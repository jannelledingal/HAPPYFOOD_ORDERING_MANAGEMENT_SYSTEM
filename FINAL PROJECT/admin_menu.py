import tkinter as tk
from tkinter import messagebox
from colors import PINK, LIGHT_PINK, WHITE, DARK_GRAY

class AdminMenuWindow:
    def __init__(self, master, user_id, username, on_back=None):
        self.master = master
        self.user_id = user_id
        self.username = username
        self.on_back = on_back
        self.master.title("HappyFood - Admin")
        self.master.resizable(True, True)
        try:
            self.master.state('zoomed')
        except Exception:
            pass
        self.master.rowconfigure(0, weight=0)
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(1, weight=1)
        header = tk.Frame(self.master, bg=PINK, height=72)
        header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        tk.Label(header, text="HappyFood ADMINISTRATION", bg=PINK, fg=WHITE, font=("Helvetica", 18, "bold")).pack(padx=12, pady=12, anchor="w")
        sidebar = tk.Frame(self.master, bg=WHITE, width=220)
        sidebar.grid(row=1, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        tk.Button(sidebar, text="📦 View Orders", bg=PINK, fg=WHITE, bd=0, command=self.view_orders, width=20).pack(pady=8)
        tk.Button(sidebar, text="🍔 Manage Menu Items", bg=PINK, fg=WHITE, bd=0, command=self.manage_menu, width=20).pack(pady=8)
        tk.Button(sidebar, text="🕒 Orders History", bg=PINK, fg=WHITE, bd=0, command=self.orders_history, width=20).pack(pady=8)
        tk.Button(sidebar, text="⬅️ Back", bg="#666", fg=WHITE, bd=0, command=self.back_to_login, width=20).pack(side="bottom", pady=12)
        self.content = tk.Frame(self.master, bg=WHITE)
        self.content.grid(row=1, column=1, sticky="nsew", padx=(8,12), pady=12)
        tk.Label(self.content, text=f"Welcome, {username}", bg=WHITE, fg=DARK_GRAY, font=("Helvetica",14,"bold")).pack(anchor="nw", padx=12, pady=8)

    def manage_menu(self):
        try:
            from admin_menu_manage import AdminMenuManageWindow
            AdminMenuManageWindow(self.master)
        except Exception as e:
            messagebox.showerror("Error", f"Manage Menu not available:\n{e}")

    def view_orders(self):
        try:
            from admin_orders import AdminOrdersWindow
            AdminOrdersWindow(self.master)
        except Exception as e:
            messagebox.showerror("Error", f"View Orders not available:\n{e}")

    def orders_history(self):
        try:
            from admin_history import AdminHistoryWindow
            AdminHistoryWindow(self.master)
        except Exception as e:
            messagebox.showerror("Error", f"Orders History not available:\n{e}")

    def back_to_login(self):
        if callable(self.on_back):
            try:
                self.on_back()
            except Exception:
                pass
        else:
            try:
                self.master.destroy()
                self.master.winfo_toplevel().deiconify()
            except Exception:
                pass