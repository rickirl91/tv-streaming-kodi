import subprocess
import sys
import unittest
from pathlib import Path

class DurableQueueTests(unittest.TestCase):
    def test_durable_queue_and_identity(self):
        source = Path(__file__).resolve().parents[1] / 'release-candidates' / 'homepersonalisation-0.1.14'
        subprocess.run([sys.executable, '-c', """
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
import sys
sys.modules['xbmcgui'] = Mock()
from continue_watching_store import DismissalStore
from continue_watching_monitor import Capture, resolve
from continue_watching_playback import Viewing
from continue_watching_feed import fetch_visible
with TemporaryDirectory() as p:
    store = DismissalStore(p)
    store.hide('tv:12', 'Test')
    report = dict(key=None, media='episode', tmdb='12', show='Test', season=1, episode=2)
    viewing = Viewing()
    for i in range(11):
        viewing.sample(p,'unverified:12:Test','file',i,i,1,Capture(store,report))
    assert 'tv:12' in store.read()
    assert not store.activity()
    store = DismissalStore(p)
    [(ident, saved)] = store.pending()
    assert saved == report
    assert store.path.with_name('cw-stage.txt').read_text() == 'Viewing queued'
    rpc = Mock(return_value={'files':[{'key':'tv:12','showtitle':'Test'}]})
    with patch('continue_watching_monitor.dismissal_key', side_effect=lambda row:row['key']):
        assert resolve(saved,rpc) == 'tv:12'
        assert resolve(dict(saved,show='Different'),rpc) is None
    assert store.commit_pending(ident,'tv:12')
    assert not store.commit_pending(ident,'tv:12')
    assert 'tv:12' not in store.read()
    assert store.activity()['tv:12'] == 1
    assert not store.pending()
    store.queue(dict(report,key='tv:12'))
    [(ident, saved)] = store.pending()
    store.hide('tv:12','Manual dismissal')
    assert not store.commit_pending(ident,'tv:12')
    assert 'tv:12' in store.read()
    store.queue(dict(report,key='tv:12'))
    [(ident, saved)] = store.pending()
    assert store.commit_pending(ident,resolve(saved,Mock(side_effect=AssertionError)))
    store.record_viewing('movie:13')
    rows = [{'key': k} for k in ('tv:12','tv:14','movie:13')]
    with patch('continue_watching_feed.dismissal_key',side_effect=lambda row:row['key']):
        assert [r['key'] for r in fetch_visible(lambda *a: {'files':rows},store)] == ['movie:13','tv:12','tv:14']
"""], cwd=source, check=True)
