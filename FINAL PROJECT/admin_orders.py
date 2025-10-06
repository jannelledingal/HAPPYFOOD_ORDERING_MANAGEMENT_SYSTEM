# ...existing code...
import tkinter as tk
from tkinter import ttk, messagebox
import db
import json
from colors import PINK, LIGHT_PINK, WHITE, DARK_GRAY
from receipt import ReceiptWindow

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
        content.columnconfigure(0, weight=1)

        cols = ("items", "total", "created_at", "status")
        self.tree = ttk.Treeview(content, columns=cols, show="headings")
        self.tree.heading("items", text="Items")
        self.tree.heading("total", text="Total (PHP)")
        self.tree.heading("created_at", text="Date/Time")
        self.tree.heading("status", text="Status")
        self.tree.column("items", width=420, anchor="w")
        self.tree.column("total", width=100, anchor="center")
        self.tree.column("created_at", width=180, anchor="center")
        self.tree.column("status", width=100, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(content, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        btnf = tk.Frame(content, bg=WHITE)
        btnf.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8,0))
        tk.Button(btnf, text="✔ Serve Order", bg=PINK, fg=WHITE, bd=0, width=16,
                  command=self.serve_selected).pack(side="left", padx=6)
        tk.Button(btnf, text="🗑 Delete Order", bg="#e74c3c", fg=WHITE, bd=0, width=16,
                  command=self.delete_selected).pack(side="left", padx=6)
        tk.Button(btnf, text="🔄 Refresh", bg="#ddd", bd=0, width=12, command=self.load_orders).pack(side="left", padx=6)
        tk.Button(btnf, text="🔍 Details", bg="#ddd", bd=0, width=12, command=self.show_order_details).pack(side="left", padx=6)
        tk.Button(btnf, text="Close", bg="#666", fg=WHITE, bd=0, width=12, command=self.destroy).pack(side="right", padx=6)

        self.tree.bind("<Double-1>", lambda e: self.show_order_details())

    def load_orders(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            rows = db.get_pending_orders()
            for r in rows:
                items = r.get("items", [])
                if isinstance(items, list):
                    items_text = ", ".join(f"{it.get('qty',1)}x {it.get('name')}({it.get('size','M')})" for it in items)
                else:
                    items_text = str(items)
                self.tree.insert("", "end", iid=str(r["id"]),
                                 values=(items_text, f"{float(r['total']):.2f}", r["created_at"], r.get("status","pending")))
        except Exception as e:
            messagebox.showerror("Error", f"Failed loading orders: {e}")

    def _get_selected_order_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select an order.")
            return None
        return int(sel[0])

    def serve_selected(self):
        order_id = self._get_selected_order_id()
        if order_id is None:
            return
        if not messagebox.askyesno("Confirm", "Mark selected order as served?"):
            return
        try:
            db.mark_order_served(order_id)
            self.tree.delete(str(order_id))
            messagebox.showinfo("Done", "Order marked as served.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not mark served: {e}")

    def delete_selected(self):
        order_id = self._get_selected_order_id()
        if order_id is None:
            return
        if not messagebox.askyesno("Confirm", "Delete selected order? This cannot be undone."):
            return
        try:
            db.delete_order(order_id)
            self.tree.delete(str(order_id))
            messagebox.showinfo("Done", "Order deleted.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete order: {e}")

    def show_order_details(self):
        order_id = self._get_selected_order_id()
        if order_id is None:
            return
        try:
            conn = db.get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM orders WHERE id=%s", (order_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                messagebox.showinfo("Info", "Order not found.")
                return
            # parse items JSON
            try:
                items_list = json.loads(row.get("items")) if isinstance(row.get("items"), str) else row.get("items")
            except Exception:
                items_list = row.get("items")

            info = f"Order ID: {order_id}\nStatus: {row.get('status')}\nCreated: {row.get('created_at')}\nTotal: ₱{float(row.get('total')):.2f}"
            # show basic info and open receipt-style details window
            messagebox.showinfo("Order Info", info)
            try:
                ReceiptWindow(self, items=items_list, total=float(row.get('total')))
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"Could not load details: {e}")
# ...existing code...