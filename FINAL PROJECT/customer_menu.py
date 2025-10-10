import tkinter as tk
from tkinter import messagebox, ttk
import db
from receipt import ReceiptWindow
from colors import PINK, LIGHT_PINK, WHITE, DARK_GRAY

# pricing rule: S = base price, M = base + 10, L = base + 20
def compute_unit_price(base_price: float, size: str):
    try:
        base = float(base_price)
    except Exception:
        base = 0.0
    if size == "S":
        return round(base, 2)
    if size == "M":
        return round(base + 10.0, 2)
    if size == "L":
        return round(base + 20.0, 2)
    return round(base, 2)

SIZE_MULTIPLIER = {"S": 1.0, "M": 1.0, "L": 1.0}  # compatibility

# Accessibility / sizing tuned so UI fits on typical screens
BUTTON_FONT = ("Helvetica", 12, "bold")
LABEL_FONT = ("Helvetica", 11)
INPUT_FONT = ("Helvetica", 11)
TREE_FONT = ("Helvetica", 11)
TREE_ROWHEIGHT = 34
BIG_BUTTON_PADX = 10
BIG_BUTTON_PADY = 8

class CustomerMenuWindow(tk.Frame):
    def __init__(self, master, user_id=None, username="Guest"):
        super().__init__(master, bg=WHITE)
        self.master = master
        self.user_id = user_id
        self.username = username
        db.init_db()
        self.cart = []
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

        # state
        self.current_category = "Recommended"
        self.current_rows = []
        self._sort_state = {"column": None, "reverse": False}

        self.create_widgets()
        self.pack(fill="both", expand=True)

    def create_widgets(self):
        header = tk.Frame(self, bg=PINK, height=64)
        header.pack(fill="x")
        tk.Label(header, text="HappyFood", bg=PINK, fg=WHITE, font=("Helvetica", 20, "bold")).pack(side="left", padx=12)
        tk.Label(header, text=f"Ordering — {self.username}", bg=PINK, fg=WHITE, font=("Helvetica", 12)).pack(side="right", padx=12)

        main = tk.Frame(self, bg=LIGHT_PINK)
        main.pack(fill="both", expand=True, padx=12, pady=12)

        top_row = tk.Frame(main, bg=LIGHT_PINK)
        top_row.pack(fill="x", pady=(0,8))

        catf = tk.Frame(top_row, bg=LIGHT_PINK)
        catf.pack(side="left", anchor="w")
        for c in ("Recommended","Meals","Drinks","Desserts"):
            tk.Button(catf, text=c, bg=WHITE, fg=DARK_GRAY, bd=0,
                      padx=BIG_BUTTON_PADX, pady=BIG_BUTTON_PADY, font=BUTTON_FONT,
                      command=lambda cat=c: self.load_category(cat)).pack(side="left", padx=6)

        searchf = tk.Frame(top_row, bg=LIGHT_PINK)
        searchf.pack(side="right", anchor="e")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(searchf, textvariable=self.search_var, width=22, font=INPUT_FONT)
        search_entry.pack(side="left", padx=(0,6))
        self.sort_var = tk.StringVar(value="Default")
        sort_menu = tk.OptionMenu(searchf, self.sort_var, "Default", "Price: Low → High", "Price: High → Low", "Name: A → Z")
        sort_menu.config(font=INPUT_FONT)
        sort_menu.pack(side="left", padx=(0,6))
        tk.Button(searchf, text="Apply", command=self.apply_search_sort, bg=PINK, fg=WHITE, bd=0,
                  padx=10, pady=6, font=BUTTON_FONT).pack(side="left")

        content = tk.Frame(main, bg=LIGHT_PINK)
        content.pack(fill="both", expand=True)

        # left: menu list
        left = tk.Frame(content, bg=LIGHT_PINK)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Treeview",
                        background=WHITE,
                        fieldbackground=WHITE,
                        rowheight=TREE_ROWHEIGHT,
                        font=TREE_FONT)
        style.configure("Custom.Treeview.Heading",
                        font=("Helvetica", 12, "bold"),
                        foreground=DARK_GRAY)
        style.map("Custom.Treeview", background=[('selected', PINK)], foreground=[('selected', WHITE)])

        self.menu_tree = ttk.Treeview(left, columns=("name", "price"), show="headings", style="Custom.Treeview")
        self.menu_tree.heading("name", text="Name", command=lambda: self.sort_column("name"))
        self.menu_tree.heading("price", text="Price (₱)", command=lambda: self.sort_column("price"))
        self.menu_tree.column("name", anchor="w")
        self.menu_tree.column("price", anchor="center", width=140)
        self.menu_tree.pack(fill="both", expand=True)
        self.menu_tree.bind("<Double-1>", lambda e: self.add_selected())
        self.menu_tree.tag_configure('odd', background='#ffffff')
        self.menu_tree.tag_configure('even', background='#f6f6f6')

        # right: compact, scrollable panel so buttons are always reachable on smaller screens
        RIGHT_WIDTH = 340
        right_outer = tk.Frame(content, bg=WHITE, width=RIGHT_WIDTH)
        right_outer.pack(side="right", fill="y")
        right_outer.pack_propagate(False)

        right_canvas = tk.Canvas(right_outer, bg=WHITE, highlightthickness=0)
        right_vsb = ttk.Scrollbar(right_outer, orient="vertical", command=right_canvas.yview)
        right_canvas.configure(yscrollcommand=right_vsb.set)
        right_vsb.pack(side="right", fill="y")
        right_canvas.pack(side="left", fill="both", expand=True)
        right_inner = tk.Frame(right_canvas, bg=WHITE)
        right_canvas.create_window((0,0), window=right_inner, anchor="nw")

        def _on_right_config(e):
            right_canvas.configure(scrollregion=right_canvas.bbox("all"))
        right_inner.bind("<Configure>", _on_right_config)

        # populate right_inner with controls
        tk.Label(right_inner, text="Cart", bg=WHITE, font=("Helvetica",14,"bold")).pack(pady=(10,6))
        self.cart_list = tk.Listbox(right_inner, width=36, height=8, font=INPUT_FONT)
        self.cart_list.pack(padx=8)
        self.total_var = tk.StringVar(value="Total: ₱0.00")
        tk.Label(right_inner, textvariable=self.total_var, bg=WHITE, font=("Helvetica",13,"bold"), fg=PINK).pack(pady=10)

        controls = tk.Frame(right_inner, bg=WHITE)
        controls.pack(pady=6, padx=8, fill="x")
        tk.Label(controls, text="Size:", bg=WHITE, font=LABEL_FONT).grid(row=0, column=0, sticky="w", padx=4)
        self.size_var = tk.StringVar(value="M")
        size_menu = tk.OptionMenu(controls, self.size_var, "S", "M", "L")
        size_menu.config(font=INPUT_FONT)
        size_menu.grid(row=0, column=1, padx=4)
        tk.Label(controls, text="Qty:", bg=WHITE, font=LABEL_FONT).grid(row=1, column=0, sticky="w", padx=4, pady=(8,0))
        self.qty_spin = tk.Spinbox(controls, from_=1, to=99, width=5, font=INPUT_FONT)
        self.qty_spin.grid(row=1, column=1, padx=4, pady=(8,0))
        controls.grid_columnconfigure(1, weight=1)

        btnf = tk.Frame(right_inner, bg=WHITE)
        btnf.pack(pady=10, padx=8, fill="x")
        add_btn = tk.Button(btnf, text="Add to Cart", bg=PINK, fg=WHITE, bd=0, command=self.add_selected,
                            padx=10, pady=8, font=BUTTON_FONT)
        add_btn.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        undo_btn = tk.Button(btnf, text="Undo", bg="#ddd", bd=0, command=self.undo,
                             padx=8, pady=8, font=BUTTON_FONT)
        undo_btn.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        redo_btn = tk.Button(btnf, text="Redo", bg="#ddd", bd=0, command=self.redo,
                             padx=8, pady=8, font=BUTTON_FONT)
        redo_btn.grid(row=0, column=2, padx=4, pady=4, sticky="ew")
        btnf.grid_columnconfigure(0, weight=1)
        btnf.grid_columnconfigure(1, weight=1)
        btnf.grid_columnconfigure(2, weight=1)

        tk.Button(right_inner, text="Place Order", bg=PINK, fg=WHITE, bd=0,
                  padx=8, pady=10, font=("Helvetica", 13, "bold"), command=self.place_order).pack(pady=(12,6), padx=12, fill="x")
        tk.Button(right_inner, text="Reset Orders", bg="#eee", bd=0,
                  padx=8, pady=8, font=BUTTON_FONT, command=self.reset_cart).pack(pady=6, padx=12, fill="x")
        tk.Button(right_inner, text="Back to Home", bg="#666", fg=WHITE, bd=0,
                  padx=8, pady=8, font=BUTTON_FONT, command=self.back_home).pack(pady=8, padx=12, fill="x")

        # ensure all widgets visible: bind mousewheel to scroll right_inner when focused
        def _on_mousewheel(e):
            right_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        right_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.load_category("Recommended")

    def apply_search_sort(self):
        q = (self.search_var.get() or "").strip().lower()
        order = self.sort_var.get()
        rows = list(self.current_rows)
        if q:
            rows = [r for r in rows if q in r.get("name","").lower()]
        if order == "Price: Low → High":
            rows.sort(key=lambda r: float(r.get("price",0)))
        elif order == "Price: High → Low":
            rows.sort(key=lambda r: float(r.get("price",0)), reverse=True)
        elif order == "Name: A → Z":
            rows.sort(key=lambda r: r.get("name","").lower())

        col = self._sort_state["column"]
        if col:
            if col == "price":
                rows.sort(key=lambda r: float(r.get("price",0)), reverse=self._sort_state["reverse"])
            else:
                rows.sort(key=lambda r: r.get("name","").lower(), reverse=self._sort_state["reverse"])

        for i in self.menu_tree.get_children():
            self.menu_tree.delete(i)
        for idx, r in enumerate(rows):
            tag = 'even' if idx%2==0 else 'odd'
            self.menu_tree.insert("", "end", iid=str(r["id"]), values=(r["name"], f"{float(r['price']):.2f}"), tags=(tag,))

    def filter_query(self, query):
        self.search_var.set(query)
        self.apply_search_sort()

    def load_category(self, category):
        self.current_category = category
        rows = db.get_menus(category=None if category=="Recommended" else category)
        self.current_rows = rows
        self._sort_state = {"column": None, "reverse": False}
        self.apply_search_sort()

    def sort_column(self, column):
        if self._sort_state["column"] == column:
            self._sort_state["reverse"] = not self._sort_state["reverse"]
        else:
            self._sort_state["column"] = column
            self._sort_state["reverse"] = False
        self.apply_search_sort()

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
        unit_price = compute_unit_price(base_price, size)
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
            order_id = db.save_order(self.cart, self.total)
            messagebox.showinfo("Success", f"Order placed. Order ID: {order_id}")
            try:
                ReceiptWindow(self.master, items=self.cart, total=self.total, order_id=order_id)
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