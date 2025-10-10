import os
import tkinter as tk
from tkinter import ttk, messagebox
import db
from colors import PINK, LIGHT_PINK, WHITE, DARK_GRAY, BLACK
from customer_menu import CustomerMenuWindow
from admin_menu import AdminMenuWindow

try:
    from PIL import Image, ImageTk
except Exception:
    Image = ImageTk = None

class HomePage(tk.Frame):
    
    PANEL_W = 760   
    PANEL_H = 480

    def __init__(self, master):
        super().__init__(master, bg=LIGHT_PINK)
        self.master = master
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self.bg_panel_path = self._find_asset("home_bg")
        self._panel_img = None

        # Preload panel image 
        if Image and self.bg_panel_path and os.path.exists(self.bg_panel_path):
            try:
                img = Image.open(self.bg_panel_path)
                img = self._fit_image(img, (self.PANEL_W - 12, self.PANEL_H - 12))
                self._panel_img = ImageTk.PhotoImage(img)
            except Exception as e:
                print("Panel preload error:", e)

        self.create_widgets()
        try:
            self.master.state('zoomed')
        except Exception:
            pass

    def _find_asset(self, base_name):
        base = os.path.join(self.assets_dir, base_name)
        for ext in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
            p = base + ext
            if os.path.exists(p):
                return p
        # fallback: look for file starting with base_name
        if os.path.isdir(self.assets_dir):
            for f in os.listdir(self.assets_dir):
                if f.lower().startswith(base_name):
                    return os.path.join(self.assets_dir, f)
        return ""

    def _fit_image(self, pil_img, max_size):
        max_w, max_h = max_size
        try:
            img_ratio = pil_img.width / pil_img.height if pil_img.height else 1
            panel_ratio = max_w / max_h if max_h else 1
            if img_ratio > panel_ratio:
                new_w = max_w
                new_h = max(1, int(max_w / img_ratio))
            else:
                new_h = max_h
                new_w = max(1, int(max_h * img_ratio))
            return pil_img.resize((new_w, new_h), Image.LANCZOS)
        except Exception:
            return pil_img

    def create_widgets(self):
        header = tk.Frame(self, bg=PINK, height=84)
        header.pack(fill="x")
        tk.Label(header, text="HappyFood.com", bg=PINK, fg=WHITE,
                 font=("Helvetica", 20, "bold")).pack(side="left", padx=20)
        search_frame = tk.Frame(header, bg=PINK)
        search_frame.pack(side="right", padx=20)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=36).pack(side="left", padx=(0,8))
        ttk.Button(search_frame, text="Search", command=self.do_search).pack(side="left")

        main_row = tk.Frame(self, bg=LIGHT_PINK)
        main_row.pack(fill="both", expand=True, padx=12, pady=12)
        main_row.rowconfigure(0, weight=1)
        main_row.columnconfigure(0, weight=1)
        main_row.columnconfigure(1, weight=0, minsize=self.PANEL_W)

        # left content
        left_col = tk.Frame(main_row, bg=LIGHT_PINK)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0,12))

        hero = tk.Frame(left_col, bg=LIGHT_PINK)
        hero.pack(fill="x", padx=6, pady=(0,8))
        tk.Label(hero, text="Delicious food to your day!", bg=LIGHT_PINK, fg=DARK_GRAY,
                 font=("Helvetica", 16, "bold")).pack(anchor="w")
        tk.Label(hero, text="Order from recommended meals, drinks and desserts", bg=LIGHT_PINK,
                 fg=DARK_GRAY, font=("Helvetica", 11)).pack(anchor="w", pady=(4,8))

        chips = tk.Frame(left_col, bg=LIGHT_PINK)
        chips.pack(fill="x", padx=6, pady=(0,8))
        for c in ("Recommended","Meals","Drinks","Desserts"):
            b = tk.Button(chips, text=c, bg=WHITE, fg=DARK_GRAY, bd=0,
                          relief="ridge", padx=10, pady=6,
                          command=lambda cat=c: self.open_customer(cat))
            b.pack(side="left", padx=6)

        actions = tk.Frame(left_col, bg=LIGHT_PINK)
        actions.pack(fill="x", padx=6, pady=(0,8))
        tk.Button(actions, text="Order Food", bg=PINK, fg=WHITE, bd=0, padx=16, pady=10,
                  command=lambda: self.open_customer("Recommended"), font=("Helvetica", 11, "bold")).pack(side="left", padx=6)
        tk.Button(actions, text="Administration", bg="#333", fg=WHITE, bd=0, padx=16, pady=10,
                  command=self.open_admin, font=("Helvetica", 11, "bold")).pack(side="left", padx=6)

        # right: pre-expanded image panel 
        self.panel_frame = tk.Frame(main_row, bg=BLACK, relief="ridge", bd=1, width=self.PANEL_W, height=self.PANEL_H)
        self.panel_frame.grid(row=0, column=1, sticky="nsew")
        self.panel_frame.grid_propagate(False)

        if self._panel_img:
            # center the image inside panel
            lbl = tk.Label(self.panel_frame, bg=BLACK, image=self._panel_img)
            lbl.image = self._panel_img
            lbl.place(relx=0.5, rely=0.5, anchor="center")
        else:
            # empty placeholder so layout is stable
            placeholder = tk.Frame(self.panel_frame, bg="#000000")
            placeholder.place(relx=0.5, rely=0.5, anchor="center", width=self.PANEL_W - 24, height=self.PANEL_H - 24)

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
        # Admin login 
        login = tk.Toplevel(self.master)
        login.title("Administration Login")
        login.geometry("780x520")
        login.resizable(False, False)
        assets_dir = self.assets_dir
        bg_path = self._find_asset("admin_dashboard")
        bg_img = None
        if Image and bg_path and os.path.exists(bg_path):
            try:
                img = Image.open(bg_path)
                img = self._fit_image(img, (780, 520))
                bg_img = ImageTk.PhotoImage(img)
            except Exception as e:
                print("Admin bg load error:", e)

        # background label
        if bg_img:
            bg_lbl = tk.Label(login, image=bg_img)
            bg_lbl.image = bg_img
            bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            login.configure(bg=WHITE)

        # central card for login fields (contrasting white card)
        card = tk.Frame(login, bg=WHITE, bd=0, relief="flat")
        card.place(relx=0.5, rely=0.5, anchor="center", width=520, height=320)

        # header inside card
        tk.Label(card, text="Administrator Login", bg=WHITE, fg=DARK_GRAY,
                 font=("Helvetica", 18, "bold")).pack(pady=(18,6))
        tk.Label(card, text="Sign in to manage orders and menu", bg=WHITE, fg=DARK_GRAY,
                 font=("Helvetica", 10)).pack()

        frm = tk.Frame(card, bg=WHITE)
        frm.pack(padx=20, pady=16, fill="x")

        tk.Label(frm, text="Username", bg=WHITE, anchor="w", font=("Helvetica", 11)).grid(row=0, column=0, sticky="w")
        user_ent = tk.Entry(frm, font=("Helvetica", 14))
        user_ent.grid(row=0, column=1, sticky="ew", pady=8, padx=(10,0))

        tk.Label(frm, text="Password", bg=WHITE, anchor="w", font=("Helvetica", 11)).grid(row=1, column=0, sticky="w")
        pass_ent = tk.Entry(frm, show="*", font=("Helvetica", 14))
        pass_ent.grid(row=1, column=1, sticky="ew", pady=8, padx=(10,0))

        frm.columnconfigure(1, weight=1)

        # large buttons for accessibility
        btn_frame = tk.Frame(card, bg=WHITE)
        btn_frame.pack(fill="x", padx=20, pady=(6,18))
        def do_back():
            login.destroy()
        def do_login():
            username = user_ent.get().strip()
            password = pass_ent.get().strip()
            if not username or not password:
                messagebox.showerror("Error", "Enter username and password.")
                return
            try:
                user = db.verify_user(username, password)
            except Exception as e:
                messagebox.showerror("Error", f"DB error: {e}")
                return
            if not user or user.get("role") != "admin":
                messagebox.showerror("Login failed", "Invalid admin credentials.")
                return
            login.destroy()
            admin_win = tk.Toplevel(self.master)
            on_back_cb = lambda: (admin_win.destroy(), self.master.deiconify())
            try:
                AdminMenuWindow(admin_win, user.get("id"), user.get("username"), on_back=on_back_cb)
            except TypeError:
                AdminMenuWindow(admin_win)
            admin_win.protocol("WM_DELETE_WINDOW", on_back_cb)
            self.master.withdraw()

        back_btn = tk.Button(btn_frame, text="Back", command=do_back,
                             bg="#f0f0f0", fg=DARK_GRAY, font=("Helvetica", 12), width=12, height=2)
        back_btn.pack(side="left", padx=(0,8))
        login_btn = tk.Button(btn_frame, text="Login", command=do_login,
                              bg=PINK, fg=WHITE, font=("Helvetica", 14, "bold"), width=18, height=2)
        login_btn.pack(side="right", padx=(8,0))

        # accessibility: focus on username
        user_ent.focus_set()
        # bind Enter to login
        login.bind("<Return>", lambda e: do_login())

if __name__ == "__main__":
    root = tk.Tk()
    root.title("HappyFood")
    HomePage(root).pack(fill="both", expand=True)
    root.mainloop()