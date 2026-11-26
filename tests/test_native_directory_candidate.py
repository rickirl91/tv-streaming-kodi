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

        self.summaries = [dict(season=1, episode=4, uniqueid={"tvshow.tmdb":"1622"})]
        self.following = []

    def rpc(self, method, params):
        url = params["directory"]
        if "info=seasons" in url:
            rows = self.summaries
        elif "season=2" in url:
            rows = self.following
        else:
            return dict(files=self.rows, limits=self.limits)
        return dict(files=rows, limits=dict(start=0,end=len(rows),total=len(rows)))

    def target(self):
        return directory_successor(self.rpc, self.current)

    def test_transition(self):
        self.current.update(episode=4, title="Phantom Traveler", imdb="tt0713617")
        self.summaries.append(dict(season=2, episode=1, uniqueid={"tvshow.tmdb":"1622"}))
        self.following = [dict(self.rows[0], season=2, title="Next season",
                               file=self.rows[0]["file"].replace("season=1","season=2"))]
        self.assertEqual((self.target()["season"], self.target()["episode"]), (2,1))
        self.following.clear()
        self.assertIsNone(self.target())

    def test_declared_count_mismatch(self):
        self.summaries[0]["episode"] = 22
        self.assertIsNone(self.target())

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

    def test_unrelated_invalid_summary(self):
        self.summaries.extend([dict(season=0, episode=-1), dict(season=-1),
                               dict(season=3, episode=None)])
        self.assertEqual(self.target()["episode"], 4)

    def test_duplicate_current_summary(self):
        self.summaries.append(dict(self.summaries[0]))
        self.assertIsNone(self.target())

    def test_invalid_following_summary(self):
        self.current.update(episode=4, title="Phantom Traveler", imdb="tt0713617")
        self.summaries.append(dict(season=2, episode=-1))
        self.assertIsNone(self.target())
