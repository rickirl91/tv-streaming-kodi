import sys
import unittest
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "nextepisode"))
from resolver import resolve_next

class ResolverTests(unittest.TestCase):
    def test_cases(self):
        a = dict(season=1, episode=7, episode_id="a", air_date="2020-01-01")
        b = dict(season=1, episode=8, episode_id="b", air_date="2020-01-01")
        c = dict(season=2, episode=1, episode_id="c", air_date="2020-01-01")
        cat = dict(series_id="show", complete=True, episodes=[c,b,a])
        now = date(2026,11,25)
        def current(row):
            return dict(row, series_id="show")
        self.assertEqual(resolve_next(current(a),cat,now),b)
        self.assertEqual(resolve_next(current(b),cat,now),c)
        self.assertIsNone(resolve_next(current(c),cat,now))
        self.assertIsNone(resolve_next(dict(current(a),series_id="wrong"),cat,now))
        self.assertIsNone(resolve_next(current(a),dict(cat,complete=False),now))
        self.assertIsNone(resolve_next(current(a),dict(cat,episodes=[a,b,b]),now))
        self.assertIsNone(resolve_next(current(a),dict(cat,episodes=[a,dict(b,air_date="2099-01-01")]),now))
        self.assertIsNone(resolve_next(current(a),dict(cat,episodes=[a,dict(b,air_date="")]),now))

if __name__ == "__main__":
    unittest.main()
