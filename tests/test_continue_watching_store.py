import tempfile
import unittest
from pathlib import Path
from continue_watching_store import DismissalStore

class StoreTests(unittest.TestCase):
    def test_persistence_and_isolation(self):
        with tempfile.TemporaryDirectory() as root:
            a = Path(root) / 'Cricky'
            b = Path(root) / 'Ricky'
            DismissalStore(a).hide('movie:12', 'Movie')
            self.assertIn('movie:12', DismissalStore(a).read())
            self.assertEqual(DismissalStore(b).read(), {})
            DismissalStore(a).viewed('movie:12')
            self.assertIn('movie:12', DismissalStore(a).read())
            DismissalStore(a).viewed('movie:12', verified=True)
            self.assertEqual(DismissalStore(a).read(), {})

    def test_invalid_key_and_repeat(self):
        with tempfile.TemporaryDirectory() as root:
            store = DismissalStore(root)
            with self.assertRaises(ValueError):
                store.hide('tv:0', 'Invalid')
            store.hide('tv:12', 'Show')
            store.hide('tv:12', 'Show')
            self.assertEqual(store.read(), {'tv:12': {'label': 'Show'}})
