
import unittest
from move_validator import MoveValidator


class TestMoveValidator(unittest.TestCase):

    def setUp(self):
        self.board = {
            (0, 0): True,
            (0, 1): True,
            (0, 2): False,
            (1, 0): True,
            (1, 1): True,
            (1, 2): True,
            (2, 0): False,
            (2, 1): True,
            (2, 2): False,
        }

    def test_valid_horizontal_move(self):
        self.assertTrue(
            MoveValidator.is_valid_move(self.board, (0, 0), (0, 2))
        )

    def test_valid_vertical_move(self):
        self.assertTrue(
            MoveValidator.is_valid_move(self.board, (0, 0), (2, 0))
        )

    def test_valid_diagonal_move(self):
        self.assertTrue(
            MoveValidator.is_valid_move(self.board, (0, 0), (2, 2))
        )

    def test_invalid_move_when_destination_has_peg(self):
        self.assertFalse(
            MoveValidator.is_valid_move(self.board, (2, 1), (0, 1))
        )

    def test_invalid_move_distance(self):
        self.assertFalse(
            MoveValidator.is_valid_move(self.board, (0, 0), (1, 1))
        )


if __name__ == "__main__":
    unittest.main()
