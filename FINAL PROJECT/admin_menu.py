import os
import tkinter as tk
from tkinter import messagebox
import db
from colors import PINK, WHITE, DARK_GRAY

# Pillow optional
try:
    from PIL import Image, ImageTk
except Exception:
    Image = ImageTk = None

# Accessibility / theme
SIDEBAR_BTN_FONT = ("Helvetica", 14, "bold")
SIDEBAR_BTN_PADX = 14
SIDEBAR_BTN_PADY = 12
CARD_TITLE_FONT = ("Helvetica", 18, "bold")
CARD_SUB_FONT = ("Helvetica", 11)
LOGIN_INPUT_FONT = ("Helvetica", 14)
LOGIN_BTN_FONT = ("Helvetica", 14, "bold")

class AdminLoginDialog:
    """FoodPanda-themed admin login dialog (can be used from main.py)."""
    def __init__(self, parent, on_success=None):
        self.parent = parent
        self.on_success = on_success
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self._bg_path = self._find_asset("admin_dashboard") or self._find_asset("admin_bg") or self._find_asset("home_bg")
        self._create_window()

    def _find_asset(self, base_name):
        base = os.path.join(self.assets_dir, base_name)
        for ext in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
            p = base + ext
            if os.path.exists(p):
                return p
        if os.path.isdir(self.assets_dir):
            for f in os.listdir(self.assets_dir):
                if f.lower().startswith(base_name):
                    return os.path.join(self.assets_dir, f)
        return ""

    def _create_window(self):
        self.win = tk.Toplevel(self.parent)
        self.win.title("Admin Login")
        self.win.geometry("820x560")
        self.win.resizable(False, False)

        # background image if available
        if Image and self._bg_path and os.path.exists(self._bg_path):
            try:
                bg = Image.open(self._bg_path)
                bg = bg.resize((820, 560), Image.LANCZOS)
                self._bg_img = ImageTk.PhotoImage(bg)
                lbl = tk.Label(self.win, image=self._bg_img)
                lbl.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception:
                self.win.configure(bg=PINK)
        else:
            self.win.configure(bg=PINK)

        # central white card
        card = tk.Frame(self.win, bg=WHITE, bd=0)
        card.place(relx=0.5, rely=0.5, anchor="center", width=540, height=360)

        tk.Label(card, text="Administrator Login", bg=WHITE, fg=DARK_GRAY, font=CARD_TITLE_FONT).pack(pady=(18,6))
        tk.Label(card, text="Sign in to manage orders and menu", bg=WHITE, fg=DARK_GRAY, font=CARD_SUB_FONT).pack()

        frm = tk.Frame(card, bg=WHITE)
        frm.pack(padx=26, pady=18, fill="x")

        tk.Label(frm, text="Username", bg=WHITE, anchor="w", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w")
        self.user_ent = tk.Entry(frm, font=LOGIN_INPUT_FONT)
        self.user_ent.grid(row=0, column=1, sticky="ew", pady=8, padx=(12,0))

        tk.Label(frm, text="Password", bg=WHITE, anchor="w", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w")
        self.pass_ent = tk.Entry(frm, show="*", font=LOGIN_INPUT_FONT)
        self.pass_ent.grid(row=1, column=1, sticky="ew", pady=8, padx=(12,0))

        frm.columnconfigure(1, weight=1)

        # big accessible buttons
        btnf = tk.Frame(card, bg=WHITE)
        btnf.pack(fill="x", padx=26, pady=(6,18))
        back_btn = tk.Button(btnf, text="Back", bg="#efefef", fg=DARK_GRAY,
                             font=LOGIN_BTN_FONT, command=self._do_back, padx=16, pady=10)
        back_btn.pack(side="left", ipadx=6)
        login_btn = tk.Button(btnf, text="Login", bg=PINK, fg=WHITE,
                              font=LOGIN_BTN_FONT, command=self._do_login, padx=20, pady=10)
        login_btn.pack(side="right", ipadx=6)

        self.user_ent.focus_set()
        self.win.bind("<Return>", lambda e: self._do_login())

    def _do_back(self):
        try:
            self.win.destroy()
        except Exception:
            pass

    def _do_login(self):
        username = (self.user_ent.get() or "").strip()
        password = (self.pass_ent.get() or "").strip()
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
        # success
        try:
            if callable(self.on_success):
                self.on_success(user)
            self.win.destroy()
        except Exception:
            self.win.destroy()

class AdminMenuWindow:
    """Admin dashboard with larger, high-contrast buttons and a pre-expanded image panel."""
    def __init__(self, master, user_id=None, username="Admin", on_back=None):
        self.master = master
        self.user_id = user_id
        self.username = username
        self.on_back = on_back

        self.master.title("HappyFood - Admin")
        self.master.resizable(True, True)
        try:
            self.master.state("zoomed")
        except Exception:
            pass

        # layout: header, sidebar, content (content uses grid with fixed panel column)
        self.master.rowconfigure(0, weight=0)
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(1, weight=1)

        header = tk.Frame(self.master, bg=PINK, height=72)
        header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        tk.Label(header, text="HappyFood ADMINISTRATION", bg=PINK, fg=WHITE,
                 font=("Helvetica", 20, "bold")).pack(padx=16, pady=14, anchor="w")

        sidebar = tk.Frame(self.master, bg=WHITE, width=260)
        sidebar.grid(row=1, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        # Larger, accessible sidebar buttons
        def mkbtn(parent, text, cmd):
            b = tk.Button(parent, text=text, bg=PINK, fg=WHITE, bd=0,
                          font=SIDEBAR_BTN_FONT, command=cmd)
            b.pack(fill="x", pady=10, padx=16, ipady=8)
            return b

        mkbtn(sidebar, "📦  View Orders", self.view_orders)
        mkbtn(sidebar, "🍔  Manage Menu Items", self.manage_menu)
        mkbtn(sidebar, "🕒  Orders History", self.orders_history)

        tk.Button(sidebar, text="⬅️  Back", bg="#666", fg=WHITE, bd=0,
                  font=SIDEBAR_BTN_FONT, command=self.back_to_login).pack(side="bottom", fill="x", pady=12, padx=16, ipady=8)

        # content area: two-column grid, right column is fixed panel (pre-expanded)
        self.content = tk.Frame(self.master, bg=WHITE)
        self.content.grid(row=1, column=1, sticky="nsew", padx=(12,16), pady=12)
        self.content.rowconfigure(0, weight=0)
        self.content.rowconfigure(1, weight=1)
        self.content.columnconfigure(0, weight=1)
        PANEL_W, PANEL_H = 720, 460
        self.content.columnconfigure(1, weight=0, minsize=PANEL_W)

        # left: welcome and controls
        left = tk.Frame(self.content, bg=WHITE)
        left.grid(row=0, column=0, rowspan=2, sticky="nsew")
        tk.Label(left, text=f"Welcome, {username}", bg=WHITE, fg=DARK_GRAY,
                 font=("Helvetica", 16, "bold")).pack(anchor="nw", padx=12, pady=12)

        # right: image panel (fixed size so it is already expanded on show)
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self._panel_path = self._find_panel_image()
        self.panel_frame = tk.Frame(self.content, bg=WHITE, relief="ridge", bd=0, width=PANEL_W, height=PANEL_H)
        self.panel_frame.grid(row=0, column=1, rowspan=2, sticky="ne", padx=(12,0))
        self.panel_frame.grid_propagate(False)

        self.panel_label = tk.Label(self.panel_frame, bg=WHITE)
        self.panel_label.place(relx=0.5, rely=0.5, anchor="center")  # center the image

        # load image synchronously scaled to panel constants (fast for one-time load)
        self._panel_img = None
        if Image and self._panel_path and os.path.exists(self._panel_path):
            try:
                img = Image.open(self._panel_path)
                # preserve aspect and fit inside PANEL_W x PANEL_H
                img_ratio = img.width / img.height if img.height else 1
                panel_ratio = PANEL_W / PANEL_H
                if img_ratio > panel_ratio:
                    new_w = PANEL_W - 24
                    new_h = max(1, int(new_w / img_ratio))
                else:
                    new_h = PANEL_H - 24
                    new_w = max(1, int(new_h * img_ratio))
                img = img.resize((new_w, new_h), Image.LANCZOS)
                self._panel_img = ImageTk.PhotoImage(img)
                self.panel_label.config(image=self._panel_img)
            except Exception as e:
                print("Admin panel image load error:", e)
        else:
            placeholder = tk.Frame(self.panel_frame, bg="#f3f3f3")
            placeholder.place(relx=0.5, rely=0.5, anchor="center", width=PANEL_W-40, height=PANEL_H-40)

    def _find_panel_image(self):
        base = os.path.join(self.assets_dir, "admin_dashboard")
        for ext in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
            p = base + ext
            if os.path.exists(p):
                return p
        # fallback: any file starting with admin or home_bg
        if os.path.isdir(self.assets_dir):
            for f in os.listdir(self.assets_dir):
                if f.lower().startswith("admin") or f.lower().startswith("home_bg"):
                    return os.path.join(self.assets_dir, f)
        return ""

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
        # Return to homepage (do not open login dialog). If on_back callback provided, call it.
        if callable(self.on_back):
            try:
                self.on_back()
            except Exception:
                pass
            return
        # otherwise destroy this admin window and restore the main/root window
        try:
            top = self.master
            # destroy admin window
            try:
                top.destroy()
            except Exception:
                pass
            # try to find the root (assumed to be the application's main Tk)
            try:
                root = top.master
                if root:
                    try:
                        root.deiconify()
                    except Exception:
                        pass
            except Exception:
                pass
        except Exception:
            pass