import tkinter as tk
from tkinter import ttk, messagebox
import db
import json
from colors import PINK, LIGHT_PINK, WHITE, DARK_GRAY
from receipt import ReceiptWindow

# Accessibility / larger controls
BTN_FONT = ("Helvetica", 13, "bold")
BTN_PADY = 10
TREE_ROWHEIGHT = 34

class AdminOrdersWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Pending Orders")
        self.resizable(True, True)
        try:
            self.state('zoomed')
        except Exception:
            pass
        self.configure(bg=LIGHT_PINK)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # cached orders list
        self._orders = []  # list of dicts
        # sort state
        self._sort_state = {"column": None, "reverse": False}

        self.create_widgets()
        self.load_orders()

    def create_widgets(self):
        header = tk.Frame(self, bg=PINK, height=64)
        header.grid(row=0, column=0, sticky="nsew")
        tk.Label(header, text="📦 Pending Orders", bg=PINK, fg=WHITE,
                 font=("Helvetica", 16, "bold")).pack(side="left", padx=12, pady=12)

        content = tk.Frame(self, bg=WHITE)
        content.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        content.rowconfigure(0, weight=1)
        content.rowconfigure(1, weight=0)
        content.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Orders.Treeview",
                        background=WHITE,
                        fieldbackground=WHITE,
                        rowheight=TREE_ROWHEIGHT,
                        font=("Helvetica", 11))
        style.configure("Orders.Treeview.Heading",
                        font=("Helvetica", 12, "bold"),
                        foreground=DARK_GRAY)
        style.map("Orders.Treeview", background=[('selected', PINK)], foreground=[('selected', WHITE)])

        cols = ("id", "items", "total", "created_at", "status")
        self.tree = ttk.Treeview(content, columns=cols, show="headings", style="Orders.Treeview", height=12)
        self.tree.heading("id", text="ID", command=lambda: self.sort_column("id"))
        self.tree.heading("items", text="Items")
        self.tree.heading("total", text="Total (₱)", command=lambda: self.sort_column("total"))
        self.tree.heading("created_at", text="Date/Time", command=lambda: self.sort_column("created_at"))
        self.tree.heading("status", text="Status", command=lambda: self.sort_column("status"))
        self.tree.column("id", width=70, anchor="center")
        self.tree.column("items", width=480, anchor="w")
        self.tree.column("total", width=120, anchor="center")
        self.tree.column("created_at", width=180, anchor="center")
        self.tree.column("status", width=120, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(content, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.tag_configure('odd', background='#ffffff')
        self.tree.tag_configure('even', background='#f6f6f6')

        self.tree.bind("<<TreeviewSelect>>", lambda e: self.on_tree_select())
        self.tree.bind("<Double-1>", lambda e: self.show_order_details())

        details_frame = tk.Frame(content, bg=LIGHT_PINK, bd=1, relief="groove")
        details_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8,8))
        details_frame.columnconfigure(0, weight=1)

        info_bar = tk.Frame(details_frame, bg=LIGHT_PINK)
        info_bar.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        self.details_id_lbl = tk.Label(info_bar, text="Order ID: —", bg=LIGHT_PINK, font=("Helvetica", 11, "bold"))
        self.details_id_lbl.pack(side="left", padx=(0,12))
        self.details_status_lbl = tk.Label(info_bar, text="Status: —", bg=LIGHT_PINK)
        self.details_status_lbl.pack(side="left", padx=(0,12))
        self.details_time_lbl = tk.Label(info_bar, text="Created: —", bg=LIGHT_PINK)
        self.details_time_lbl.pack(side="left", padx=(0,12))
        self.details_total_lbl = tk.Label(info_bar, text="Total: ₱0.00", bg=LIGHT_PINK, fg=PINK, font=("Helvetica", 11, "bold"))
        self.details_total_lbl.pack(side="right", padx=(0,6))

        dcols = ("name", "qty", "size", "unit_price", "subtotal")
        self.details_tree = ttk.Treeview(details_frame, columns=dcols, show="headings", height=5)
        for c, title, w in zip(dcols, ("Name", "Qty", "Size", "Unit (₱)", "Subtotal (₱)"), (300, 60, 60, 100, 120)):
            self.details_tree.heading(c, text=title)
            self.details_tree.column(c, width=w, anchor="center" if c != "name" else "w")
        self.details_tree.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))

        btnf = tk.Frame(content, bg=WHITE)
        btnf.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0,0))
        tk.Button(btnf, text="✔  Serve Order", bg=PINK, fg=WHITE, bd=0, width=18,
                  command=self.serve_selected, font=BTN_FONT, padx=10, pady=BTN_PADY).pack(side="left", padx=8)
        tk.Button(btnf, text="🗑  Delete Order", bg="#e74c3c", fg=WHITE, bd=0, width=18,
                  command=self.delete_selected, font=BTN_FONT, padx=10, pady=BTN_PADY).pack(side="left", padx=8)
        tk.Button(btnf, text="🔄  Refresh", bg="#ddd", bd=0, width=14, command=self.load_orders,
                  font=BTN_FONT, padx=10, pady=BTN_PADY).pack(side="left", padx=8)
        tk.Button(btnf, text="🔍  Open Receipt", bg="#ddd", bd=0, width=16, command=self.open_receipt_for_selected,
                  font=BTN_FONT, padx=10, pady=BTN_PADY).pack(side="left", padx=8)
        tk.Button(btnf, text="Close", bg="#666", fg=WHITE, bd=0, width=14, command=self.destroy,
                  font=BTN_FONT, padx=10, pady=BTN_PADY).pack(side="right", padx=8)

        self.update_heading_indicators()

    def load_orders(self):
        """Load orders from DB and populate tree. Expects db.get_orders() or db.get_conn()."""
        try:
            try:
                rows = db.get_orders()
            except Exception:
                # fallback: direct SQL
                conn = db.get_conn()
                cur = conn.cursor()
                cur.execute("SELECT id, items, total, created_at, status FROM orders ORDER BY id DESC")
                cols = [r[0] for r in cur.description]
                rows = []
                for r in cur.fetchall():
                    rows.append({
                        "id": r[0],
                        "items": r[1],
                        "total": r[2],
                        "created_at": r[3],
                        "status": r[4]
                    })
                cur.close(); conn.close()
            # normalize and store
            self._orders = []
            for r in rows:
                ord = dict(r) if isinstance(r, dict) else r
                self._orders.append(ord)
            # apply sort/search if needed
            self._refresh_tree()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {e}")

    def _refresh_tree(self):
        # simple sort if requested
        rows = list(self._orders)
        col = self._sort_state["column"]
        if col:
            rev = self._sort_state["reverse"]
            if col in ("id","total"):
                rows.sort(key=lambda r: float(r.get(col,0)), reverse=rev)
            else:
                rows.sort(key=lambda r: str(r.get(col,"")).lower(), reverse=rev)
        # populate tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        for idx, r in enumerate(rows):
            items_text = self._items_summary_text(r.get("items"))
            tag = 'even' if idx%2==0 else 'odd'
            self.tree.insert("", "end", iid=str(r["id"]), values=(r["id"], items_text, f"{float(r.get('total',0)):.2f}", str(r.get("created_at","")), r.get("status","")), tags=(tag,))

    def _items_summary_text(self, items_field):
        try:
            if isinstance(items_field, str):
                items = json.loads(items_field)
            else:
                items = items_field
            parts = []
            for it in items:
                name = it.get("name") if isinstance(it, dict) else str(it)
                qty = it.get("qty", 1) if isinstance(it, dict) else 1
                parts.append(f"{qty}x {name}")
            return "; ".join(parts)
        except Exception:
            return "—"

    def on_tree_select(self):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        order = next((o for o in self._orders if str(o.get("id"))==str(iid)), None)
        if not order:
            return
        # update info labels
        self.details_id_lbl.config(text=f"Order ID: {order.get('id')}")
        self.details_status_lbl.config(text=f"Status: {order.get('status', '—')}")
        self.details_time_lbl.config(text=f"Created: {order.get('created_at', '—')}")
        self.details_total_lbl.config(text=f"Total: ₱{float(order.get('total',0)):.2f}")
        # populate details tree
        for i in self.details_tree.get_children():
            self.details_tree.delete(i)
        items = order.get("items")
        try:
            if isinstance(items, str):
                items = json.loads(items)
        except Exception:
            items = []
        for it in items:
            name = it.get("name", "")
            qty = it.get("qty", 1)
            size = it.get("size", "")
            unit = it.get("unit_price", 0.0) if "unit_price" in it else it.get("price", 0.0)
            subtotal = it.get("subtotal", round(float(unit)*int(qty) if qty else 0,2))
            self.details_tree.insert("", "end", values=(name, qty, size, f"{float(unit):.2f}", f"{float(subtotal):.2f}"))

    def show_order_details(self):
        # same as selection handler — ensure user sees details
        self.on_tree_select()

    def get_selected_order_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select an order first.")
            return None
        return int(sel[0])

    def serve_selected(self):
        oid = self.get_selected_order_id()
        if oid is None:
            return
        if not messagebox.askyesno("Confirm", f"Mark order #{oid} as served?"):
            return
        try:
            # try db helper first
            try:
                db.update_order_status(oid, "served")
            except Exception:
                conn = db.get_conn()
                cur = conn.cursor()
                cur.execute("UPDATE orders SET status=%s WHERE id=%s", ("served", oid))
                conn.commit()
                cur.close(); conn.close()
            messagebox.showinfo("Served", f"Order #{oid} marked as served.")
            self.load_orders()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update order: {e}")

    def delete_selected(self):
        oid = self.get_selected_order_id()
        if oid is None:
            return
        if not messagebox.askyesno("Confirm", f"Delete order #{oid}? This cannot be undone."):
            return
        try:
            try:
                db.delete_order(oid)
            except Exception:
                conn = db.get_conn()
                cur = conn.cursor()
                cur.execute("DELETE FROM orders WHERE id=%s", (oid,))
                conn.commit()
                cur.close(); conn.close()
            messagebox.showinfo("Deleted", f"Order #{oid} deleted.")
            self.load_orders()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete order: {e}")

    def open_receipt_for_selected(self):
        oid = self.get_selected_order_id()
        if oid is None:
            return
        order = next((o for o in self._orders if int(o.get("id"))==int(oid)), None)
        if not order:
            messagebox.showerror("Error", "Order not found.")
            return
        items = order.get("items")
        try:
            if isinstance(items, str):
                items = json.loads(items)
        except Exception:
            items = []
        total = float(order.get("total", 0.0))
        try:
            ReceiptWindow(self, items=items, total=total, order_id=oid)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open receipt: {e}")

    def sort_column(self, column):
        if self._sort_state["column"] == column:
            self._sort_state["reverse"] = not self._sort_state["reverse"]
        else:
            self._sort_state["column"] = column
            self._sort_state["reverse"] = False
        self._refresh_tree()

    def update_heading_indicators(self):
        pass