import subprocess
import sys
import unittest
from pathlib import Path

class ActivityTests(unittest.TestCase):
    def test_activity(self):
        source = Path(__file__).resolve().parents[1] / 'release-candidates' / 'homepersonalisation-0.1.13'
        subprocess.run([sys.executable, '-c', """
from tempfile import TemporaryDirectory
from continue_watching_store import DismissalStore
from continue_watching_playback import Viewing
from continue_watching_feed import fetch_visible
from unittest.mock import patch
with TemporaryDirectory() as p:
    store = DismissalStore(p)
    store.hide('tv:12', 'Test')
    v = Viewing()
    for i in range(11):
        v.sample(p,'tv:12','file',i,i,1,store)
    assert 'tv:12' not in store.read()
    assert store.activity()['tv:12'] == 1
    store.record_viewing('movie:13')
    store = DismissalStore(p)
    rows = [{'key': k} for k in ('tv:12','tv:14','movie:13','tv:15')]
    with patch('continue_watching_feed.dismissal_key', side_effect=lambda r:r['key']):
        assert [r['key'] for r in fetch_visible(lambda *a: {'files':rows},store)] == ['movie:13','tv:12','tv:14','tv:15']
"""], cwd=source, check=True)
