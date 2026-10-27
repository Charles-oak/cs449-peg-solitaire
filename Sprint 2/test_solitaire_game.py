
import unittest
from solitaire_game import SolitaireGame


class TestConfiguration(unittest.TestCase):
    def test_supported_sizes(self):
        for size in (5, 7, 9):
            with self.subTest(size=size):
                game = SolitaireGame(size)
                self.assertEqual(game.size, size)

    def test_invalid_size_preserves_selected_configuration(self):
        """Candidate LLM test 1; verify exception AND unchanged state."""
        game = SolitaireGame(size=7, board_type="English")
        old_board = game.board.copy()
        with self.assertRaises(ValueError):
            game.new_game(size=8, board_type="Diamond")
        self.assertEqual(game.size, 7)
        self.assertEqual(game.board_type, "English")
        self.assertEqual(game.board, old_board)

    def test_invalid_size_text_and_bool(self):
        game = SolitaireGame()
        for invalid in ("abc", "", True, 10, "3.5"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    game.new_game(size=invalid)
                self.assertEqual(game.size, 7)

    def test_select_each_board_type(self):
        game = SolitaireGame()
        for board_type in SolitaireGame.SUPPORTED_TYPES:
            with self.subTest(board_type=board_type):
                game.new_game(board_type=board_type)
                self.assertEqual(game.board_type, board_type)
                self.assertIn((3, 3), game.board)

    def test_change_type_only_new_type_kept(self):
        game = SolitaireGame(board_type="English")
        game.new_game(board_type="Diamond")
        self.assertEqual(game.board_type, "Diamond")
        self.assertEqual(set(game.board),
                         SolitaireGame.board_positions(7, "Diamond"))

    def test_invalid_board_type_preserves_prior(self):
        game = SolitaireGame()
        old = game.board.copy()
        with self.assertRaises(ValueError):
            game.new_game(board_type="Triangle")
        self.assertEqual(game.board_type, "English")
        self.assertEqual(game.board, old)


class TestInitialization(unittest.TestCase):
    def test_center_empty_and_other_cells_filled(self):
        for board_type in SolitaireGame.SUPPORTED_TYPES:
            game = SolitaireGame(7, board_type)
            with self.subTest(board_type=board_type):
                self.assertFalse(game.board[(3, 3)])
                self.assertTrue(all(peg for pos, peg in game.board.items()
                                    if pos != (3, 3)))
                self.assertEqual(game.remaining_pegs(), len(game.board)-1)

    def test_new_game_matches_size_and_type(self):
        game = SolitaireGame()
        game.new_game(size=9, board_type="Hexagon")
        self.assertEqual(set(game.board),
                         SolitaireGame.board_positions(9, "Hexagon"))
        self.assertFalse(game.board[(4, 4)])

    def test_restart_resets_moves_and_board(self):
        game = SolitaireGame()
        self.assertTrue(game.make_move((3, 1), (3, 3)))
        self.assertEqual(game.move_count, 1)
        game.new_game()
        self.assertEqual(game.move_count, 0)
        self.assertEqual(game.remaining_pegs(), 32)
        self.assertFalse(game.board[(3, 3)])


class TestMove(unittest.TestCase):
    def setUp(self):
        self.game = SolitaireGame()

    def test_vertical_jump_updates_three_cells_and_count(self):
        """Candidate LLM test 2; checks all affected cells and count."""
        self.assertTrue(self.game.make_move((1, 3), (3, 3)))
        self.assertFalse(self.game.board[(1, 3)])
        self.assertFalse(self.game.board[(2, 3)])
        self.assertTrue(self.game.board[(3, 3)])
        self.assertEqual(self.game.remaining_pegs(), 31)
        self.assertEqual(self.game.move_count, 1)

    def test_horizontal_jump(self):
        self.assertTrue(self.game.make_move((3, 1), (3, 3)))
        self.assertFalse(self.game.board[(3, 1)])
        self.assertFalse(self.game.board[(3, 2)])
        self.assertTrue(self.game.board[(3, 3)])

    def test_diagonal_jump(self):
        # (1,1) is not playable in an English cross: use legal board cells.
        # Create a reachable board-state pattern with the destination empty.
        self.game.board[(3, 5)] = False
        self.assertTrue(self.game.make_move((1, 3), (3, 5)))
        self.assertFalse(self.game.board[(1, 3)])
        self.assertFalse(self.game.board[(2, 4)])
        self.assertTrue(self.game.board[(3, 5)])

    def test_reject_occupied_destination(self):
        before = self.game.board.copy()
        self.assertFalse(self.game.make_move((1, 3), (1, 5)))
        self.assertEqual(self.game.board, before)
        self.assertEqual(self.game.move_count, 0)

    def test_reject_empty_start(self):
        before = self.game.board.copy()
        self.assertFalse(self.game.make_move((3, 3), (1, 3)))
        self.assertEqual(self.game.board, before)

    def test_reject_empty_middle(self):
        # First jump creates a gap at (2,3); the next proposed jump
        # attempts to jump over that empty cell.
        self.game.make_move((1, 3), (3, 3))
        before = self.game.board.copy()
        self.assertFalse(self.game.make_move((3, 3), (1, 3)))
        self.assertEqual(self.game.board, before)

    def test_reject_wrong_distance(self):
        before = self.game.board.copy()
        self.assertFalse(self.game.make_move((2, 3), (3, 3)))
        self.assertEqual(self.game.board, before)

    def test_reject_outside_board(self):
        before = self.game.board.copy()
        self.assertFalse(self.game.make_move((2, 3), (0, 5)))
        self.assertEqual(self.game.board, before)


class TestEndOfGame(unittest.TestCase):
    def test_game_continues_with_legal_moves(self):
        game = SolitaireGame()
        self.assertFalse(game.is_game_over())
        self.assertIsNone(game.final_rating())
        self.assertTrue(game.legal_moves())

    def test_one_peg_outstanding(self):
        game = SolitaireGame()
        game.board = {(3, 3): True, (3, 4): False}
        self.assertTrue(game.is_game_over())
        self.assertEqual(game.final_rating(), "Outstanding")

    def test_no_moves_two_pegs_very_good(self):
        game = SolitaireGame()
        game.board = {(0, 0): True, (6, 6): True}
        self.assertTrue(game.is_game_over())
        self.assertEqual(game.final_rating(), "Very Good")

    def test_no_moves_three_pegs_good(self):
        game = SolitaireGame()
        game.board = {(0, 0): True, (0, 5): True, (5, 0): True}
        self.assertTrue(game.is_game_over())
        self.assertEqual(game.final_rating(), "Good")

    def test_no_moves_four_pegs_average(self):
        game = SolitaireGame()
        game.board = {(0, 0): True, (0, 5): True,
                      (5, 0): True, (5, 5): True}
        self.assertTrue(game.is_game_over())
        self.assertEqual(game.final_rating(), "Average")

    def test_no_move_after_game_ends(self):
        game = SolitaireGame()
        game.board = {(0, 0): True, (0, 1): False}
        snapshot = game.board.copy()
        self.assertFalse(game.make_move((0, 0), (0, 1)))
        self.assertEqual(game.board, snapshot)


if __name__ == "__main__":
    unittest.main()
