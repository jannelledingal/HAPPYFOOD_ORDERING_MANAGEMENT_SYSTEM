import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import random

class ReceiptWindow(tk.Toplevel):
    def __init__(self, master, items, total, order_id=None):
        super().__init__(master)
        self.title("Receipt")
        self.geometry("420x480")
        self.items = items
        self.total = total
        self.order_id = order_id or f"X{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"
        self.create_widgets()

    def create_widgets(self):
        txt = tk.Text(self, wrap="word", state="normal", font=("Courier", 10))
        txt.pack(fill="both", expand=True, padx=8, pady=8)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"HappyFood Receipt\nOrder No: {self.order_id}\nDate: {now}\n\n"
        txt.insert("end", header)
        for it in self.items:
            if isinstance(it, dict):
                qty = it.get("qty", 1)
                size = it.get("size", "M")
                unit = float(it.get("unit_price", it.get("price", 0)))
                subtotal = float(it.get("subtotal", unit * qty))
                txt.insert("end", f"{qty} x {it.get('name')[:30]:30} ({size})  ₱{unit:7.2f}  Subtotal: ₱{subtotal:7.2f}\n")
            else:
                name = it[0] if isinstance(it, (list,tuple)) else str(it)
                price = float(it[1]) if isinstance(it, (list,tuple)) and len(it)>1 else 0.0
                txt.insert("end", f"{name:30}  ₱{price:7.2f}\n")
        txt.insert("end", f"\nTotal: ₱{self.total:.2f}\n")
        txt.config(state="disabled")

        btnf = tk.Frame(self)
        btnf.pack(fill="x", padx=8, pady=6)
        tk.Button(btnf, text="Save Receipt", command=self.save_receipt).pack(side="left", padx=4)
        tk.Button(btnf, text="Close", command=self.destroy).pack(side="right", padx=4)

    def save_receipt(self):
        default = f"receipt_{self.order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=default, filetypes=[("Text", "*.txt")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"HappyFood Receipt\nOrder No: {self.order_id}\nDate: {datetime.now().isoformat()}\n\n")
                for it in self.items:
                    if isinstance(it, dict):
                        qty = it.get("qty",1); size = it.get("size","M")
                        unit = float(it.get("unit_price",0)); subtotal = float(it.get("subtotal", unit*qty))
                        f.write(f"{qty} x {it.get('name')} ({size})  ₱{unit:.2f}  Subtotal: ₱{subtotal:.2f}\n")
                    else:
                        f.write(f"{it[0]}  ₱{float(it[1]):.2f}\n")
                f.write(f"\nTotal: ₱{self.total:.2f}\n")
            messagebox.showinfo("Saved", f"Receipt saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))