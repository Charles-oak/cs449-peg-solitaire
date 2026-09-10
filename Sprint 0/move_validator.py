class MoveValidator:
    """Checks whether a move in Peg Solitaire is valid."""

    @staticmethod
    def get_middle_position(start, end):
        """Return the position jumped over, or None for invalid geometry."""
        start_row, start_col = start
        end_row, end_col = end

        row_difference = abs(end_row - start_row)
        col_difference = abs(end_col - start_col)

        valid_move = (
            (row_difference == 2 and col_difference == 0)
            or (row_difference == 0 and col_difference == 2)
            or (row_difference == 2 and col_difference == 2)
        )

        if not valid_move:
            return None

        middle_row = (start_row + end_row) // 2
        middle_col = (start_col + end_col) // 2

        return middle_row, middle_col

    @classmethod
    def is_valid_move(cls, board, start, end):
        """Check the geometry and board state of a move."""
        middle = cls.get_middle_position(start, end)

        if middle is None:
            return False

        if start not in board or middle not in board or end not in board:
            return False

        start_has_peg = board[start]
        middle_has_peg = board[middle]
        destination_is_empty = not board[end]

        return start_has_peg and middle_has_peg and destination_is_empty
