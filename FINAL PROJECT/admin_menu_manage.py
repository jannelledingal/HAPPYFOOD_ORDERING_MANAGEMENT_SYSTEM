import tkinter as tk
from tkinter import ttk, messagebox
import db
from colors import PINK, LIGHT_PINK, WHITE, DARK_GRAY

# Accessibility 
BTN_FONT = ("Helvetica", 13, "bold")
BTN_PADX = 12
BTN_PADY = 10
TREE_ROWHEIGHT = 34
HEADING_FONT = ("Helvetica", 12, "bold")

class AdminMenuManageWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Manage Menu Items")
        self.resizable(True, True)
        try:
            self.state('zoomed')
        except Exception:
            pass
        self.configure(bg=LIGHT_PINK)

        # state
        self.all_rows = []
        self._sort_state = {"column": None, "reverse": False}

        # layout
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self.create_widgets()
        self.load_menu()

    def create_widgets(self):
        header = tk.Frame(self, bg=PINK, height=64)
        header.grid(row=0, column=0, sticky="nsew")
        tk.Label(header, text="🍔 Manage Menu Items", bg=PINK, fg=WHITE,
                 font=("Helvetica", 16, "bold")).pack(side="left", padx=12, pady=12)

        topf = tk.Frame(self, bg=WHITE)
        topf.grid(row=1, column=0, sticky="ew", padx=12, pady=10)

        # search + sort controls
        self.search_var = tk.StringVar()
        ttk.Entry(topf, textvariable=self.search_var, width=36).pack(side="left", padx=(6,8))
        self.sort_var = tk.StringVar(value="Default")
        tk.OptionMenu(topf, self.sort_var, "Default", "Price: Low → High", "Price: High → Low", "Name: A → Z").pack(side="left", padx=(0,8))
        tk.Button(topf, text="OK", bg=PINK, fg=WHITE, bd=0, command=self.apply_search_sort,
                  font=BTN_FONT, padx=BTN_PADX, pady=BTN_PADY).pack(side="left", padx=(0,8))

        tk.Button(topf, text="➕ Add Item", bg=PINK, fg=WHITE, bd=0, width=14, command=self.add_item,
                  font=BTN_FONT, padx=BTN_PADX, pady=BTN_PADY).pack(side="left", padx=6)
        tk.Button(topf, text="✏️ Edit Item", bg="#ff9fb1", fg=WHITE, bd=0, width=14, command=self.edit_item,
                  font=BTN_FONT, padx=BTN_PADX, pady=BTN_PADY).pack(side="left", padx=6)
        tk.Button(topf, text="🗑 Delete Item", bg="#e74c3c", fg=WHITE, bd=0, width=14, command=self.delete_item,
                  font=BTN_FONT, padx=BTN_PADX, pady=BTN_PADY).pack(side="left", padx=6)
        tk.Button(topf, text="🔄 Refresh", bg="#ddd", bd=0, width=12, command=self.load_menu,
                  font=BTN_FONT, padx=BTN_PADX, pady=BTN_PADY).pack(side="left", padx=6)
        tk.Button(topf, text="Close", bg="#666", fg=WHITE, bd=0, width=12, command=self.destroy,
                  font=BTN_FONT, padx=BTN_PADX, pady=BTN_PADY).pack(side="right", padx=6)

        # style & tree
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Admin.Treeview",
                        background=WHITE,
                        fieldbackground=WHITE,
                        rowheight=TREE_ROWHEIGHT,
                        font=("Helvetica", 11))
        style.configure("Admin.Treeview.Heading",
                        font=HEADING_FONT,
                        foreground=DARK_GRAY)
        style.map("Admin.Treeview", background=[('selected', PINK)], foreground=[('selected', WHITE)])

        cols = ("id", "category", "name", "price")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", style="Admin.Treeview")
        self.tree.heading("id", text="ID", command=lambda: self.sort_column("id"))
        self.tree.heading("category", text="Category", command=lambda: self.sort_column("category"))
        self.tree.heading("name", text="Name", command=lambda: self.sort_column("name"))
        self.tree.heading("price", text="Price (₱)", command=lambda: self.sort_column("price"))
        self.tree.column("id", anchor="center", width=70)
        self.tree.column("category", anchor="center", width=140)
        self.tree.column("name", anchor="w", width=420)
        self.tree.column("price", anchor="center", width=140)
        self.tree.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0,12))

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=2, column=1, sticky="ns", pady=(0,12))
        self.tree.configure(yscrollcommand=vsb.set)

        # zebra
        self.tree.tag_configure('odd', background='#ffffff')
        self.tree.tag_configure('even', background='#f6f6f6')

    def load_menu(self):
        try:
            rows = db.get_menus()
            self.all_rows = rows
            # reset header sort
            self._sort_state = {"column": None, "reverse": False}
            self.apply_search_sort()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load menu: {e}")

    def sort_column(self, column):
        if self._sort_state["column"] == column:
            self._sort_state["reverse"] = not self._sort_state["reverse"]
        else:
            self._sort_state["column"] = column
            self._sort_state["reverse"] = False
        self.apply_search_sort()

    def apply_search_sort(self):
        q = (self.search_var.get() or "").strip().lower()
        order = self.sort_var.get()
        rows = list(self.all_rows)
        if q:
            rows = [r for r in rows if q in r.get("name","").lower() or q in (r.get("category","").lower())]
        if order == "Price: Low → High":
            rows.sort(key=lambda r: float(r.get("price",0)))
        elif order == "Price: High → Low":
            rows.sort(key=lambda r: float(r.get("price",0)), reverse=True)
        elif order == "Name: A → Z":
            rows.sort(key=lambda r: r.get("name","").lower())

        # header-click sorting overrules option if set
        col = self._sort_state["column"]
        if col:
            if col in ("price", "id"):
                rows.sort(key=lambda r: float(r.get(col,0)), reverse=self._sort_state["reverse"])
            else:
                rows.sort(key=lambda r: r.get(col,"").lower(), reverse=self._sort_state["reverse"])

        # refresh tree with zebra
        for i in self.tree.get_children():
            self.tree.delete(i)
        for idx, r in enumerate(rows):
            tag = 'even' if idx%2==0 else 'odd'
            self.tree.insert("", "end", iid=str(r["id"]), values=(r["id"], r["category"], r["name"], f"{float(r['price']):.2f}"), tags=(tag,))

    def _get_selected_iid(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select an item.")
            return None
        return sel[0]

    # add_item / edit_item / delete_item 
    def add_item(self):
        d = tk.Toplevel(self)
        d.title("Add Menu Item")
        d.geometry("420x180")
        tk.Label(d, text="Category").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        cat_var = tk.StringVar(value="Meals")
        tk.OptionMenu(d, cat_var, "Meals", "Drinks", "Desserts").grid(row=0, column=1, padx=8, pady=8)
        tk.Label(d, text="Name").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        name_ent = tk.Entry(d, width=36); name_ent.grid(row=1, column=1, padx=8, pady=8)
        tk.Label(d, text="Price").grid(row=2, column=0, sticky="w", padx=8, pady=8)
        price_ent = tk.Entry(d, width=20); price_ent.grid(row=2, column=1, padx=8, pady=8)
        def do_add():
            name = name_ent.get().strip()
            try:
                price = float(price_ent.get())
            except Exception:
                messagebox.showerror("Error", "Enter valid price.")
                return
            if not name:
                messagebox.showerror("Error", "Enter item name.")
                return
            try:
                db.add_menu_item(cat_var.get(), name, price)
                messagebox.showinfo("Added", "Menu item added.")
                d.destroy()
                self.load_menu()
            except Exception as e:
                messagebox.showerror("Error", f"Could not add item: {e}")
        tk.Button(d, text="Add", bg=PINK, fg=WHITE, bd=0, command=do_add).grid(row=3, column=0, columnspan=2, pady=10)

    def edit_item(self):
        iid = self._get_selected_iid()
        if iid is None:
            return
        vals = self.tree.item(iid, "values")
        d = tk.Toplevel(self)
        d.title("Edit Menu Item")
        d.geometry("420x180")
        tk.Label(d, text="Category").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        cat_var = tk.StringVar(value=vals[1])
        tk.OptionMenu(d, cat_var, "Meals", "Drinks", "Desserts").grid(row=0, column=1, padx=8, pady=8)
        tk.Label(d, text="Name").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        name_ent = tk.Entry(d, width=36); name_ent.insert(0, vals[2]); name_ent.grid(row=1, column=1, padx=8, pady=8)
        tk.Label(d, text="Price").grid(row=2, column=0, sticky="w", padx=8, pady=8)
        price_ent = tk.Entry(d, width=20); price_ent.insert(0, vals[3]); price_ent.grid(row=2, column=1, padx=8, pady=8)
        def do_update():
            name = name_ent.get().strip()
            try:
                price = float(price_ent.get())
            except Exception:
                messagebox.showerror("Error", "Enter valid price.")
                return
            if not name:
                messagebox.showerror("Error", "Enter item name.")
                return
            try:
                conn = db.get_conn()
                cur = conn.cursor()
                cur.execute("UPDATE menus SET category=%s, name=%s, price=%s WHERE id=%s",
                            (cat_var.get(), name, float(price), int(iid)))
                conn.commit()
                cur.close(); conn.close()
                messagebox.showinfo("Updated", "Menu item updated.")
                d.destroy()
                self.load_menu()
            except Exception as e:
                messagebox.showerror("Error", f"Could not update: {e}")
        tk.Button(d, text="Update", bg=PINK, fg=WHITE, bd=0, command=do_update).grid(row=3, column=0, columnspan=2, pady=10)

    def delete_item(self):
        iid = self._get_selected_iid()
        if iid is None:
            return
        if not messagebox.askyesno("Confirm", "Delete selected menu item?"):
            return
        try:
            conn = db.get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM menus WHERE id=%s", (int(iid),))
            conn.commit()
            cur.close(); conn.close()
            messagebox.showinfo("Deleted", "Menu item deleted.")
            self.load_menu()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete item: {e}")