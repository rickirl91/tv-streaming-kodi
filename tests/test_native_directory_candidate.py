import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "nextepisode"))
from native_directory_candidate import directory_successor


class NativeDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.current = dict(series_id="1622", show="Supernatural", title="Dead in the Water",
                            season=1, episode=3, imdb="tt0713613")
        self.rows = [
            dict(title=title, showtitle="Supernatural", season=1, episode=i,
                 file=f"plugin://plugin.video.themoviedb.helper/?info=play&tmdb_type=tv&tmdb_id=1622&season=1&episode={i}",
                 firstaired="", premiered="2005-09-27",
                 uniqueid={"tvshow.tmdb":"1622", "tvshow.imdb":"tt0460681", "imdb":imdb})
            for i, (title, imdb) in enumerate([
                ("Pilot","tt0713618"), ("Wendigo","tt0713624"),
                ("Dead in the Water","tt0713613"), ("Phantom Traveler","tt0713617")], 1)]
        self.limits = dict(start=0, end=4, total=4)

    def target(self):
        return directory_successor(lambda method, params: dict(files=self.rows, limits=self.limits), self.current)

    def test_premiered_fallback(self):
        self.assertEqual(self.target()["title"], "Phantom Traveler")

    def test_wrong_parent(self):
        self.rows[3]["uniqueid"]["tvshow.tmdb"] = "999"
        self.assertIsNone(self.target())

    def test_wrong_current_imdb(self):
        self.current["imdb"] = "tt999"
        self.assertIsNone(self.target())

    def test_missing_or_future_date(self):
        for value in ("", "2099-01-01"):
            self.rows[3]["premiered"] = value
            self.assertIsNone(self.target())

    def test_partial_directory(self):
        self.limits["total"] = 22
        self.assertIsNone(self.target())

    def test_missing_limits(self):
        self.limits = {}
        self.assertIsNone(self.target())

    def test_group_and_boundary(self):
        self.current["group"] = "alternate"
        self.assertIsNone(self.target())
        self.current.update(group=None, episode=4, title="Phantom Traveler", imdb="tt0713617")
        self.assertIsNone(self.target())
