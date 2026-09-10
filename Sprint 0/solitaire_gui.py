"""An interactive Peg Solitaire GUI for the CS 449 project.

Click a peg, then click an empty hole two spaces away to make a move.
"""

import random
import tkinter as tk
from tkinter import messagebox, ttk


class SolitaireGUI:
    """Provide a playable, polished Tkinter interface for Peg Solitaire."""

    BACKGROUND = "#f4f7fb"
    NAVY = "#173b62"
    BLUE = "#2f80ed"
    GOLD = "#f4b942"
    BOARD = "#e9c46a"
    HOLE = "#b48a4d"

    def __init__(self, root):
        self.root = root
        self.root.title("Peg Solitaire | CS 449")
        self.root.geometry("1060x720")
        self.root.minsize(920, 650)
        self.root.configure(bg=self.BACKGROUND)

        self.board_type = tk.StringVar(value="English")
        self.board_size = tk.IntVar(value=7)
        self.record_game = tk.BooleanVar(value=False)
        self.status = tk.StringVar()
        self.moves_var = tk.StringVar(value="0")
        self.pegs_var = tk.StringVar(value="0")
        self.best_var = tk.StringVar(value="--")
        self.selected = None
        self.move_count = 0
        self.autoplay_job = None
        self.board = {}
        self.cell_bounds = {}
        self.recorded_moves = []

        self._configure_styles()
        self._build_layout()
        self.new_game()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Card.TFrame", background="white")
        style.configure("Title.TLabel", background=self.BLUE, foreground="white",
                        font=("Segoe UI", 24, "bold"))
        style.configure("Section.TLabel", background="white", foreground=self.NAVY,
                        font=("Segoe UI", 12, "bold"))
        style.configure("Metric.TLabel", background="white", foreground=self.NAVY,
                        font=("Segoe UI", 19, "bold"))
        style.configure("MetricName.TLabel", background="white", foreground="#63758b",
                        font=("Segoe UI", 9))
        style.configure("Info.TLabel", background="white", foreground="#506176",
                        font=("Segoe UI", 10))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.configure("Primary.TButton", background=self.BLUE, foreground="white",
                        font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.map("Primary.TButton", background=[("active", "#1769cf")])

    def _build_layout(self):
        header = tk.Frame(self.root, bg=self.BLUE, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)
        ttk.Label(header, text="PEG SOLITAIRE", style="Title.TLabel").pack(
            anchor="w", padx=42, pady=24
        )

        content = tk.Frame(self.root, bg=self.BACKGROUND)
        content.pack(fill="both", expand=True, padx=28, pady=24)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        controls = ttk.Frame(content, style="Card.TFrame", padding=22)
        controls.grid(row=0, column=0, sticky="nsw", padx=(0, 22))
        self._build_controls(controls)

        board_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        board_card.grid(row=0, column=1, sticky="nsew")
        board_card.grid_rowconfigure(1, weight=1)
        board_card.grid_columnconfigure(0, weight=1)
        board_card.grid_columnconfigure(1, minsize=220)
        top = tk.Frame(board_card, bg="white")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(top, text="Game board", style="Section.TLabel").pack(side="left")
        ttk.Label(top, text="Click a peg, then an empty destination", style="Info.TLabel").pack(side="right")
        self.canvas = tk.Canvas(board_card, bg="white", highlightthickness=0, cursor="hand2")
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self.on_board_click)
        self._build_game_info(board_card)

        footer = tk.Frame(self.root, bg=self.BACKGROUND)
        footer.pack(fill="x", padx=42, pady=(0, 18))
        tk.Label(footer, textvariable=self.status, bg=self.BACKGROUND, fg="#4b6078",
                 font=("Segoe UI", 10)).pack(side="left")
        tk.Label(footer, text="Tip: a legal jump crosses exactly one peg.", bg=self.BACKGROUND,
                 fg="#78879a", font=("Segoe UI", 10)).pack(side="right")

    def _build_controls(self, parent):
        ttk.Label(parent, text="Game setup", style="Section.TLabel").pack(anchor="w")
        ttk.Label(parent, text="Board type", style="Info.TLabel").pack(anchor="w", pady=(18, 5))
        for name in ("English", "Hexagon", "Diamond"):
            ttk.Radiobutton(parent, text=name, value=name, variable=self.board_type,
                            command=self.new_game).pack(anchor="w", pady=3)

        ttk.Label(parent, text="Board size", style="Info.TLabel").pack(anchor="w", pady=(18, 5))
        size_menu = ttk.Combobox(parent, textvariable=self.board_size, state="readonly",
                                 values=(5, 7, 9), width=9)
        size_menu.pack(anchor="w")
        size_menu.bind("<<ComboboxSelected>>", lambda _event: self.new_game())
        ttk.Checkbutton(parent, text="Record game", variable=self.record_game,
                        command=self.refresh_move_history).pack(
            anchor="w", pady=(14, 0)
        )

        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=22)
        ttk.Button(parent, text="New game", style="Primary.TButton", command=self.new_game).pack(fill="x", pady=4)
        ttk.Button(parent, text="Replay", style="Action.TButton", command=self.replay).pack(fill="x", pady=4)
        ttk.Button(parent, text="Randomize", style="Action.TButton", command=self.randomize).pack(fill="x", pady=4)
        self.autoplay_button = ttk.Button(parent, text="Autoplay", style="Action.TButton",
                                          command=self.toggle_autoplay)
        self.autoplay_button.pack(fill="x", pady=4)
        ttk.Button(parent, text="Tutorial", style="Action.TButton", command=self.show_tutorial).pack(
            fill="x", pady=4
        )

    def _build_game_info(self, parent):
        """Use the space beside the board for game status and recorded moves."""
        panel = ttk.Frame(parent, style="Card.TFrame", padding=(18, 12))
        panel.grid(row=1, column=1, sticky="nsew", padx=(12, 0))
        ttk.Label(panel, text="Game status", style="Section.TLabel").pack(anchor="w")
        ttk.Label(panel, text="LIVE STATISTICS", style="MetricName.TLabel").pack(
            anchor="w", pady=(14, 4)
        )
        metric_row = tk.Frame(panel, bg="white")
        metric_row.pack(fill="x")
        for value, label in ((self.moves_var, "MOVES"), (self.pegs_var, "PEGS"), (self.best_var, "BEST")):
            item = tk.Frame(metric_row, bg="white")
            item.pack(side="left", expand=True, fill="x")
            ttk.Label(item, textvariable=value, style="Metric.TLabel").pack()
            ttk.Label(item, text=label, style="MetricName.TLabel").pack()

        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=20)
        ttk.Label(panel, text="Move history", style="Section.TLabel").pack(anchor="w")
        self.history_list = tk.Listbox(panel, height=10, bg="#f8fafc", fg="#40546b",
                                       font=("Segoe UI", 9), relief="flat", highlightthickness=1,
                                       highlightbackground="#d7e0eb", selectbackground=self.BLUE)
        ttk.Button(panel, text="Open tutorial", style="Action.TButton", command=self.show_tutorial).pack(
            fill="x", side="bottom", pady=(12, 0)
        )
        self.history_list.pack(fill="both", expand=True, pady=(8, 0))

    def show_tutorial(self):
        """Show the concise game instructions in a separate dialog."""
        messagebox.showinfo(
            "Peg Solitaire Tutorial",
            "1. Select a blue peg.\n\n"
            "2. Click an empty hole exactly two spaces away.\n\n"
            "3. The peg between them is removed.\n\n"
            "Goal: finish with one peg remaining."
        )

    def refresh_move_history(self):
        """Refresh the right-side move history panel."""
        self.history_list.delete(0, tk.END)
        if not self.record_game.get():
            self.history_list.insert(tk.END, "Turn on Record game to save")
            self.history_list.insert(tk.END, "moves here.")
        elif not self.recorded_moves:
            self.history_list.insert(tk.END, "No moves recorded yet.")
        else:
            for move in self.recorded_moves:
                self.history_list.insert(tk.END, move)
            self.history_list.see(tk.END)

    def valid_positions(self):
        size = self.board_size.get()
        center = size // 2
        positions = set()
        for row in range(size):
            for col in range(size):
                if self.board_type.get() == "English":
                    arm = center - 1
                    valid = arm <= row <= size - arm - 1 or arm <= col <= size - arm - 1
                elif self.board_type.get() == "Hexagon":
                    q, r = col - center, row - center
                    valid = max(abs(q), abs(r), abs(-q - r)) <= center
                else:
                    valid = abs(row - center) + abs(col - center) <= center
                if valid:
                    positions.add((row, col))
        return positions

    def new_game(self):
        self.stop_autoplay()
        positions = self.valid_positions()
        center = (self.board_size.get() // 2, self.board_size.get() // 2)
        self.board = {position: position != center for position in positions}
        self.selected = None
        self.move_count = 0
        self.recorded_moves = []
        self.refresh_move_history()
        self.status.set(f"New {self.board_type.get()} board ready. Select a peg to begin.")
        self.draw_board()

    def replay(self):
        self.new_game()
        self.status.set("Opening position restored.")

    def randomize(self):
        self.stop_autoplay()
        positions = self.valid_positions()
        empty = random.choice(tuple(positions))
        self.board = {position: position != empty for position in positions}
        self.selected = None
        self.move_count = 0
        self.recorded_moves = []
        self.refresh_move_history()
        self.status.set("Random opening created. Find a legal jump!")
        self.draw_board()

    @staticmethod
    def middle_position(start, end):
        row_change, col_change = abs(end[0] - start[0]), abs(end[1] - start[1])
        if (row_change, col_change) not in ((2, 0), (0, 2), (2, 2)):
            return None
        return ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)

    def is_valid_move(self, start, end):
        middle = self.middle_position(start, end)
        return (middle is not None and start in self.board and middle in self.board and end in self.board
                and self.board[start] and self.board[middle] and not self.board[end])

    def legal_moves(self):
        moves = []
        for start, has_peg in self.board.items():
            if not has_peg:
                continue
            for row_delta, col_delta in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)):
                end = (start[0] + row_delta, start[1] + col_delta)
                if self.is_valid_move(start, end):
                    moves.append((start, end))
        return moves

    def make_move(self, start, end):
        middle = self.middle_position(start, end)
        self.board[start] = False
        self.board[middle] = False
        self.board[end] = True
        self.move_count += 1
        self.selected = None
        if self.record_game.get():
            self.recorded_moves.append(
                f"{self.move_count:02}: ({start[0] + 1}, {start[1] + 1}) to ({end[0] + 1}, {end[1] + 1})"
            )
            self.refresh_move_history()
        pegs = sum(self.board.values())
        if pegs == 1:
            self.status.set("Excellent — you solved the board!")
        elif not self.legal_moves():
            self.status.set(f"No more legal moves. {pegs} pegs remain.")
        else:
            self.status.set(f"Move {self.move_count} completed. {pegs} pegs remain.")
        self.draw_board()

    def on_board_click(self, event):
        position = next((pos for pos, bounds in self.cell_bounds.items()
                         if bounds[0] <= event.x <= bounds[2] and bounds[1] <= event.y <= bounds[3]), None)
        if position is None:
            return
        if self.selected is None:
            if self.board[position]:
                self.selected = position
                self.status.set("Peg selected. Now click an empty hole two spaces away.")
            else:
                self.status.set("Choose a peg first.")
        elif position == self.selected:
            self.selected = None
            self.status.set("Selection cleared.")
        elif self.is_valid_move(self.selected, position):
            self.make_move(self.selected, position)
            return
        elif self.board[position]:
            self.selected = position
            self.status.set("New peg selected. Choose an empty destination.")
        else:
            self.status.set("That is not a legal jump. Cross one peg and land in an empty hole.")
        self.draw_board()

    def toggle_autoplay(self):
        if self.autoplay_job:
            self.stop_autoplay()
            self.status.set("Autoplay paused.")
        else:
            self.status.set("Autoplay is making legal moves.")
            self.autoplay_button.configure(text="Pause autoplay")
            self.autoplay_step()

    def autoplay_step(self):
        moves = self.legal_moves()
        if not moves:
            self.stop_autoplay()
            self.status.set("Autoplay stopped: no legal moves remain.")
            return
        self.make_move(*random.choice(moves))
        self.autoplay_job = self.root.after(650, self.autoplay_step)

    def stop_autoplay(self):
        if self.autoplay_job:
            self.root.after_cancel(self.autoplay_job)
            self.autoplay_job = None
        if hasattr(self, "autoplay_button"):
            self.autoplay_button.configure(text="Autoplay")

    def draw_board(self):
        self.canvas.delete("all")
        self.canvas.update_idletasks()
        width = max(self.canvas.winfo_width(), 500)
        height = max(self.canvas.winfo_height(), 500)
        size = self.board_size.get()
        cell = min((width - 80) / size, (height - 80) / size, 78)
        total = cell * size
        offset_x = (width - total) / 2
        offset_y = (height - total) / 2
        self.cell_bounds = {}

        for (row, col), has_peg in self.board.items():
            x1, y1 = offset_x + col * cell, offset_y + row * cell
            x2, y2 = x1 + cell, y1 + cell
            self.cell_bounds[(row, col)] = (x1, y1, x2, y2)
            self.canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, fill=self.BOARD,
                                         outline="#b68e3e", width=1)
            center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
            radius = cell * 0.29
            self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                                    fill=self.HOLE, outline="#8e6b35", width=2)
            if has_peg:
                peg_fill = self.GOLD if (row, col) == self.selected else self.BLUE
                self.canvas.create_oval(center_x - radius * .72, center_y - radius * .72,
                                        center_x + radius * .72, center_y + radius * .72,
                                        fill=peg_fill, outline="#163d6b", width=2)
                self.canvas.create_oval(center_x - radius * .42, center_y - radius * .52,
                                        center_x + radius * .1, center_y - radius * .04,
                                        fill="#ffffff", outline="", stipple="gray50")

        pegs = sum(self.board.values())
        self.moves_var.set(str(self.move_count))
        self.pegs_var.set(str(pegs))
        current_best = int(self.best_var.get()) if self.best_var.get().isdigit() else pegs
        self.best_var.set(str(min(current_best, pegs)))


def main():
    root = tk.Tk()
    SolitaireGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
