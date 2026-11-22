import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location('core', ROOT / 'plugin.video.tvstreaming.homepersonalisation' / 'core.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


class HomeTests(unittest.TestCase):
    def setUp(self):
        self.original = [
            {'label': 'Trending Movies', 'path': 'plugin://A', 'id': 4, 'widget_style': 'posters'},
            {'label': '[B]Continue Watching[/B]', 'path': 'plugin://historic', 'target': 'videos', 'id': 10},
            {'label': 'Netflix Movies', 'path': 'plugin://B', 'other': {'foo': 1}},
            {'label': 'Because You Watched', 'path': 'plugin://oldversion'},
            {'label': 'Disney+ Series', 'path': 'plugin://C', 'some': ['thing']},
        ]

    def test_exact_order_and_unchanged_existing(self):
        actual = core.plan_home(self.original)
        self.assertEqual([x['label'] for x in actual[:4]],
                         ['[B]Continue Watching[/B]', 'Recommended For You',
                          'Because You Watched', 'From Your Watchlist'])
        self.assertEqual([x['label'] for x in actual[4:]],
                         ['Trending Movies', 'Netflix Movies', 'Disney+ Series'])
        self.assertIs(actual[0], self.original[1])
        self.assertIs(actual[4], self.original[0])
        self.assertIs(actual[5], self.original[2])
        self.assertIs(actual[6], self.original[4])
        self.assertEqual(self.original[3]['path'], 'plugin://oldversion')

    def test_idempotent(self):
        once = core.plan_home(self.original)
        self.assertEqual(core.plan_home(once), once)

    def test_refuses_ambiguous_current_state(self):
        for bad in [[], [{'label': 'Other'}],
                    [{'label': 'Continue Watching'}, {'label': 'Continue Watching'}]]:
            with self.assertRaises(ValueError):
                core.plan_home(bad)

    def test_sources_require_correct_types_and_endpoint(self):
        for kind in core.INFO_BY_KIND:
            for med in ('movie', 'tv'):
                source = core.source_url(kind, med)
                self.assertTrue(core.valid_source(source, kind, med))
                self.assertFalse(core.valid_source(source, kind, 'notmedia'))
        self.assertFalse(core.valid_source('https://example.com/?info=sync_watchlist&tmdb_type=tv', 'watchlist', 'tv'))

    def test_backup_restores_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / core.TARGET_NAME
            original_bytes = json.dumps(self.original, indent=2).encode('utf-8') + b'\r\n'
            home.write_bytes(original_bytes)
            folder = core.apply_home(home, Path(tmp)/'backups', core.sha256(original_bytes), 'Cricky')
            self.assertIsNotNone(folder)
            self.assertEqual((folder / core.TARGET_NAME).read_bytes(), original_bytes)
            self.assertEqual(core.latest_backup(Path(tmp)/'backups'), folder)
            self.assertEqual(core.restore_home(home, folder, 'Cricky'), 'restored')
            self.assertEqual(home.read_bytes(), original_bytes)
            self.assertEqual(core.restore_home(home, folder, 'Cricky'), 'already-restored')

    def test_detects_changed_preview_and_conflicting_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / core.TARGET_NAME
            home.write_text(json.dumps(self.original), encoding='utf-8')
            wrong_hash = core.sha256(b'changed')
            with self.assertRaises(RuntimeError):
                core.apply_home(home, Path(tmp)/'backups', wrong_hash)
            folder = core.apply_home(home, Path(tmp)/'backups', core.sha256(home.read_bytes()))
            home.write_text(home.read_text(encoding='utf-8') + ' ', encoding='utf-8')
            with self.assertRaises(RuntimeError):
                core.restore_home(home, folder)
            self.assertTrue(home.read_text(encoding='utf-8').endswith(' '))

    def test_other_profiles_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / core.TARGET_NAME
            home.write_text(json.dumps(self.original), encoding='utf-8')
            with self.assertRaises(ValueError):
                core.apply_home(home, Path(tmp)/'backups', core.sha256(home.read_bytes()), profile='Ricky')


if __name__ == '__main__':
    unittest.main(verbosity=2)
