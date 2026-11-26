import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "nextepisode"))
from catalogue import directory_successor

class DirectoryTests(unittest.TestCase):
    def setUp(self):
        self.current = dict(series_id="1622", parent_verified=True, group="", show="Supernatural", title="Dead in the Water", season=1, episode=3)
        self.rows = [dict(file="plugin://plugin.video.themoviedb.helper/?info=details&tmdb_type=tv&tmdb_id=1622&season=1&episode="+str(n), season=1, episode=n, showtitle="Supernatural", title=t, firstaired="2005-09-20") for n,t in enumerate(["Pilot","Wendigo","Dead in the Water","Phantom Traveler"],1)]
    def resolve(self):
        return directory_successor(lambda method, params: dict(files=self.rows, limits=dict(total=len(self.rows))), self.current)
    def test_successor(self):
        self.assertEqual(self.resolve()["episode"],4)
    def test_gap(self):
        del self.rows[1]
        self.assertIsNone(self.resolve())
    def test_wrong_show(self):
        self.rows[3]["showtitle"]="Other"
        self.assertIsNone(self.resolve())
    def test_wrong_current_title(self):
        self.current["title"]="Other"
        self.assertIsNone(self.resolve())
    def test_future(self):
        self.rows[3]["firstaired"]="2999-01-01"
        self.assertIsNone(self.resolve())
    def test_missing_date(self):
        self.rows[3]["firstaired"]=None
        self.assertIsNone(self.resolve())
    def test_boundary(self):
        self.rows.pop()
        self.assertIsNone(self.resolve())
    def test_unverified_parent(self):
        self.current["parent_verified"]=False
        self.assertIsNone(self.resolve())
    def test_group(self):
        self.current["group"]="alternate"
        self.assertIsNone(self.resolve())
    def test_partial(self):
        self.assertIsNone(directory_successor(lambda m,p: dict(files=self.rows, limits=dict(total=22)),self.current))
    def test_duplicate(self):
        self.rows.append(self.rows[-1])
        self.assertIsNone(self.resolve())
