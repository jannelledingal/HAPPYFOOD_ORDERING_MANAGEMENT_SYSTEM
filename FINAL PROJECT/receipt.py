import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime

class ReceiptWindow(tk.Toplevel):
    def __init__(self, master, items, total):
        super().__init__(master)
        self.title("Receipt")
        self.geometry("380x420")
        self.items = items
        self.total = total
        self.create_widgets()

    def create_widgets(self):
        txt = tk.Text(self, wrap="word", state="normal")
        txt.pack(fill="both", expand=True, padx=8, pady=8)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"HappyFood Receipt\nDate: {now}\n\n"
        txt.insert("end", header)
        for it in self.items:
            # support dict format
            name = it.get("name") if isinstance(it, dict) else (it[0] if isinstance(it, (list,tuple)) else str(it))
            if isinstance(it, dict):
                qty = it.get("qty", 1)
                size = it.get("size", "M")
                unit = float(it.get("unit_price", it.get("price", 0)))
                subtotal = float(it.get("\nsubtotal", unit * qty))
                txt.insert("end", f"{qty} x {name} ({size})  ₱{unit:.2f}  Subtotal: ₱{subtotal:.2f}\n")
            else:
                txt.insert("end", f"{name}  ₱{float(it[1]):.2f}\n")
        txt.insert("end", f"\nTotal: ₱{self.total:.2f}\n")
        txt.config(state="disabled")
        btnf = tk.Frame(self)
        btnf.pack(fill="x", padx=8, pady=6)
        tk.Button(btnf, text="Save Receipt", command=self.save_receipt).pack(side="left", padx=4)
        tk.Button(btnf, text="Close", command=self.destroy).pack(side="right", padx=4)

    def save_receipt(self):
        default = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=default, filetypes=[("Text", "*.txt")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"HappyFood Receipt\nDate: {datetime.now().isoformat()}\n\n")
                for it in self.items:
                    if isinstance(it, dict):
                        qty = it.get("qty",1); size = it.get("size","M")
                        unit = float(it.get("unit_price",0)); subtotal = float(it.get("subtotal", unit*qty))
                        f.write(f"{qty} x {it.get('name')} ({size})  ₱{unit:.2f} Subtotal: ₱{subtotal:.2f}\n")
                    else:
                        f.write(f"{it[0]}  ₱{float(it[1]):.2f}\n")
                f.write(f"\nTotal: ₱{self.total:.2f}\n")
            messagebox.showinfo("Saved", f"Receipt saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))