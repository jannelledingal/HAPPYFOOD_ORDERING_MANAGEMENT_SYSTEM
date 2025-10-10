import tkinter as tk
from customer_menu import orders

class CustomerOrdersWindow(tk.Toplevel):
    def __init__(self, master, user_id, username):
        super().__init__(master)
        self.user_id = user_id
        self.username = username
        self.title("Your Orders")
        self.geometry("540x370")
        tk.Label(self, text="Your Orders + Total Cost", font=("Arial", 14, "bold")).pack()
        sort_frame = tk.Frame(self)
        sort_frame.pack(pady=2)
        tk.Label(sort_frame, text="Sort by:").pack(side="left")
        self.sort_var = tk.StringVar(value="order_time DESC")
        options = [
            ("Newest", "order_time DESC"),
            ("Oldest", "order_time ASC"),
            ("Price High-Low", "total_price DESC"),
            ("Price Low-High", "total_price ASC")
        ]
        for text, val in options:
            tk.Radiobutton(sort_frame, text=text, variable=self.sort_var, value=val, command=self.load_orders).pack(side="left")
        self.orders_frame = tk.Frame(self)
        self.orders_frame.pack()
        self.load_orders()
        tk.Button(self, text="View Receipt (Last Order)", command=self.show_receipt).pack(pady=10)
        tk.Button(self, text="Exit", command=self.destroy).pack()

    def load_orders(self):
        for widget in self.orders_frame.winfo_children():
            widget.destroy()
        user_orders = [o for o in orders if o["user_id"] == self.user_id]
        key, reverse = ("order_time", False) if "order_time" in self.sort_var.get() else ("total_price", False)
        reverse = "DESC" in self.sort_var.get()
        user_orders = sorted(user_orders, key=lambda x: x[key], reverse=reverse)
        total = 0
        for order in user_orders:
            tk.Label(self.orders_frame, text=f"{order['order_time'].strftime('%Y-%m-%d %H:%M')} | {order['order_details']} | ₱{order['total_price']:.2f}").pack(anchor="w")
            total += order['total_price']
        tk.Label(self.orders_frame, text=f"Total Cost: ₱{total:.2f}", font=("Arial", 12, "bold")).pack(pady=5)

    def show_receipt(self):
        from receipt import ReceiptWindow
        ReceiptWindow(self, self.user_id)