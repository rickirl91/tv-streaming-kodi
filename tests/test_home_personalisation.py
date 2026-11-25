import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'src'
spec = importlib.util.spec_from_file_location('core', ROOT / 'homepersonalisation' / 'core.py')
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




class HiddenGemsTests(unittest.TestCase):
    def test_locates_hub_and_renames_only_exact_label(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hub = root / 'skinvariables-shortcut-1101widgets.json'
            home = root / core.TARGET_NAME
            home.write_text(json.dumps([{'label': 'Continue Watching'}]))
            widget = {
                'label': core.HIDDEN_GEMS_OLD,
                'path': 'plugin://plugin.video.streamrow/?mode=wrap&source=opaque&reload=1',
                'filters': {'rating': 8, 'sort': 'vote_count.asc'},
                'art': {'thumb': 'icon'},
            }
            near = dict(widget, label=core.HIDDEN_GEMS_OLD + ' Picks')
            rows = [near, {'label': 'Catalogue', 'widgets': [widget]}]
            raw = json.dumps(rows).encode() + b'\r\n'
            hub.write_bytes(raw)
            self.assertEqual(core.hidden_gems_snapshot(root), (hub, raw))
            plan = core.plan_hidden_gems(rows)
            self.assertEqual(plan, [near, {'label': 'Catalogue', 'widgets': [
                dict(widget, label='Hidden Gems')]}])
            self.assertEqual(core.plan_hidden_gems(plan), plan)
            options = dict(filename=hub.name)
            with self.assertRaises(ValueError):
                core.apply_home(hub, root / 'backup', core.sha256(raw), 'Other',
                                planner=core.plan_hidden_gems, **options)
            folder = core.apply_home(hub, root / 'backup', core.sha256(raw),
                                     planner=core.plan_hidden_gems, **options)
            self.assertIsNone(core.hidden_gems_snapshot(root))
            self.assertEqual((folder / hub.name).read_bytes(), raw)
            applied = hub.read_bytes()
            hub.write_bytes(applied + b' ')
            with self.assertRaises(RuntimeError):
                core.restore_home(hub, folder, **options)
            hub.write_bytes(applied)
            self.assertEqual(core.restore_home(hub, folder, **options), 'restored')
            self.assertEqual(hub.read_bytes(), raw)
            self.assertEqual(json.loads(home.read_bytes()), [{'label': 'Continue Watching'}])

    def test_ambiguous_hub_or_unexpected_source_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = dict(label=core.HIDDEN_GEMS_OLD, path='plugin://other/')
            with self.assertRaises(ValueError):
                core.plan_hidden_gems([row])
            row['path'] = 'plugin://plugin.video.streamrow/?mode=wrap'
            for name in ('home', '1102'):
                (root / f'skinvariables-shortcut-{name}widgets.json').write_text(json.dumps([row]))
            with self.assertRaisesRegex(ValueError, 'multiple hub files'):
                core.hidden_gems_snapshot(root)

if __name__ == '__main__':
    unittest.main(verbosity=2)
