
from move_validator import MoveValidator


class SolitaireGame:
    """Keep all mutable game state and move validation out of the GUI."""

    SUPPORTED_SIZES = (5, 7, 9)
    SUPPORTED_TYPES = ("English", "Hexagon", "Diamond")
    JUMP_OFFSETS = (
        (-2, 0), (2, 0), (0, -2), (0, 2),
        (-2, -2), (-2, 2), (2, -2), (2, 2),
    )

    def __init__(self, size=7, board_type="English"):
        self.size = 7
        self.board_type = "English"
        self.board = {}
        self.move_count = 0
        self.new_game(size=size, board_type=board_type)

    @classmethod
    def validate_size(cls, value):
        """Return a supported integer size or raise ValueError."""
        try:
            if isinstance(value, bool):
                raise ValueError
            if isinstance(value, float) and not value.is_integer():
                raise ValueError
            size = int(str(value).strip())
        except (TypeError, ValueError):
            raise ValueError("Board size must be 5, 7, or 9.") from None
        if size not in cls.SUPPORTED_SIZES:
            raise ValueError("Board size must be 5, 7, or 9.")
        return size

    @classmethod
    def validate_type(cls, value):
        if value not in cls.SUPPORTED_TYPES:
            raise ValueError("Board type must be English, Hexagon, or Diamond.")
        return value

    @staticmethod
    def board_positions(size, board_type):
        """Return playable row/column pairs for the selected board layout."""
        center = size // 2
        positions = set()
        for row in range(size):
            for col in range(size):
                if board_type == "English":
                    arm = center - 1
                    valid = (arm <= row <= size - arm - 1 or
                             arm <= col <= size - arm - 1)
                elif board_type == "Hexagon":
                    q, r = col - center, row - center
                    valid = max(abs(q), abs(r), abs(-q-r)) <= center
                else:  # Diamond
                    valid = abs(row-center) + abs(col-center) <= center
                if valid:
                    positions.add((row, col))
        return positions

    def new_game(self, size=None, board_type=None):
        """Validate first so invalid input never overwrites valid settings."""
        validated_size = self.validate_size(self.size if size is None else size)
        validated_type = self.validate_type(
            self.board_type if board_type is None else board_type
        )
        positions = self.board_positions(validated_size, validated_type)
        center = (validated_size // 2, validated_size // 2)
        new_board = {p: p != center for p in positions}
        self.size = validated_size
        self.board_type = validated_type
        self.board = new_board
        self.move_count = 0
        return self.board

    def is_valid_move(self, start, end):
        if self.is_game_over():
            return False
        return MoveValidator.is_valid_move(self.board, start, end)

    def legal_moves(self):
        """Find possible moves directly; avoids circular game-over checks."""
        result = []
        for (row, col), occupied in self.board.items():
            if not occupied:
                continue
            for dr, dc in self.JUMP_OFFSETS:
                end = (row + dr, col + dc)
                if MoveValidator.is_valid_move(self.board, (row, col), end):
                    result.append(((row, col), end))
        return result

    def make_move(self, start, end):
        """Apply a legal jump; invalid moves never change board or count."""
        if not self.is_valid_move(start, end):
            return False
        middle = MoveValidator.get_middle_position(start, end)
        self.board[start] = False
        self.board[middle] = False
        self.board[end] = True
        self.move_count += 1
        return True

    def remaining_pegs(self):
        return sum(self.board.values())

    def is_game_over(self):
        return self.remaining_pegs() <= 1 or not self.legal_moves()

    def final_rating(self):
        """Return an end-of-game rating, otherwise None."""
        if not self.is_game_over():
            return None
        n = self.remaining_pegs()
        if n == 1:
            return "Outstanding"
        if n == 2:
            return "Very Good"
        if n == 3:
            return "Good"
        return "Average"
