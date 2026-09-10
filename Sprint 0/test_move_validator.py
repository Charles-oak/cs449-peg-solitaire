import importlib.util
import unittest
from pathlib import Path


MOVE_VALIDATOR_PATH = Path(r"C:\Desktop\move_validator.py")
spec = importlib.util.spec_from_file_location("external_move_validator", MOVE_VALIDATOR_PATH)
move_validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(move_validator)
MoveValidator = move_validator.MoveValidator


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
