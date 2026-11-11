
import json
import random
import tempfile
import unittest
from pathlib import Path

from game_recording import GameRecorder
from solitaire_game import AutomatedGame, ManualGame


class TestGameRecording(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "record.txt"

    def test_manual_record_file_and_replay_all_snapshots(self):
        game = ManualGame(7, "English")
        recording = GameRecorder()
        recording.capture(game, "Start")
        game.make_move((1, 3), (3, 3))
        recording.capture(game, "Manual move")
        recording.save(self.path)
        self.assertTrue(self.path.read_text(encoding="utf-8").startswith("{"))
        frames = GameRecorder.load(self.path)
        self.assertEqual(len(frames), 2)
        replay = ManualGame()
        GameRecorder.restore_frame(replay, frames[1])
        self.assertEqual(replay.board, game.board)
        self.assertEqual(replay.move_count, game.move_count)
        self.assertEqual(replay.remaining_pegs(), 31)

    def test_randomized_states_record_and_replay(self):
        game = ManualGame(5, "Hexagon")
        rec = GameRecorder()
        rec.capture(game, "Start")
        for step in game.randomize_state(steps=2, rng=random.Random(1)):
            # Capture of a batch happens afterward in this example.
            self.assertIsInstance(step, tuple)
        rec.capture(game, "Randomized")
        rec.save(self.path)
        frames = GameRecorder.load(self.path)
        replay = ManualGame()
        GameRecorder.restore_frame(replay, frames[-1])
        self.assertEqual(replay.board, game.board)
        self.assertEqual(replay.move_count, game.move_count)

    def test_automated_recording_replays_final_state(self):
        game = AutomatedGame(5, "English")
        rec = GameRecorder()
        rec.capture(game, "Start")
        for start, end in game.play_until_end(random.Random(5)):
            self.assertIsInstance(start, tuple)
            self.assertIsInstance(end, tuple)
        rec.capture(game, "Finish")
        rec.save(self.path)
        frames = GameRecorder.load(self.path)
        self.assertEqual(frames[0]["mode"], "automated")
        replay = AutomatedGame()
        GameRecorder.restore_frame(replay, frames[-1])
        self.assertEqual(replay.final_rating(), game.final_rating())
        self.assertEqual(replay.remaining_pegs(), game.remaining_pegs())

    def test_empty_recording_is_not_saved(self):
        with self.assertRaises(ValueError):
            GameRecorder().save(self.path)

    def test_invalid_json_recording_rejected(self):
        self.path.write_text("not json at all", encoding="utf-8")
        with self.assertRaises(ValueError):
            GameRecorder.load(self.path)

    def test_invalid_board_positions_rejected(self):
        rec = GameRecorder()
        rec.capture(ManualGame(), "Start")
        rec.save(self.path)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        data["frames"][0]["board"].pop()
        self.path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValueError):
            GameRecorder.load(self.path)

    def test_invalid_mode_rejected(self):
        rec = GameRecorder()
        rec.capture(ManualGame(), "Start")
        rec.save(self.path)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        data["frames"][0]["mode"] = "unknown"
        self.path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValueError):
            GameRecorder.load(self.path)
