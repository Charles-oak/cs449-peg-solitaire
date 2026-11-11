
import random
import unittest

from solitaire_game import AutomatedGame, ManualGame, SolitaireGame


class TestGameModes(unittest.TestCase):
    def test_manual_and_automated_share_base_class(self):
        self.assertTrue(issubclass(ManualGame, SolitaireGame))
        self.assertTrue(issubclass(AutomatedGame, SolitaireGame))

    def test_manual_move_updates_state(self):
        game = ManualGame()
        self.assertTrue(game.make_move((1, 3), (3, 3)))
        self.assertEqual(game.move_count, 1)
        self.assertEqual(game.remaining_pegs(), 31)

    def test_manual_ending_one_peg(self):
        game = ManualGame()
        game.board = {(3, 3): True, (3, 4): False}
        self.assertTrue(game.is_game_over())
        self.assertEqual(game.final_rating(), "Outstanding")

    def test_invalid_size_preserves_game_state(self):
        game = ManualGame(7, "English")
        game.make_move((1, 3), (3, 3))
        before = (game.size, game.board_type, game.board.copy(), game.move_count)
        with self.assertRaises(ValueError):
            game.new_game(size="8", board_type="Diamond")
        self.assertEqual(
            (game.size, game.board_type, game.board, game.move_count), before)


class TestManualRandomization(unittest.TestCase):
    def test_randomize_changes_board_only_by_valid_jumps(self):
        game = ManualGame(5, "English")
        before = game.remaining_pegs()
        performed = game.randomize_state(steps=3, rng=random.Random(1))
        self.assertGreater(len(performed), 0)
        self.assertLessEqual(len(performed), 3)
        self.assertEqual(game.remaining_pegs(), before - len(performed))
        self.assertEqual(game.move_count, len(performed))

    def test_randomize_periodically_until_game_over(self):
        game = ManualGame(5, "English")
        chooser = random.Random(7)
        while not game.is_game_over():
            result = game.randomize_state(steps=2, rng=chooser)
            self.assertTrue(result)
        self.assertIsNotNone(game.final_rating())
        self.assertFalse(game.legal_moves())

    def test_randomize_rejects_invalid_steps_without_state_change(self):
        game = ManualGame()
        board = game.board.copy()
        for steps in (0, -1, True, 0.5):
            with self.subTest(steps=steps):
                with self.assertRaises(ValueError):
                    game.randomize_state(steps=steps)
        self.assertEqual(game.board, board)

    def test_randomize_after_game_over_does_nothing(self):
        game = ManualGame()
        game.board = {(3, 3): True, (3, 4): False}
        self.assertEqual(game.randomize_state(), [])
        self.assertEqual(game.move_count, 0)


class TestAutomatedMode(unittest.TestCase):
    def test_automatic_step_is_legal_and_updates_pegs(self):
        game = AutomatedGame()
        old_pegs = game.remaining_pegs()
        start, end = game.autoplay_step(random.Random(2))
        self.assertFalse(game.board[start])
        self.assertTrue(game.board[end])
        self.assertEqual(game.remaining_pegs(), old_pegs - 1)
        self.assertEqual(game.move_count, 1)

    def test_autoplay_reaches_terminal_state_english(self):
        game = AutomatedGame(5, "English")
        steps = game.play_until_end(random.Random(5))
        self.assertTrue(game.is_game_over())
        self.assertEqual(game.move_count, len(steps))
        self.assertEqual(game.remaining_pegs(), len(game.board) - 1 - len(steps))
        self.assertIn(game.final_rating(),
                      ("Outstanding", "Very Good", "Good", "Average"))

    def test_autoplay_reaches_terminal_state_hexagon(self):
        game = AutomatedGame(5, "Hexagon")
        game.play_until_end(random.Random(17))
        self.assertTrue(game.is_game_over())
        self.assertFalse(game.legal_moves())

    def test_autoplay_cannot_move_after_terminal_state(self):
        game = AutomatedGame()
        game.board = {(3, 3): True, (3, 4): False}
        self.assertIsNone(game.autoplay_step())
        self.assertEqual(game.move_count, 0)

    def test_restart_resets_automatic_game(self):
        game = AutomatedGame(7, "Diamond")
        game.autoplay_step()
        game.new_game(size=9, board_type="Hexagon")
        self.assertEqual(game.size, 9)
        self.assertEqual(game.board_type, "Hexagon")
        self.assertEqual(game.move_count, 0)
        self.assertFalse(game.board[(4, 4)])
