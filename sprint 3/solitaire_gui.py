
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from game_recording import GameRecorder
from solitaire_game import AutomatedGame, ManualGame, SolitaireGame

BACKGROUND = "#f4f7fb"
BLUE = "#2f80ed"
NAVY = "#173b62"
BOARD = "#e9c46a"
HOLE = "#b48a4d"


class SolitaireGUI:
    """Present game configuration, board, recording, and replay controls."""

    def __init__(self, root):
        self.root = root
        self.root.title("Peg Solitaire | CS 449 Sprint 3")
        self.root.geometry("1060x800")
        self.root.minsize(930, 710)
        self.root.configure(bg=BACKGROUND)

        self.game = ManualGame()
        self.board_type = tk.StringVar(value="English")
        self.board_size = tk.StringVar(value="7")
        self.game_mode = tk.StringVar(value="manual")
        self.record_game = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Select a peg to begin.")
        self.moves_var = tk.StringVar(value="0")
        self.pegs_var = tk.StringVar(value="32")
        self.best_var = tk.StringVar(value="32")
        self.selected = None
        self.hint_destination = None
        self.cell_bounds = {}
        self.recorder = GameRecorder()
        self.autoplay_job = None
        self.replay_job = None
        self.replay_frames = []
        self.replay_index = 0

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
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"),
                        padding=(12, 4))
        style.configure("Primary.TButton", background=BLUE, foreground="white",
                        font=("Segoe UI", 10, "bold"), padding=(12, 4))

    def _build_layout(self):
        header = tk.Frame(self.root, bg=BLUE, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        ttk.Label(header, text="PEG SOLITAIRE", style="Title.TLabel").pack(
            anchor="w", padx=42, pady=18)

        content = tk.Frame(self.root, bg=BACKGROUND)
        content.pack(fill="both", expand=True, padx=28, pady=16)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        controls = ttk.Frame(content, style="Card.TFrame", padding=16)
        controls.grid(row=0, column=0, sticky="nsw", padx=(0, 18))
        ttk.Label(controls, text="Game setup", style="Section.TLabel").pack(anchor="w")
        ttk.Label(controls, text="Board type", style="Info.TLabel").pack(
            anchor="w", pady=(9, 3))
        for name in SolitaireGame.SUPPORTED_TYPES:
            ttk.Radiobutton(controls, text=name, value=name,
                            variable=self.board_type).pack(anchor="w", pady=1)

        ttk.Label(controls, text="Board size", style="Info.TLabel").pack(
            anchor="w", pady=(10, 3))
        self.size_box = ttk.Combobox(controls, textvariable=self.board_size,
                                      values=SolitaireGame.SUPPORTED_SIZES, width=9)
        self.size_box.pack(anchor="w")
        self.size_box.bind("<Return>", lambda _event: self.new_game())

        ttk.Label(controls, text="Game mode", style="Info.TLabel").pack(
            anchor="w", pady=(10, 3))
        for label, value in (("Manual", "manual"), ("Automated", "automated")):
            ttk.Radiobutton(controls, text=label, value=value,
                            variable=self.game_mode).pack(anchor="w", pady=1)

        ttk.Checkbutton(controls, text="Record game", variable=self.record_game,
                        command=self.toggle_recording).pack(anchor="w", pady=(9, 1))
        ttk.Separator(controls, orient="horizontal").pack(fill="x", pady=10)
        ttk.Button(controls, text="New game", style="Primary.TButton",
                   command=self.new_game).pack(fill="x", pady=2)
        self.hint_button = ttk.Button(controls, text="Hint (manual)",
                                      style="Action.TButton", command=self.hint_move)
        self.hint_button.pack(fill="x", pady=2)
        self.randomize_button = ttk.Button(controls, text="Randomize",
                                            style="Action.TButton", command=self.randomize)
        self.randomize_button.pack(fill="x", pady=2)
        self.autoplay_button = ttk.Button(controls, text="Autoplay",
                                          style="Action.TButton", command=self.toggle_autoplay)
        self.autoplay_button.pack(fill="x", pady=2)
        ttk.Button(controls, text="Save recording (.txt)", style="Action.TButton",
                   command=self.save_recording).pack(fill="x", pady=2)
        ttk.Button(controls, text="Replay from file", style="Action.TButton",
                   command=self.replay_from_file).pack(fill="x", pady=2)
        ttk.Button(controls, text="Tutorial", style="Action.TButton",
                   command=self.show_tutorial).pack(fill="x", pady=2)

        board_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        board_card.grid(row=0, column=1, sticky="nsew")
        board_card.grid_rowconfigure(1, weight=1)
        board_card.grid_columnconfigure(0, weight=1)
        board_card.grid_columnconfigure(1, minsize=205)
        top = tk.Frame(board_card, bg="white")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(top, text="Game board", style="Section.TLabel").pack(side="left")
        self.board_caption = ttk.Label(top, text="English / Manual",
                                       style="Info.TLabel")
        self.board_caption.pack(side="right")

        self.canvas = tk.Canvas(board_card, bg="white", highlightthickness=0,
                                cursor="hand2")
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self.on_board_click)
        self.canvas.bind("<Configure>", lambda _event: self.draw_board())

        panel = ttk.Frame(board_card, style="Card.TFrame", padding=(14, 12))
        panel.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        ttk.Label(panel, text="Game status", style="Section.TLabel").pack(anchor="w")
        ttk.Label(panel, text="LIVE STATISTICS", style="MetricName.TLabel").pack(
            anchor="w", pady=(14, 4))
        metrics = tk.Frame(panel, bg="white")
        metrics.pack(fill="x")
        for value, label in ((self.moves_var, "MOVES"),
                             (self.pegs_var, "PEGS"), (self.best_var, "BEST")):
            box = tk.Frame(metrics, bg="white")
            box.pack(side="left", expand=True, fill="x")
            ttk.Label(box, textvariable=value, style="Metric.TLabel").pack()
            ttk.Label(box, text=label, style="MetricName.TLabel").pack()
        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=16)
        ttk.Label(panel, text="Move history", style="Section.TLabel").pack(anchor="w")
        self.history = tk.Listbox(panel, height=10, bg="#f8fafc", fg="#40546b",
                                  font=("Segoe UI", 9), relief="flat",
                                  highlightthickness=1,
                                  highlightbackground="#d7e0eb")
        self.history.pack(fill="both", expand=True, pady=(8, 0))
        self._refresh_history()

        tk.Label(self.root, textvariable=self.status, bg=BACKGROUND,
                 fg="#4b6078", font=("Segoe UI", 10)).pack(
            anchor="w", padx=42, pady=(0, 12))
        self._update_mode_controls()

    def _update_mode_controls(self):
        automated = isinstance(self.game, AutomatedGame)
        self.autoplay_button.configure(state="normal" if automated else "disabled")
        self.randomize_button.configure(state="disabled" if automated else "normal")
        self.hint_button.configure(state="disabled" if automated else "normal")

    def _stop_timers(self):
        for field in ("autoplay_job", "replay_job"):
            job = getattr(self, field)
            if job is not None:
                self.root.after_cancel(job)
                setattr(self, field, None)
        if hasattr(self, "autoplay_button"):
            self.autoplay_button.configure(text="Autoplay")

    def _refresh_history(self):
        self.history.delete(0, tk.END)
        if not self.recorder.frames:
            self.history.insert(tk.END, "Enable Record game to track moves.")
        else:
            for i, frame in enumerate(self.recorder.frames):
                self.history.insert(tk.END,
                    f"{i:02}: {frame['label']} / {frame['move_count']} moves")
            self.history.see(tk.END)

    def _record(self, label):
        if self.record_game.get():
            self.recorder.capture(self.game, label)
            self._refresh_history()

    def toggle_recording(self):
        if self.record_game.get():
            self.recorder = GameRecorder()
            self._record("Recording started")
            self.status.set("Recording on. Save to a text file when finished.")
        else:
            self.status.set("Recording paused. Save recording to export the trace.")
        self._refresh_history()

    def new_game(self):
        """Start fresh while keeping Sprint 1 invalid-input safety."""
        try:
            size = SolitaireGame.validate_size(self.board_size.get())
            board_type = SolitaireGame.validate_type(self.board_type.get())
            requested_mode = self.game_mode.get()
            if requested_mode not in ("manual", "automated"):
                raise ValueError("Select Manual or Automated mode.")
        except ValueError as exc:
            self.board_size.set(str(self.game.size))
            self.board_type.set(self.game.board_type)
            self.game_mode.set("automated" if isinstance(self.game, AutomatedGame)
                               else "manual")
            self.status.set(f"Invalid configuration: {exc}")
            messagebox.showerror("Invalid configuration", str(exc), parent=self.root)
            return False
        self._stop_timers()
        self.game = (AutomatedGame if requested_mode == "automated" else ManualGame)(
            size, board_type)
        self.selected = None
        self.hint_destination = None
        self.best_var.set(str(self.game.remaining_pegs()))
        self.recorder = GameRecorder()
        self._record("New game")
        self._refresh_history()
        self._update_mode_controls()
        self.status.set(f"New {board_type} {requested_mode} game / size {size}.")
        self.draw_board()
        return True

    def _end_message(self):
        if self.game.is_game_over():
            self.status.set(f"GAME OVER: {self.game.final_rating()} "
                            f"({self.game.remaining_pegs()} pegs left).")
        else:
            self.status.set(f"{self.game.remaining_pegs()} pegs remain. "
                            f"Moves: {self.game.move_count}.")

    def hint_move(self):
        if not isinstance(self.game, ManualGame) or self.game.is_game_over():
            self._end_message()
            return
        start, end = self.game.legal_moves()[0]
        self.selected = start
        self.hint_destination = end
        self.status.set(f"Hint: click highlighted hole ({end[0]+1}, {end[1]+1}).")
        self.draw_board()

    def on_board_click(self, event):
        if not isinstance(self.game, ManualGame) or self.replay_job is not None:
            return
        position = next((point for point, rect in self.cell_bounds.items()
                         if rect[0] <= event.x <= rect[2] and
                         rect[1] <= event.y <= rect[3]), None)
        if position is None:
            return
        if self.game.is_game_over():
            self._end_message()
        elif self.selected is None:
            if self.game.board[position]:
                self.selected = position
                self.status.set("Peg selected. Choose the empty destination.")
            else:
                self.status.set("Select a peg first.")
        elif position == self.selected:
            self.selected = None
            self.hint_destination = None
            self.status.set("Selection cleared.")
        elif self.game.make_move(self.selected, position):
            self._record(f"Manual {self.selected} -> {position}")
            self.selected = None
            self.hint_destination = None
            self._end_message()
        elif self.game.board[position]:
            self.selected = position
            self.hint_destination = None
            self.status.set("Different peg selected.")
        else:
            self.status.set("Invalid jump. Board unchanged.")
        self.draw_board()

    def randomize(self):
        if not isinstance(self.game, ManualGame):
            return
        self._stop_timers()
        moved = []
        for _ in range(3):
            move = self.game.randomize_state(steps=1)
            if not move:
                break
            moved.extend(move)
            self._record(f"Random jump {move[0][0]} -> {move[0][1]}")
        self.selected = None
        self.hint_destination = None
        self._end_message()
        if moved and not self.game.is_game_over():
            self.status.set(f"Randomized with {len(moved)} legal jumps; "
                            f"{self.game.remaining_pegs()} pegs left.")
        self.draw_board()

    def toggle_autoplay(self):
        if not isinstance(self.game, AutomatedGame):
            return
        if self.autoplay_job is not None:
            self._stop_timers()
            self.status.set("Autoplay paused.")
            return
        if self.game.is_game_over():
            self._end_message()
            return
        self.autoplay_button.configure(text="Pause autoplay")
        self.status.set("Automated mode is playing legal random moves.")
        self._autoplay_step()

    def _autoplay_step(self):
        self.autoplay_job = None
        move = self.game.autoplay_step()
        if move is not None:
            self._record(f"Auto {move[0]} -> {move[1]}")
        self.draw_board()
        if self.game.is_game_over():
            self.autoplay_button.configure(text="Autoplay")
            self._end_message()
        else:
            self.autoplay_job = self.root.after(120, self._autoplay_step)

    def save_recording(self):
        if not self.recorder.frames:
            messagebox.showinfo("No recording", "Enable Record game first.",
                                parent=self.root)
            return
        path = filedialog.asksaveasfilename(
            parent=self.root, title="Save recording", defaultextension=".txt",
            filetypes=[("Text recordings", "*.txt"), ("All files", "*.*")],
            initialfile="peg_solitaire_record.txt")
        if path:
            try:
                self.recorder.save(path)
            except (ValueError, OSError) as exc:
                messagebox.showerror("Save failed", str(exc), parent=self.root)
            else:
                self.status.set(f"Recording saved: {path}")

    def replay_from_file(self):
        path = filedialog.askopenfilename(
            parent=self.root, title="Open recording",
            filetypes=[("Text recordings", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        try:
            frames = GameRecorder.load(path)
        except ValueError as exc:
            messagebox.showerror("Invalid recording", str(exc), parent=self.root)
            return
        self._stop_timers()
        self.replay_frames = frames
        self.replay_index = 0
        self.game = (AutomatedGame if frames[0]["mode"] == "automated"
                     else ManualGame)(frames[0]["size"], frames[0]["board_type"])
        self.game_mode.set(frames[0]["mode"])
        self.board_type.set(frames[0]["board_type"])
        self.board_size.set(str(frames[0]["size"]))
        self.selected = None
        self.hint_destination = None
        self._update_mode_controls()
        self._replay_step()

    def _replay_step(self):
        self.replay_job = None
        if self.replay_index >= len(self.replay_frames):
            self.status.set("Replay complete. Last recorded state shown.")
            return
        frame = self.replay_frames[self.replay_index]
        GameRecorder.restore_frame(self.game, frame)
        self.replay_index += 1
        self.draw_board()
        self.status.set(f"Replay {self.replay_index}/{len(self.replay_frames)}: "
                        f"{frame['label']}")
        if self.replay_index < len(self.replay_frames):
            self.replay_job = self.root.after(180, self._replay_step)
        else:
            self.status.set(f"Replay complete: {len(self.replay_frames)} states.")

    def show_tutorial(self):
        messagebox.showinfo(
            "Peg Solitaire Tutorial",
            "Manual: click a peg and an empty destination two cells away.\n"
            "Hint selects a legal starting peg; click the outlined target.\n"
            "Randomize advances the manual board using random legal jumps.\n"
            "Automated: select Automated, click New game, then Autoplay.\n"
            "Record game: enable, play, Save recording, then Replay from file.",
            parent=self.root)

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
            x1, y1 = offset_x + col*cell, offset_y + row*cell
            x2, y2 = x1 + cell, y1 + cell
            self.cell_bounds[(row, col)] = (x1, y1, x2, y2)
            self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2,
                                         fill=BOARD, outline="#b68e3e", width=1)
            cx, cy = (x1+x2)/2, (y1+y2)/2
            radius = cell*.29
            self.canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius,
                                    fill=HOLE, outline="#8e6b35", width=2)
            if occupied:
                color = "#f4b942" if (row, col) == self.selected else BLUE
                self.canvas.create_oval(cx-radius*.72, cy-radius*.72,
                                        cx+radius*.72, cy+radius*.72,
                                        fill=color, outline="#163d6b", width=2)
                self.canvas.create_oval(cx-radius*.42, cy-radius*.52,
                                        cx+radius*.10, cy-radius*.04,
                                        fill="white", outline="", stipple="gray50")
            if (row, col) == self.hint_destination:
                self.canvas.create_oval(cx-radius*.72, cy-radius*.72,
                                        cx+radius*.72, cy+radius*.72,
                                        outline="#159947", width=4)
        self.moves_var.set(str(self.game.move_count))
        self.pegs_var.set(str(self.game.remaining_pegs()))
        self.board_caption.configure(text=f"{self.game.board_type} / {self.game_mode.get().title()} "
                                          f"/ size {size}")
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
