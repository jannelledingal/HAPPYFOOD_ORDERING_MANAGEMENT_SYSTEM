import tkinter as tk
from tkinter import messagebox
from customer_menu import orders

class CustomerCartWindow(tk.Toplevel):
    def __init__(self, master, cart, user_id, username):
        super().__init__(master)
        self.cart = cart
        self.user_id = user_id
        self.username = username
        self.title("Your Cart")
        self.geometry("400x350")
        self.build()

    def build(self):
        tk.Label(self, text="Your Cart").pack()
        self.cart_frame = tk.Frame(self)
        self.cart_frame.pack()
        self.refresh_cart()
        tk.Button(self, text="Place Order", command=self.place_order).pack(pady=8)
        tk.Button(self, text="Close", command=self.destroy).pack()

    def refresh_cart(self):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()
        total = 0
        for item in self.cart:
            tk.Label(self.cart_frame, text=f"{item['name']} x{item['qty']} - ₱{item['price']*item['qty']:.2f}").pack()
            total += item['price']*item['qty']
        tk.Label(self.cart_frame, text=f"Total: ₱{total:.2f}", font=("Arial", 13, "bold")).pack(pady=5)

    def place_order(self):
        if not self.cart:
            messagebox.showwarning("Cart", "Cart is empty.")
            return
        order_details = "; ".join(f"{item['name']} x{item['qty']}" for item in self.cart)
        total = sum(item['price']*item['qty'] for item in self.cart)
        from datetime import datetime
        orders.append({
            "user_id": self.user_id,
            "order_details": order_details,
            "total_price": total,
            "order_time": datetime.now(),
            "served": 0
        })
        self.cart.clear()
        self.refresh_cart()
        messagebox.showinfo("Order", "Order placed!")
        from customer_orders import CustomerOrdersWindow
        CustomerOrdersWindow(self.master, self.user_id, self.username)
        self.destroy()