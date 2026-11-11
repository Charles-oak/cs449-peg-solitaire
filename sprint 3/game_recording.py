"""Text-file recordings of Peg Solitaire board snapshots (JSON text)."""

import json
from pathlib import Path

from solitaire_game import AutomatedGame, SolitaireGame


class GameRecorder:
    """Store complete board states; no Tkinter or gameplay rules are here."""

    FORMAT_VERSION = 1

    def __init__(self):
        self.frames = []

    def capture(self, game, label="Move"):
        """Copy an immutable-in-practice snapshot of the current game state."""
        frame = {
            "size": game.size,
            "board_type": game.board_type,
            "mode": "automated" if isinstance(game, AutomatedGame) else "manual",
            "move_count": game.move_count,
            "board": [[row, col, int(occupied)]
                      for (row, col), occupied in sorted(game.board.items())],
            "label": str(label),
        }
        self.frames.append(frame)
        return frame

    def save(self, path):
        if not self.frames:
            raise ValueError("There is no recording to save.")
        destination = Path(path)
        destination.write_text(
            json.dumps({"version": self.FORMAT_VERSION,
                        "frames": self.frames}, indent=2),
            encoding="utf-8",
        )
        return destination

    @classmethod
    def load(cls, path):
        """Load and validate a recording, rejecting malformed files."""
        try:
            content = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("The recording cannot be read.") from exc
        if (not isinstance(content, dict) or
                content.get("version") != cls.FORMAT_VERSION or
                not isinstance(content.get("frames"), list) or
                not content["frames"]):
            raise ValueError("Invalid recording format.")

        frames = content["frames"]
        try:
            first = frames[0]
            game_size = SolitaireGame.validate_size(first["size"])
            board_type = SolitaireGame.validate_type(first["board_type"])
            mode = first["mode"]
            if mode not in ("manual", "automated"):
                raise ValueError("Invalid game mode.")
            expected_positions = SolitaireGame.board_positions(game_size, board_type)
            prev_count = -1
            for frame in frames:
                if (frame["size"] != game_size or
                        frame["board_type"] != board_type or
                        frame["mode"] != mode or
                        not isinstance(frame["label"], str) or
                        type(frame["move_count"]) is not int or
                        frame["move_count"] < prev_count):
                    raise ValueError("Inconsistent recording frame.")
                prev_count = frame["move_count"]
                board = frame["board"]
                if not isinstance(board, list) or len(board) != len(expected_positions):
                    raise ValueError("Board size does not match recording.")
                if not all(isinstance(entry, list) and len(entry) == 3 and
                           all(type(n) is int for n in entry) and
                           entry[2] in (0, 1) for entry in board):
                    raise ValueError("Invalid board values.")
                if {(row, col) for row, col, _ in board} != expected_positions:
                    raise ValueError("Invalid board positions.")
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid recording data.") from exc
        return frames

    @staticmethod
    def restore_frame(game, frame):
        """Apply a loaded snapshot to a temporary game for GUI playback."""
        game.new_game(size=frame["size"], board_type=frame["board_type"])
        game.board = {(row, col): bool(value)
                      for row, col, value in frame["board"]}
        game.move_count = frame["move_count"]
