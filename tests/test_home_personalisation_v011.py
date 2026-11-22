import copy
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

SOURCE = Path('/mnt/data/cricky_v011/plugin.video.tvstreaming.homepersonalisation')
spec = importlib.util.spec_from_file_location('cricky_core_v011', SOURCE / 'core.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


def home():
    rows = [
        {'label': 'Continue Watching', 'path': 'plugin://progress/', 'unique': 'keep', 'art': {'a': 1}},
        *[{'label': label, 'path': core.widget_path(kind), 'target': 'videos', 'id': 'personal-'+kind}
          for kind, label, _ in core.LABELS],
        {'label': 'Up Next Episodes', 'path': 'plugin://nextup/', 'unique': 'keepnext'},
        {'label': 'Your TV Show Watchlist', 'path': 'plugin://old/?type=tv'},
        {'label': 'Trending Movies', 'path': 'plugin://trending/', 'art': {'some': 'art'}},
        {'label': 'Your Movie Watchlist', 'path': 'plugin://old/?type=movie'},
        {'label': 'Recently Released', 'path': 'plugin://releases/'},
        {'label': 'Recommended Movies for You', 'path': 'plugin://old/?rec=movie'},
        {'label': 'Recommended Shows for You', 'path': 'plugin://old/?rec=tv'},
        {'label': 'Your Movie Watchlist — curated picks', 'path': 'plugin://custom/', 'keep': True},
        {'label': 'Netflix Movies', 'path': 'plugin://netflix/', 'keep': True},
    ]
    return rows


class CrickyV011Tests(unittest.TestCase):
    def test_four_overlap_removed_and_everything_else_same(self):
        before = home()
        planned = core.plan_cleanup(before)
        self.assertEqual(len(before)-len(planned), 4)
        removed = {r['label'] for _,r in core.cleanup_candidates(before)}
        self.assertEqual(removed, {'Your TV Show Watchlist','Your Movie Watchlist',
                                   'Recommended Movies for You','Recommended Shows for You'})
        self.assertEqual(planned, [row for row in before if row['label'] not in removed])
        self.assertIs(planned[0], before[0])
        self.assertIs(planned[4], before[4])
        self.assertEqual(planned[-1]['label'], 'Netflix Movies')
        self.assertEqual(planned[4]['label'], 'Up Next Episodes')

    def test_cleanup_is_idempotent(self):
        initial = home()
        self.assertEqual(core.plan_cleanup(core.plan_cleanup(initial)), core.plan_cleanup(initial))
        self.assertEqual(core.cleanup_candidates(core.plan_cleanup(initial)), [])

    def test_unrelated_similar_label_preserved(self):
        planned = core.plan_cleanup(home())
        self.assertTrue(any(r['label'].endswith('curated picks') for r in planned))

    def test_requires_new_personalisation_first(self):
        bad = home()
        bad[2]['label'] = 'Some Other Category'
        with self.assertRaisesRegex(ValueError, 'first four'):
            core.plan_cleanup(bad)

    def test_requires_exact_widget_sources(self):
        bad = home()
        bad[1]['path'] = 'plugin://some.other.addon/'
        with self.assertRaisesRegex(ValueError, 'source differs'):
            core.plan_cleanup(bad)

    def test_backup_apply_restore_and_protect_later_changes(self):
        before = home()
        raw = (json.dumps(before, separators=(',',':'))+'\r\n').encode('utf-8')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/core.TARGET_NAME
            backups = Path(folder)/'backups'
            path.write_bytes(raw)
            manifest_folder=core.apply_home(path, backups, core.sha256(raw), planner=core.plan_cleanup)
            self.assertIsNotNone(manifest_folder)
            self.assertEqual((manifest_folder/core.TARGET_NAME).read_bytes(), raw)
            after=path.read_bytes()
            self.assertEqual(core.load_home(after), core.plan_cleanup(before))
            self.assertNotEqual(raw, after)
            self.assertEqual(core.restore_home(path, manifest_folder), 'restored')
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(core.restore_home(path, manifest_folder), 'already-restored')
            path.write_bytes(after + b'\n')
            with self.assertRaisesRegex(RuntimeError, 'newer manual changes'):
                core.restore_home(path, manifest_folder)

    def test_reject_changed_between_preview_and_apply(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/core.TARGET_NAME
            p.write_bytes(core.serialize_home(home()))
            original_hash=core.sha256(p.read_bytes())
            p.write_bytes(p.read_bytes()+b' ')
            with self.assertRaisesRegex(RuntimeError, 'changed after preview'):
                core.apply_home(p, Path(folder)/'backup', original_hash, planner=core.plan_cleanup)

    def test_other_profile_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/core.TARGET_NAME
            p.write_bytes(core.serialize_home(home()))
            with self.assertRaisesRegex(ValueError, 'Cricky'):
                core.apply_home(p, Path(folder)/'backup', core.sha256(p.read_bytes()), profile='Master', planner=core.plan_cleanup)

    def test_artwork_uses_streamrow_neutral_not_first_title_poster(self):
        source=(SOURCE/'default.py').read_text()
        self.assertIn('see_all_miami_neutral_v024.png',source)
        self.assertIn("picture = {'poster': artwork, 'thumb': artwork, 'icon': artwork}", source)
        self.assertNotIn("picture = {'poster': poster, 'thumb': poster, 'fanart': fanart}", source)
        self.assertIn("picture['fanart'] = fanart",source)

    def test_addon_version_and_syntax(self):
        self.assertIn('version="0.1.1"', (SOURCE/'addon.xml').read_text())
        for name in ('core.py','default.py'):
            compile((SOURCE/name).read_text(),name,'exec')

if __name__=='__main__': unittest.main(verbosity=2)
