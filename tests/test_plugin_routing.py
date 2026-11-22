import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).parent / 'plugin.video.tvstreaming.homepersonalisation'
for name in ('xbmc', 'xbmcaddon', 'xbmcgui', 'xbmcplugin', 'xbmcvfs'):
    sys.modules[name] = types.ModuleType(name)

xbmc = sys.modules['xbmc']
xbmc.LOGINFO, xbmc.LOGERROR = 1, 4
xbmc.log = lambda *a: None
xbmc.getInfoLabel = lambda _: 'Cricky'
xbmc.getSkinDir = lambda: 'skin.arctic.fuse.3'
xbmc.getCondVisibility = lambda _: True
xbmc.executebuiltin = lambda _: None

xbmcaddon = sys.modules['xbmcaddon']
xbmcaddon.Addon = lambda *a: object()

class FakeItem:
    def __init__(self, **kwargs):
        self.label = kwargs.get('label')
        self.path = kwargs.get('path')
        self.props = {}
        self.art = {}
    def setArt(self, a): self.art = a
    def setInfo(self, *args): pass
    def setProperty(self, k, v): self.props[k] = v
    def getVideoInfoTag(self): return self
    def setUniqueIDs(self, ids): self.ids = ids

class FakeDialog:
    def ok(self, *args): pass

xbmcgui = sys.modules['xbmcgui']
xbmcgui.ListItem = FakeItem
xbmcgui.Dialog = FakeDialog

xbmcplugin = sys.modules['xbmcplugin']
xbmcplugin.added = []
xbmcplugin.addDirectoryItem = lambda handle, path, item, isFolder: xbmcplugin.added.append((path, item, isFolder))
xbmcplugin.setContent = lambda *a: None
xbmcplugin.endOfDirectory = lambda *a, **kw: None
sys.modules['xbmcvfs'].translatePath = lambda x: '/fake'

sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location('personalplugin', ROOT / 'default.py')
plugin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plugin)


def provider_reply(path):
    from urllib.parse import parse_qs, urlparse
    q = parse_qs(urlparse(path).query)
    typ = q['tmdb_type'][0]
    page = int(q.get('page', ['1'])[0])
    if typ == 'tv' and page > 1:
        raise AssertionError('tv pagination exhausted and should not restart')
    record = {'label': 'Title {} {}'.format(typ, page),
              'file': 'plugin://plugin.video.themoviedb.helper/?info=details&tmdb_type={}&tmdb_id={}'.format(typ, 100 if typ == 'movie' else 200),
              'thumbnail': 'poster.png', 'art': {'fanart': 'fanart.jpg'},
              'filetype': 'directory', 'uniqueid': {'tmdb': '100'}}
    records = [record]
    if typ == 'movie' and page == 1:
        records.append({'label': 'Next Page', 'file': path + '&page=2'})
    return {'jsonrpc': '2.0', 'result': {'files': records}, 'id': 1}

xbmc.executeJSONRPC = lambda raw: json.dumps(provider_reply(json.loads(raw)['params']['directory']))

class RouterTests(unittest.TestCase):
    def setUp(self): xbmcplugin.added.clear()

    def test_first_page_mixed_and_preserved_callback(self):
        plugin.handle_feed(42, {'kind': ['watchlist'], 'mode': ['widget']})
        self.assertEqual(len(xbmcplugin.added), 4)
        self.assertTrue(xbmcplugin.added[0][1].label.startswith('See All'))
        self.assertIn('tmdb_type=movie', xbmcplugin.added[1][0])
        self.assertIn('tmdb_type=tv', xbmcplugin.added[2][0])
        self.assertEqual(xbmcplugin.added[2][1].props['tmdb_type'], 'tv')
        next_page = xbmcplugin.added[-1][0]
        self.assertIn('t=END', next_page)
        self.assertIn('m=', next_page)

    def test_second_page_does_not_requery_exhausted_tv(self):
        plugin.handle_feed(42, {'kind': ['watchlist'], 'mode': ['widget']})
        next_page = xbmcplugin.added[-1][0]
        from urllib.parse import parse_qs, urlparse
        xbmcplugin.added.clear()
        plugin.handle_feed(42, parse_qs(urlparse(next_page).query))
        self.assertEqual(len(xbmcplugin.added), 1)
        self.assertIn('tmdb_type=movie', xbmcplugin.added[0][0])

if __name__ == '__main__': unittest.main(verbosity=2)
