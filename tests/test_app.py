import importlib.util
import os
import random
import unittest
from datetime import date, timedelta

APP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"
)


def load_app():
    spec = importlib.util.spec_from_file_location("linesmaker_app", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LinesmakerTest(unittest.TestCase):
    def setUp(self):
        self.mod = load_app()
        self.client = self.mod.app.test_client()

    def test_parts_counts(self):
        self.assertGreaterEqual(len(self.mod.OPENINGS), 10)
        self.assertGreaterEqual(len(self.mod.BODIES), 10)
        self.assertGreaterEqual(len(self.mod.ENDINGS), 10)

    def test_build_line_with_indices(self):
        line = self.mod.build_line(0, 0, 0)
        expected = (
            self.mod.OPENINGS[0] + self.mod.BODIES[0] + self.mod.ENDINGS[0]
        )
        self.assertEqual(line, expected)

    def test_build_line_clamps_out_of_range(self):
        line = self.mod.build_line(999, -5, 999)
        expected = (
            self.mod.OPENINGS[-1] + self.mod.BODIES[0] + self.mod.ENDINGS[-1]
        )
        self.assertEqual(line, expected)

    def test_random_line_reproducible_with_seed(self):
        line1 = self.mod.random_line(random.Random(42))
        line2 = self.mod.random_line(random.Random(42))
        self.assertEqual(line1, line2)

    def test_random_indices_in_range(self):
        for seed in range(20):
            o, b, e = self.mod.random_indices(random.Random(seed))
            self.assertTrue(0 <= o < len(self.mod.OPENINGS))
            self.assertTrue(0 <= b < len(self.mod.BODIES))
            self.assertTrue(0 <= e < len(self.mod.ENDINGS))

    def test_todays_line_deterministic(self):
        d = date(2026, 10, 31)
        self.assertEqual(self.mod.todays_line(d), self.mod.todays_line(d))

    def test_todays_line_varies_by_date(self):
        base = date(2026, 1, 1)
        lines = {self.mod.todays_line(base + timedelta(days=i)) for i in range(30)}
        self.assertGreater(len(lines), 1)

    def test_index_page_200(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("セリフメーカー", resp.get_data(as_text=True))

    def test_index_page_with_selection(self):
        resp = self.client.get("/?o=1&b=2&e=3")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn(self.mod.build_line(1, 2, 3), html)

    def test_index_page_random(self):
        resp = self.client.get("/?random=1")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("今日のセリフ", html)

    def test_healthz(self):
        resp = self.client.get("/healthz")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
