

import tkinter as tk
from tkinter import ttk


BACKGROUND = "#f4f7fb"
BLUE = "#2f80ed"
NAVY = "#173b62"
BOARD = "#e9c46a"
HOLE = "#b48a4d"


def configure_styles():
    """Set the visual styling used by the static cover."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Card.TFrame", background="white")
    style.configure("Title.TLabel", background=BLUE, foreground="white",
                    font=("Segoe UI", 24, "bold"))
    style.configure("Section.TLabel", background="white", foreground=NAVY,
                    font=("Segoe UI", 12, "bold"))
    style.configure("Info.TLabel", background="white", foreground="#506176",
                    font=("Segoe UI", 10))
    style.configure("Metric.TLabel", background="white", foreground=NAVY,
                    font=("Segoe UI", 19, "bold"))
    style.configure("MetricName.TLabel", background="white", foreground="#63758b",
                    font=("Segoe UI", 9))
    style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8))
    style.configure("Primary.TButton", background=BLUE, foreground="white",
                    font=("Segoe UI", 10, "bold"), padding=(12, 8))


def draw_initial_board(canvas):
    """Draw the initial English board with its central hole empty."""
    canvas.delete("all")
    canvas.update_idletasks()
    width = max(canvas.winfo_width(), 600)
    height = max(canvas.winfo_height(), 500)
    cell = min((width - 90) / 7, (height - 80) / 7, 78)
    offset_x = (width - cell * 7) / 2
    offset_y = (height - cell * 7) / 2

    for row in range(7):
        for col in range(7):
            if not (2 <= row <= 4 or 2 <= col <= 4):
                continue
            x1 = offset_x + col * cell
            y1 = offset_y + row * cell
            x2 = x1 + cell
            y2 = y1 + cell
            canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                                    fill=BOARD, outline="#b68e3e", width=1)
            center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
            radius = cell * 0.29
            canvas.create_oval(center_x - radius, center_y - radius,
                               center_x + radius, center_y + radius,
                               fill=HOLE, outline="#8e6b35", width=2)
            if (row, col) == (3, 3):
                continue
            canvas.create_oval(center_x - radius * 0.72, center_y - radius * 0.72,
                               center_x + radius * 0.72, center_y + radius * 0.72,
                               fill=BLUE, outline="#163d6b", width=2)
            canvas.create_oval(center_x - radius * 0.42, center_y - radius * 0.52,
                               center_x + radius * 0.10, center_y - radius * 0.04,
                               fill="white", outline="", stipple="gray50")


def build_gui(root):
    """Build the non-interactive cover window."""
    root.title("Peg Solitaire | Sprint 0 GUI Cover")
    root.geometry("1060x720")
    root.minsize(920, 650)
    root.configure(bg=BACKGROUND)
    configure_styles()

    header = tk.Frame(root, bg=BLUE, height=90)
    header.pack(fill="x")
    header.pack_propagate(False)
    ttk.Label(header, text="PEG SOLITAIRE", style="Title.TLabel").pack(
        anchor="w", padx=42, pady=24
    )

    content = tk.Frame(root, bg=BACKGROUND)
    content.pack(fill="both", expand=True, padx=28, pady=24)
    content.grid_columnconfigure(1, weight=1)
    content.grid_rowconfigure(0, weight=1)

    controls = ttk.Frame(content, style="Card.TFrame", padding=22)
    controls.grid(row=0, column=0, sticky="nsw", padx=(0, 22))
    ttk.Label(controls, text="Game setup", style="Section.TLabel").pack(anchor="w")
    ttk.Label(controls, text="Board type", style="Info.TLabel").pack(anchor="w", pady=(18, 5))
    board_type = tk.StringVar(value="English")
    for name in ("English", "Hexagon", "Diamond"):
        ttk.Radiobutton(controls, text=name, value=name, variable=board_type).pack(anchor="w", pady=3)
    ttk.Label(controls, text="Board size", style="Info.TLabel").pack(anchor="w", pady=(18, 5))
    board_size = tk.StringVar(value="7")
    ttk.Combobox(controls, textvariable=board_size, values=(5, 7, 9),
                 state="readonly", width=9).pack(anchor="w")
    ttk.Checkbutton(controls, text="Record game").pack(anchor="w", pady=(14, 0))
    ttk.Separator(controls, orient="horizontal").pack(fill="x", pady=22)
    for text, style in (("New game", "Primary.TButton"), ("Replay", "Action.TButton"),
                        ("Randomize", "Action.TButton"), ("Autoplay", "Action.TButton"),
                        ("Tutorial", "Action.TButton")):
        ttk.Button(controls, text=text, style=style).pack(fill="x", pady=4)

    board_card = ttk.Frame(content, style="Card.TFrame", padding=18)
    board_card.grid(row=0, column=1, sticky="nsew")
    board_card.grid_rowconfigure(1, weight=1)
    board_card.grid_columnconfigure(0, weight=1)
    board_card.grid_columnconfigure(1, minsize=220)
    top = tk.Frame(board_card, bg="white")
    top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
    ttk.Label(top, text="Game board", style="Section.TLabel").pack(side="left")
    ttk.Label(top, text="Initial English board", style="Info.TLabel").pack(side="right")

    canvas = tk.Canvas(board_card, bg="white", highlightthickness=0)
    canvas.grid(row=1, column=0, sticky="nsew")
    canvas.bind("<Configure>", lambda _event: draw_initial_board(canvas))
    root.after_idle(lambda: draw_initial_board(canvas))

    panel = ttk.Frame(board_card, style="Card.TFrame", padding=(18, 12))
    panel.grid(row=1, column=1, sticky="nsew", padx=(12, 0))
    ttk.Label(panel, text="Game status", style="Section.TLabel").pack(anchor="w")
    ttk.Label(panel, text="LIVE STATISTICS", style="MetricName.TLabel").pack(
        anchor="w", pady=(14, 4)
    )
    metrics = tk.Frame(panel, bg="white")
    metrics.pack(fill="x")
    for value, label in (("0", "MOVES"), ("32", "PEGS"), ("32", "BEST")):
        item = tk.Frame(metrics, bg="white")
        item.pack(side="left", expand=True, fill="x")
        ttk.Label(item, text=value, style="Metric.TLabel").pack()
        ttk.Label(item, text=label, style="MetricName.TLabel").pack()
    ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=20)
    ttk.Label(panel, text="Move history", style="Section.TLabel").pack(anchor="w")
    history = tk.Listbox(panel, height=10, bg="#f8fafc", fg="#40546b",
                         font=("Segoe UI", 9), relief="flat", highlightthickness=1,
                         highlightbackground="#d7e0eb")
    history.insert(tk.END, "Turn on Record game to save")
    history.insert(tk.END, "moves here.")
    history.pack(fill="both", expand=True, pady=(8, 0))
    ttk.Button(panel, text="Open tutorial", style="Action.TButton").pack(
        fill="x", pady=(12, 0)
    )


def main():
    root = tk.Tk()
    build_gui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
