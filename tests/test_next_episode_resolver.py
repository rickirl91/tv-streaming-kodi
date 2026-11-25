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

from controller import Controller

class ControllerTests(unittest.TestCase):
    def test_timing_and_natural_end(self):
        c = Controller()
        c.begin("next")
        self.assertIsNone(c.tick(1600,1800,1))
        self.assertIsNone(c.tick(1680,1800,0))
        self.assertEqual(c.tick(1680,1800,1),"offer")
        self.assertIsNone(c.tick(1700,1800,1))
        self.assertEqual(c.finish(True),"next")
        self.assertIsNone(c.finish(True))

    def test_cancel_and_stop(self):
        for cancel in (True,False):
            c = Controller()
            c.begin("next")
            self.assertEqual(c.tick(550,600,1),"offer")
            if cancel:
                c.cancel()
            self.assertIsNone(c.finish(cancel))

    def test_confirmation(self):
        c = Controller()
        for i in range(3):
            c.begin("next",continuation=i>0)
            self.assertEqual(c.tick(550,600,1),"still_watching" if i==2 else "offer")
            if i<2:
                self.assertEqual(c.finish(True),"next")
        self.assertIsNone(c.finish(True))
        self.assertEqual(c.advance(confirmed=True),"next")

from catalogue import normalize

class CatalogueTests(unittest.TestCase):
    def test_identity(self):
        row = dict(file="plugin://plugin.video.themoviedb.helper/?info=details&tmdb_type=tv&tmdb_id=123&season=1&episode=7", season=1, episode=7, firstaired="2020-01-01")
        cat = normalize("123", [row])
        self.assertEqual(cat["episodes"][0]["episode_id"], "123:1:7")
        self.assertFalse(cat["complete"])
        self.assertIsNone(normalize("456", [row]))
        self.assertIsNone(normalize("123", [dict(row, episode=8)]))
        self.assertIsNone(normalize("123", [dict(row, file="https://example.com")]))
        self.assertIsNone(normalize("123", []))

if __name__ == "__main__":
    unittest.main()
