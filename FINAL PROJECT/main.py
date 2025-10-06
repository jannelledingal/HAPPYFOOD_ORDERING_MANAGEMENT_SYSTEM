import tkinter as tk
from tkinter import ttk, messagebox
import db
from colors import PINK, LIGHT_PINK, WHITE, DARK_GRAY
from customer_menu import CustomerMenuWindow
from admin_menu import AdminMenuWindow

class HomePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=LIGHT_PINK)
        self.master = master
        self.create_widgets()
        try:
            self.master.state('zoomed')
        except Exception:
            pass

    def create_widgets(self):
        header = tk.Frame(self, bg=PINK, height=84)
        header.pack(fill="x")
        tk.Label(header, text="HappyFood.com", bg=PINK, fg=WHITE, font=("Helvetica", 20, "bold")).pack(side="left", padx=20)
        search_frame = tk.Frame(header, bg=PINK)
        search_frame.pack(side="right", padx=20)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=36).pack(side="left", padx=(0,8))
        ttk.Button(search_frame, text="Search", command=self.do_search).pack(side="left")

        hero = tk.Frame(self, bg=LIGHT_PINK)
        hero.pack(fill="x", padx=18, pady=12)
        tk.Label(hero, text="Delicious food to your day!", bg=LIGHT_PINK, fg=DARK_GRAY,
                 font=("Helvetica", 16, "bold")).pack(anchor="w")
        tk.Label(hero, text="Order from recommended meals, drinks and desserts", bg=LIGHT_PINK,
                 fg=DARK_GRAY, font=("Helvetica", 11)).pack(anchor="w", pady=(4,8))

        chips = tk.Frame(self, bg=LIGHT_PINK)
        chips.pack(fill="x", padx=18)
        for c in ("Recommended","Meals","Drinks","Desserts"):
            b = tk.Button(chips, text=c, bg=WHITE, fg=DARK_GRAY, bd=0,
                          relief="ridge", padx=10, pady=6,
                          command=lambda cat=c: self.open_customer(cat))
            b.pack(side="left", padx=6)

        actions = tk.Frame(self, bg=LIGHT_PINK)
        actions.pack(fill="x", padx=18, pady=12)
        tk.Button(actions, text="Order Food", bg=PINK, fg=WHITE, bd=0, padx=16, pady=8,
                  command=lambda: self.open_customer("Recommended")).pack(side="left", padx=6)
        tk.Button(actions, text="Administration", bg="#333", fg=WHITE, bd=0, padx=16, pady=8,
                  command=self.open_admin).pack(side="left", padx=6)

    def do_search(self):
        q = self.search_var.get().strip()
        if not q:
            messagebox.showinfo("Search", "Type something to search.")
            return
        self.open_customer("Recommended", query=q)

    def open_customer(self, category="Recommended", query=None):
        win = tk.Toplevel(self.master)
        win.configure(bg=WHITE)
        try:
            cm = CustomerMenuWindow(win, None, "Customer")
            try:
                if query:
                    cm.filter_query(query)
                else:
                    cm.load_category(category)
            except Exception:
                pass
            self.master.withdraw()
        except Exception:
            win.destroy()

    def open_admin(self):
        login = tk.Toplevel(self.master)
        login.title("Administration Login")
        login.configure(bg=WHITE)
        login.resizable(True, True)
        try:
            login.state('zoomed')
        except Exception:
            pass
        login.rowconfigure(0, weight=1)
        login.columnconfigure(0, weight=1)
        container = tk.Frame(login, bg=WHITE)
        container.grid(sticky="nsew", row=0, column=0, padx=12, pady=12)
        tk.Label(container, text="Administrator Login", font=("Helvetica", 13, "bold"), bg=WHITE, fg=DARK_GRAY).pack(pady=(12,6))
        frm = tk.Frame(container, bg=WHITE)
        frm.pack(padx=12, pady=6, fill="x")
        tk.Label(frm, text="Username", bg=WHITE).grid(row=0, column=0, sticky="w")
        user_ent = tk.Entry(frm); user_ent.grid(row=0, column=1, sticky="ew", padx=6)
        tk.Label(frm, text="Password", bg=WHITE).grid(row=1, column=0, sticky="w")
        pass_ent = tk.Entry(frm, show="*"); pass_ent.grid(row=1, column=1, sticky="ew", padx=6)
        frm.grid_columnconfigure(1, weight=1)
        btnf = tk.Frame(container, bg=WHITE)
        btnf.pack(fill="x", padx=12, pady=(6,12))
        def do_back():
            login.destroy()
        def do_login():
            username = user_ent.get().strip(); password = pass_ent.get().strip()
            if not username or not password:
                messagebox.showerror("Error","Enter username and password.")
                return
            try:
                user = db.verify_user(username, password)
            except Exception as e:
                messagebox.showerror("Error", f"DB error: {e}")
                return
            if not user or user.get("role") != "admin":
                messagebox.showerror("Login failed","Invalid admin credentials.")
                return
            login.destroy()
            admin_win = tk.Toplevel(self.master)
            on_back_cb = lambda: (admin_win.destroy(), self.master.deiconify())
            AdminMenuWindow(admin_win, user.get("id"), user.get("username"), on_back=on_back_cb)
            admin_win.protocol("WM_DELETE_WINDOW", on_back_cb)
            self.master.withdraw()
        tk.Button(btnf, text="Back", command=do_back, bg=WHITE, bd=0).pack(side="left")
        tk.Button(btnf, text="Login", command=do_login, bg=PINK, fg=WHITE, bd=0).pack(side="right")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("HappyFood")
    HomePage(root).pack(fill="both", expand=True)
    root.mainloop()