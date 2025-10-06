import tkinter as tk
from tkinter import messagebox, ttk
import db
from receipt import ReceiptWindow
from colors import PINK, LIGHT_PINK, WHITE, DARK_GRAY

SIZE_MULTIPLIER = {"S": 0.9, "M": 1.0, "L": 1.2}

class CustomerMenuWindow(tk.Frame):
    def __init__(self, master, user_id=None, username="Customer"):
        super().__init__(master, bg=WHITE)
        self.master = master
        self.user_id = user_id
        self.username = username
        db.init_db()
        self.cart = []            # list of dicts: name, unit_price, qty, size, subtotal
        self._undo_stack = []
        self._redo_stack = []
        self.total = 0.0
        try:
            self.master.resizable(True, True)
            self.master.state('zoomed')
        except Exception:
            pass
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.create_widgets()
        self.pack(fill="both", expand=True)

    def create_widgets(self):
        header = tk.Frame(self, bg=PINK, height=60)
        header.pack(fill="x")
        tk.Label(header, text="HappyFood.com", bg=PINK, fg=WHITE, font=("Helvetica", 16, "bold")).pack(side="left", padx=12)
        tk.Label(header, text=f"Ordering — {self.username}", bg=PINK, fg=WHITE, font=("Helvetica", 11)).pack(side="right", padx=12)

        main = tk.Frame(self, bg=LIGHT_PINK)
        main.pack(fill="both", expand=True, padx=12, pady=12)
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)

        catf = tk.Frame(main, bg=LIGHT_PINK)
        catf.pack(fill="x", pady=(0,8))
        for c in ("Recommended","Meals","Drinks","Desserts"):
            tk.Button(catf, text=c, bg=WHITE, fg=DARK_GRAY, bd=0, padx=8, pady=6,
                      command=lambda cat=c: self.load_category(cat)).pack(side="left", padx=6)

        content = tk.Frame(main, bg=LIGHT_PINK)
        content.pack(fill="both", expand=True)
        left = tk.Frame(content, bg=LIGHT_PINK)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))
        self.menu_tree = ttk.Treeview(left, columns=("price",), show="headings", height=18)
        self.menu_tree.heading("price", text="--ITEM -------- PRICE--")
        self.menu_tree.pack(fill="both", expand=True)
        self.menu_tree.bind("<Double-1>", lambda e: self.add_selected())

        right = tk.Frame(content, bg=WHITE, width=320)
        right.pack(side="right", fill="y")
        tk.Label(right, text="Cart", bg=WHITE, font=("Helvetica",14,"bold")).pack(pady=8)
        self.cart_list = tk.Listbox(right, width=40, height=12)
        self.cart_list.pack(padx=8)
        self.total_var = tk.StringVar(value="Total: ₱0.00")
        tk.Label(right, textvariable=self.total_var, bg=WHITE, font=("Helvetica",14,"bold"), fg=PINK).pack(pady=8)

        # size and quantity controls
        controls = tk.Frame(right, bg=WHITE)
        controls.pack(pady=6)
        tk.Label(controls, text="Size:", bg=WHITE).grid(row=0, column=0, sticky="w", padx=4)
        self.size_var = tk.StringVar(value="M")
        tk.OptionMenu(controls, self.size_var, "S", "M", "L").grid(row=0, column=1, padx=4)
        tk.Label(controls, text="Qty:", bg=WHITE).grid(row=1, column=0, sticky="w", padx=4, pady=(6,0))
        self.qty_spin = tk.Spinbox(controls, from_=1, to=99, width=5)
        self.qty_spin.grid(row=1, column=1, padx=4, pady=(6,0))

        btnf = tk.Frame(right, bg=WHITE)
        btnf.pack(pady=6)
        tk.Button(btnf, text="Add to Cart", bg=PINK, fg=WHITE, bd=0, command=self.add_selected).grid(row=0, column=0, padx=4)
        tk.Button(btnf, text="Undo", bg="#ddd", bd=0, command=self.undo).grid(row=0, column=1, padx=4)
        tk.Button(btnf, text="Redo", bg="#ddd", bd=0, command=self.redo).grid(row=0, column=2, padx=4)
        tk.Button(right, text="Place Order", bg=PINK, fg=WHITE, bd=0, width=22, command=self.place_order).pack(pady=(8,4))
        tk.Button(right, text="Reset Orders", bg="#eee", bd=0, width=22, command=self.reset_cart).pack(pady=2)
        tk.Button(right, text="Back to Home", bg="#666", fg=WHITE, bd=0, width=22, command=self.back_home).pack(pady=6)
        self.load_category("Recommended")

    def filter_query(self, query):
        rows = db.get_menus()
        matches = [r for r in rows if query.lower() in r["name"].lower()]
        for i in self.menu_tree.get_children():
            self.menu_tree.delete(i)
        for r in matches:
            self.menu_tree.insert("", "end", iid=str(r["id"]), values=(f"{r['name']} — ₱{float(r['price']):.2f}",))

    def load_category(self, category):
        for i in self.menu_tree.get_children():
            self.menu_tree.delete(i)
        rows = db.get_menus(category=None if category=="Recommended" else category)
        for r in rows:
            self.menu_tree.insert("", "end", iid=str(r["id"]), values=(f"{r['name']} — ₱{float(r['price']):.2f}",))

    def _get_menu_item_by_iid(self, iid):
        rows = db.get_menus()
        return next((r for r in rows if str(r["id"])==str(iid)), None)

    def add_selected(self):
        sel = self.menu_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select an item to add.")
            return
        iid = sel[0]
        item = self._get_menu_item_by_iid(iid)
        if not item:
            messagebox.showerror("Error", "Item not found.")
            return
        name = item["name"]
        base_price = float(item["price"])
        size = self.size_var.get() or "M"
        try:
            qty = int(self.qty_spin.get())
            if qty < 1:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Enter valid quantity.")
            return
        unit_price = round(base_price * SIZE_MULTIPLIER.get(size, 1.0), 2)
        subtotal = round(unit_price * qty, 2)
        cart_item = {
            "menu_id": int(iid),
            "name": name,
            "unit_price": unit_price,
            "qty": qty,
            "size": size,
            "subtotal": subtotal
        }
        self.cart.append(cart_item)
        self.cart_list.insert("end", f"{qty} x {name} ({size}) — ₱{subtotal:.2f}")
        self._undo_stack.append(("add", cart_item))
        self._redo_stack.clear()
        self.update_total()

    def update_total(self):
        self.total = round(sum(item["subtotal"] for item in self.cart), 2)
        self.total_var.set(f"Total: ₱{self.total:.2f}")

    def undo(self):
        if not self._undo_stack:
            return
        action, data = self._undo_stack.pop()
        if action == "add":
            # remove last matching item
            for i in range(len(self.cart)-1, -1, -1):
                if self.cart[i] == data:
                    del self.cart[i]
                    self.cart_list.delete(i)
                    break
            self._redo_stack.append((action, data))
            self.update_total()

    def redo(self):
        if not self._redo_stack:
            return
        action, data = self._redo_stack.pop()
        if action == "add":
            self.cart.append(data)
            self.cart_list.insert("end", f"{data['qty']} x {data['name']} ({data['size']}) — ₱{data['subtotal']:.2f}")
            self._undo_stack.append((action, data))
            self.update_total()

    def place_order(self):
        if not self.cart:
            messagebox.showinfo("Info", "Cart is empty.")
            return
        if not messagebox.askyesno("Confirm", f"Place order for total ₱{self.total:.2f}?"):
            return
        try:
            db.save_order(self.cart, self.total)
            messagebox.showinfo("Success", "Order placed.")
            try:
                ReceiptWindow(self.master, items=self.cart, total=self.total)
            except Exception:
                pass
            self.reset_cart()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save order: {e}")

    def reset_cart(self):
        self.cart.clear()
        self.cart_list.delete(0, "end")
        self._undo_stack.clear()
        self._redo_stack.clear()
        self.update_total()

    def back_home(self):
        try:
            parent = self.master.master
            self.master.destroy()
            try:
                parent.deiconify()
            except Exception:
                pass
        except Exception:
            pass