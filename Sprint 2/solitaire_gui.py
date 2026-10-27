
import tkinter as tk
from tkinter import messagebox, ttk
from solitaire_game import SolitaireGame

BACKGROUND = "#f4f7fb"  # Same Sprint 0 palette
BLUE = "#2f80ed"
NAVY = "#173b62"
BOARD = "#e9c46a"
HOLE = "#b48a4d"


class SolitaireGUI:
    """Render the model and translate button/canvas events into model calls."""

    def __init__(self, root):
        self.root = root
        self.root.title("Peg Solitaire | CS 449 Sprint 2")
        self.root.geometry("1060x720")
        self.root.minsize(920, 650)
        self.root.configure(bg=BACKGROUND)
        self.game = SolitaireGame()
        self.board_type = tk.StringVar(value=self.game.board_type)
        self.board_size = tk.StringVar(value=str(self.game.size))
        self.status = tk.StringVar(value="Select a peg to begin.")
        self.moves_var = tk.StringVar(value="0")
        self.pegs_var = tk.StringVar(value="32")
        self.best_var = tk.StringVar(value="32")
        self.selected = None
        self.cell_bounds = {}
        self._configure_styles()
        self._build_layout()
        self.root.after_idle(self.draw_board)

    @staticmethod
    def _configure_styles():
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
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 5))
        style.configure("Primary.TButton", background=BLUE, foreground="white",
                        font=("Segoe UI", 10, "bold"), padding=(12, 5))

    def _build_layout(self):
        header = tk.Frame(self.root, bg=BLUE, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)
        ttk.Label(header, text="PEG SOLITAIRE", style="Title.TLabel").pack(
            anchor="w", padx=42, pady=24)

        content = tk.Frame(self.root, bg=BACKGROUND)
        content.pack(fill="both", expand=True, padx=28, pady=24)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        controls = ttk.Frame(content, style="Card.TFrame", padding=16)
        controls.grid(row=0, column=0, sticky="nsw", padx=(0, 22))
        ttk.Label(controls, text="Game setup", style="Section.TLabel").pack(anchor="w")
        ttk.Label(controls, text="Board type", style="Info.TLabel").pack(
            anchor="w", pady=(18, 5))
        for name in SolitaireGame.SUPPORTED_TYPES:
            ttk.Radiobutton(controls, text=name, value=name,
                            variable=self.board_type).pack(anchor="w", pady=3)

        ttk.Label(controls, text="Board size", style="Info.TLabel").pack(
            anchor="w", pady=(18, 5))
        # Editable to demonstrate rejected input (Sprint 1 AC 1.2).
        self.size_box = ttk.Combobox(controls, textvariable=self.board_size,
                                     values=SolitaireGame.SUPPORTED_SIZES, width=9)
        self.size_box.pack(anchor="w")
        self.size_box.bind("<Return>", lambda _event: self.new_game())
        self.record_game = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="Record game", variable=self.record_game,
                        state="disabled").pack(anchor="w", pady=(14, 0))
        ttk.Separator(controls, orient="horizontal").pack(fill="x", pady=12)
        ttk.Button(controls, text="New game", style="Primary.TButton",
                   command=self.new_game).pack(fill="x", pady=2)
        for future_name in ("Replay", "Randomize", "Autoplay", "Tutorial"):
            ttk.Button(controls, text=future_name, style="Action.TButton",
                       state="disabled").pack(fill="x", pady=2)

        board_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        board_card.grid(row=0, column=1, sticky="nsew")
        board_card.grid_rowconfigure(1, weight=1)
        board_card.grid_columnconfigure(0, weight=1)
        board_card.grid_columnconfigure(1, minsize=220)
        top = tk.Frame(board_card, bg="white")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(top, text="Game board", style="Section.TLabel").pack(side="left")
        self.board_caption = ttk.Label(top, text="English board", style="Info.TLabel")
        self.board_caption.pack(side="right")

        self.canvas = tk.Canvas(board_card, bg="white", highlightthickness=0,
                                cursor="hand2")
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self.on_board_click)
        self.canvas.bind("<Configure>", lambda _event: self.draw_board())

        panel = ttk.Frame(board_card, style="Card.TFrame", padding=(18, 12))
        panel.grid(row=1, column=1, sticky="nsew", padx=(12, 0))
        ttk.Label(panel, text="Game status", style="Section.TLabel").pack(anchor="w")
        ttk.Label(panel, text="LIVE STATISTICS", style="MetricName.TLabel").pack(
            anchor="w", pady=(14, 4))
        metrics = tk.Frame(panel, bg="white")
        metrics.pack(fill="x")
        for value, label in ((self.moves_var, "MOVES"), (self.pegs_var, "PEGS"),
                             (self.best_var, "BEST")):
            item = tk.Frame(metrics, bg="white")
            item.pack(side="left", expand=True, fill="x")
            ttk.Label(item, textvariable=value, style="Metric.TLabel").pack()
            ttk.Label(item, text=label, style="MetricName.TLabel").pack()
        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=20)
        ttk.Label(panel, text="Move history", style="Section.TLabel").pack(anchor="w")
        self.history = tk.Listbox(panel, height=10, bg="#f8fafc", fg="#40546b",
                                  font=("Segoe UI", 9), relief="flat",
                                  highlightthickness=1,
                                  highlightbackground="#d7e0eb")
        self.history.insert(tk.END, "Recording available in Sprint 5.")
        self.history.pack(fill="both", expand=True, pady=(8, 0))
        ttk.Button(panel, text="Open tutorial", style="Action.TButton",
                   state="disabled").pack(fill="x", pady=(12, 0))
        footer = tk.Label(self.root, textvariable=self.status,
                          bg=BACKGROUND, fg="#4b6078", font=("Segoe UI", 10))
        footer.pack(anchor="w", padx=42, pady=(0, 14))

    def new_game(self):
        """Apply selected setup safely; invalid size preserves previous game."""
        try:
            self.game.new_game(size=self.board_size.get(),
                               board_type=self.board_type.get())
        except ValueError as error:
            self.board_size.set(str(self.game.size))
            self.board_type.set(self.game.board_type)
            self.status.set(f"Invalid configuration: {error}")
            messagebox.showerror("Invalid board size or type", str(error),
                                 parent=self.root)
            return False
        self.selected = None
        self.best_var.set(str(self.game.remaining_pegs()))
        self.status.set(f"New {self.game.board_type} game ({self.game.size} x "
                        f"{self.game.size}) started.")
        self.draw_board()
        return True

    def on_board_click(self, event):
        position = next((p for p, rect in self.cell_bounds.items()
                         if rect[0] <= event.x <= rect[2] and
                         rect[1] <= event.y <= rect[3]), None)
        if position is None:
            return
        if self.game.is_game_over():
            self.status.set(f"Game over: {self.game.final_rating()}.")
        elif self.selected is None:
            if self.game.board[position]:
                self.selected = position
                self.status.set("Peg selected. Choose an empty destination.")
            else:
                self.status.set("Select a peg first.")
        elif self.selected == position:
            self.selected = None
            self.status.set("Selection cleared.")
        elif self.game.make_move(self.selected, position):
            self.selected = None
            if self.game.is_game_over():
                self.status.set(f"Game over: {self.game.final_rating()} "
                                f"({self.game.remaining_pegs()} pegs left).")
            else:
                self.status.set(f"Valid move. {self.game.remaining_pegs()} pegs remain.")
        elif self.game.board[position]:
            self.selected = position
            self.status.set("Different peg selected.")
        else:
            self.status.set("Invalid jump. Board unchanged.")
        self.draw_board()

    def draw_board(self):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        self.canvas.update_idletasks()
        size = self.game.size
        width = max(self.canvas.winfo_width(), 500)
        height = max(self.canvas.winfo_height(), 500)
        cell = min((width - 90) / size, (height - 80) / size, 78)
        offset_x = (width - cell * size) / 2
        offset_y = (height - cell * size) / 2
        self.cell_bounds = {}
        for (row, col), occupied in sorted(self.game.board.items()):
            x1, y1 = offset_x + col * cell, offset_y + row * cell
            x2, y2 = x1 + cell, y1 + cell
            self.cell_bounds[(row, col)] = (x1, y1, x2, y2)
            self.canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                                         fill=BOARD, outline="#b68e3e", width=1)
            center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
            radius = cell * .29
            self.canvas.create_oval(center_x - radius, center_y - radius,
                                    center_x + radius, center_y + radius,
                                    fill=HOLE, outline="#8e6b35", width=2)
            if occupied:
                color = "#f4b942" if (row, col) == self.selected else BLUE
                self.canvas.create_oval(
                    center_x - radius*.72, center_y - radius*.72,
                    center_x + radius*.72, center_y + radius*.72,
                    fill=color, outline="#163d6b", width=2)
                self.canvas.create_oval(
                    center_x - radius*.42, center_y - radius*.52,
                    center_x + radius*.10, center_y - radius*.04,
                    fill="white", outline="", stipple="gray50")
        self.moves_var.set(str(self.game.move_count))
        self.pegs_var.set(str(self.game.remaining_pegs()))
        self.board_caption.configure(text=f"{self.game.board_type} board / "
                                          f"size {size}")
        try:
            previous = int(self.best_var.get())
        except ValueError:
            previous = self.game.remaining_pegs()
        self.best_var.set(str(min(previous, self.game.remaining_pegs())))


def main():
    root = tk.Tk()
    SolitaireGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
