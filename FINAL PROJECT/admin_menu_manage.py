import tkinter as tk
from tkinter import ttk, messagebox
import db
from colors import PINK, LIGHT_PINK, WHITE, DARK_GRAY

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
        tk.Button(topf, text="➕ Add Item", bg=PINK, fg=WHITE, bd=0, width=12, command=self.add_item).pack(side="left", padx=6)
        tk.Button(topf, text="✏️ Edit Item", bg="#ff9fb1", fg=WHITE, bd=0, width=12, command=self.edit_item).pack(side="left", padx=6)
        tk.Button(topf, text="🗑 Delete Item", bg="#e74c3c", fg=WHITE, bd=0, width=12, command=self.delete_item).pack(side="left", padx=6)
        tk.Button(topf, text="🔄 Refresh", bg="#ddd", bd=0, width=10, command=self.load_menu).pack(side="left", padx=6)
        tk.Button(topf, text="Close", bg="#666", fg=WHITE, bd=0, width=10, command=self.destroy).pack(side="right", padx=6)
        cols = ("id", "category", "name", "price")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, anchor="center")
        self.tree.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0,12))
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=2, column=1, sticky="ns", pady=(0,12))
        self.tree.configure(yscrollcommand=vsb.set)

    def load_menu(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            rows = db.get_menus()
            for r in rows:
                self.tree.insert("", "end", iid=str(r["id"]), values=(r["id"], r["category"], r["name"], f"{float(r['price']):.2f}"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load menu: {e}")

    def _get_selected_iid(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select an item.")
            return None
        return sel[0]

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