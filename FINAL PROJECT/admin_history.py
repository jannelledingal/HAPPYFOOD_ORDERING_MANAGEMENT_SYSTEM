import tkinter as tk
from tkinter import messagebox
import db
from colors import PINK, LIGHT_PINK, WHITE, DARK_GRAY

# Accessibility
BTN_FONT = ("Helvetica", 13, "bold")
BTN_PADY = 10
HEADER_FONT = ("Helvetica", 16, "bold")
LIST_FONT = ("Helvetica", 11)
LABEL_FONT = ("Helvetica", 12, "bold")

# optional matplotlib for charts
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

class AdminHistoryWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Orders History & Earnings")
        self.resizable(True, True)
        try:
            self.state('zoomed')
        except Exception:
            pass
        self.configure(bg=LIGHT_PINK)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_widgets()
        self.load_summary()

    def create_widgets(self):
        header = tk.Frame(self, bg=PINK, height=64)
        header.grid(row=0, column=0, sticky="nsew")
        tk.Label(header, text="🕒 Orders Summary & Earnings", bg=PINK, fg=WHITE, font=HEADER_FONT).pack(side="left", padx=16, pady=12)

        # main frame with left list and right charts
        self.frm = tk.Frame(self, bg=WHITE)
        self.frm.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        self.frm.rowconfigure(0, weight=1)
        # left column fixed (summary), right column expands (charts)
        self.frm.columnconfigure(0, weight=0, minsize=300)
        self.frm.columnconfigure(1, weight=1)

        # left: textual summary list + controls
        left = tk.Frame(self.frm, bg=WHITE, bd=1, relief="solid")
        left.grid(row=0, column=0, sticky="nsew", padx=(0,8), pady=0)
        left.rowconfigure(1, weight=1)

        tk.Label(left, text="Summary", bg=WHITE, font=LABEL_FONT).grid(row=0, column=0, sticky="w", padx=12, pady=(8,6))

        list_frame = tk.Frame(left, bg=WHITE)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=8)
        list_frame.rowconfigure(0, weight=1); list_frame.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(list_frame, height=20, font=LIST_FONT, bd=0, activestyle="none", highlightthickness=0)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        vsb = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.listbox.configure(yscrollcommand=vsb.set)

        btnf = tk.Frame(left, bg=WHITE)
        btnf.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        tk.Button(btnf, text="Refresh", command=self.load_summary, font=BTN_FONT, padx=12, pady=BTN_PADY, bg=PINK, fg=WHITE, bd=0).pack(side="left", padx=6)
        tk.Button(btnf, text="Close", command=self.destroy, font=BTN_FONT, padx=12, pady=BTN_PADY, bg="#666", fg=WHITE, bd=0).pack(side="right", padx=6)

        # right: charts area (card style)
        charts_card = tk.Frame(self.frm, bg=WHITE, bd=1, relief="solid")
        charts_card.grid(row=0, column=1, sticky="nsew", padx=(8,0), pady=0)
        charts_card.rowconfigure(0, weight=1); charts_card.columnconfigure(0, weight=1)

        # placeholder label while charts are drawn
        self.charts_frame = tk.Frame(charts_card, bg=WHITE)
        self.charts_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.charts_frame.rowconfigure(0, weight=1); self.charts_frame.columnconfigure(0, weight=1)

        if not MATPLOTLIB_AVAILABLE:
            ph = tk.Label(self.charts_frame, text="Matplotlib not installed.\nInstall with: pip install matplotlib", bg=WHITE, fg=DARK_GRAY, justify="center", font=LIST_FONT)
            ph.place(relx=0.5, rely=0.5, anchor="center")

    def load_summary(self):
        try:
            summary = db.get_orders_summary()
            self.listbox.delete(0, "end")
            keys = ("today","yesterday","week","month","year")
            for key in keys:
                s = summary.get(key, {"count":0,"total":0.0})
                self.listbox.insert("end", f"{key.title():<10}  Orders: {s['count']:<4}   Earned: ₱{s['total']:.2f}")
            # update charts on right
            self._update_charts(summary, keys)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load summary: {e}")

    def _update_charts(self, summary, keys):
        # clear previous charts
        for w in self.charts_frame.winfo_children():
            w.destroy()

        if not MATPLOTLIB_AVAILABLE:
            ph = tk.Label(self.charts_frame, text="Matplotlib not installed.\nInstall with: pip install matplotlib", bg=WHITE, fg=DARK_GRAY, justify="center", font=LIST_FONT)
            ph.place(relx=0.5, rely=0.5, anchor="center")
            return

        # prepare data
        counts = [summary.get(k, {}).get("count", 0) for k in keys]
        totals = [summary.get(k, {}).get("total", 0.0) for k in keys]

        # create figure sized to available area (fallback to sensible default)
        fig_width = 8
        fig_height = 6
        try:
            # try to approximate using charts_frame size (may be 1 initially)
            w = max(600, self.charts_frame.winfo_width())
            h = max(300, self.charts_frame.winfo_height())
            fig_width = max(6, w / 100)
            fig_height = max(4, h / 100)
        except Exception:
            pass

        fig, axes = plt.subplots(2, 1, figsize=(fig_width, fig_height), constrained_layout=True)
        # style bars
        x_labels = [k.title() for k in keys]

        # orders count bar chart
        axes[0].bar(x_labels, counts, color="#ff7aa2", edgecolor="#e75c88")
        axes[0].set_title("Orders Count", fontsize=13)
        axes[0].set_ylabel("Orders")
        axes[0].grid(axis="y", linestyle="--", alpha=0.2)
        for i, v in enumerate(counts):
            axes[0].text(i, v + max(0.5, max(counts)*0.02), str(v), ha="center", va="bottom", fontsize=10)

        # earnings bar chart
        axes[1].bar(x_labels, totals, color="#ff4d7a", edgecolor="#e73b5a")
        axes[1].set_title("Earnings (₱)", fontsize=13)
        axes[1].set_ylabel("₱")
        axes[1].grid(axis="y", linestyle="--", alpha=0.2)
        for i, v in enumerate(totals):
            axes[1].text(i, v + max(1.0, max(totals)*0.01), f"₱{v:.2f}", ha="center", va="bottom", fontsize=10)

        # remove top/right spines for cleaner look
        for ax in axes:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)
        # allow responsive redraw when window resizes
        def _on_resize(event):
            try:
                # small debounce: redraw figure to fit new size
                widget.configure(width=event.width, height=event.height)
            except Exception:
                pass
        self.charts_frame.bind("<Configure>", lambda e: canvas.draw())