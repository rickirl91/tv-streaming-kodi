#!/usr/bin/env python3
"""Patch exact previous RC ZIPs, preserving all unrelated files and assets."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from xml.etree import ElementTree as ET
import hashlib
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'release-candidates' / 'widget-performance-001'
CACHE = (SRC / 'widget_cache.py').read_bytes()
def replace_once(s, a, b):
    assert s.count(a) == 1, a
    return s.replace(a, b, 1)
def adapt(addon, text):
    text = replace_once(text, 'import xbmcplugin\n', 'import xbmcplugin\nimport widget_cache\n')
    if addon == 'plugin.video.streamrow':
        text = replace_once(text, 'import widget_cache\n', 'import widget_cache\nimport xbmcvfs\n')
        text = replace_once(text, 'def get_items(category=None, source=None):',
            '''def get_items(category=None, source=None):
    uri = source or (category_directory(category) + "&widget=true&reload=")
    root = xbmcvfs.translatePath('special://profile/')
    def active():
        return (xbmc.getInfoLabel('System.ProfileName').strip().casefold() == 'cricky'
                and xbmcvfs.translatePath('special://profile/') == root)
    # Only ordinary public catalogue rows. User lists and other modes remain live.
    info = parse_qs(urlparse(uri).query).get('info', [''])[0]
    if info not in ('discover', 'trending_week', 'trending_day', 'now_playing',
                    'popular', 'top_rated', 'upcoming', 'airing_today', 'on_the_air'):
        return _get_items_live(category, source)
    return widget_cache.cached(root, uri, lambda: _get_items_live(category, source),
                               active, lambda msg: xbmc.log(msg, xbmc.LOGINFO))

def _get_items_live(category=None, source=None):''')
    else:
        text = replace_once(text, 'def fetch_kind(kind, paths=None):',
            '''def cached_tmdb_directory(uri):
    root = translated('special://profile/')
    def active():
        return (current_profile().casefold() == 'cricky'
                and translated('special://profile/') == root)
    return widget_cache.cached(root, uri, lambda: tmdb_directory(uri),
                               active, lambda msg: xbmc.log(msg, xbmc.LOGINFO))

def fetch_kind(kind, paths=None, use_cache=False):''')
        text = replace_once(text, 'split_source(tmdb_directory(source), kind, media)',
            'split_source((cached_tmdb_directory if use_cache else tmdb_directory)(source), kind, media)')
        text = replace_once(text, 'rows, nexts = fetch_kind(kind, paths)',
            "rows, nexts = fetch_kind(kind, paths, use_cache=(mode == 'widget' and not paths))")
    return text

def build(addon, old, new):
    previous = ROOT / (addon + '-' + old + '-RC.zip')
    name = addon + '-' + new + '-RC.zip'
    with ZipFile(previous) as z:
        assert z.testzip() is None
        files = {n: z.read(n) for n in z.namelist() if not n.endswith('/')}
    assert all(n.startswith(addon+'/') and '..' not in n.split('/') for n in files)
    original = dict(files)
    default, manifest, cache = [addon+'/'+n for n in ('default.py','addon.xml','widget_cache.py')]
    assert cache not in files
    files[default] = adapt(addon, files[default].decode('utf-8')).encode('utf-8')
    m = files[manifest].decode('utf-8')
    assert ET.fromstring(m).get('version') == old
    files[manifest] = replace_once(m, 'version="'+old+'"', 'version="'+new+'"').encode('utf-8')
    files[cache] = CACHE
    assert ET.fromstring(files[manifest]).get('version') == new
    assert not any(e.get('point') == 'xbmc.service' for e in ET.fromstring(files[manifest]).findall('extension'))
    assert all(files[n] == data for n,data in original.items() if n not in (default,manifest))
    for n,data in files.items():
        if n.endswith('.py'):
            compile(data,n,'exec')
    with ZipFile(ROOT/name,'w') as z:
        for n,data in sorted(files.items()):
            i = ZipInfo(n,(2026,11,28,0,0,0))
            i.external_attr = 0o100644 << 16
            z.writestr(i,data,compress_type=ZIP_DEFLATED,compresslevel=9)
    with ZipFile(ROOT/name) as z:
        assert z.testzip() is None and set(z.namelist()) == set(files)
        assert all(z.read(n)==data for n,data in files.items())
    digest = hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    print('PASS',name,digest)
    return name,digest

if __name__ == '__main__':
    results = [build('plugin.video.streamrow','0.3.2','0.3.3'),
               build('plugin.video.tvstreaming.homepersonalisation','0.1.17','0.1.18')]
    checksum = ROOT/'SHA256SUMS.txt'
    names = {n for n,d in results}
    lines = [l for l in checksum.read_text().splitlines() if l.rsplit('  ',1)[-1] not in names]
    checksum.write_text('\n'.join(lines+[d+'  '+n for n,d in results])+'\n')
    index = ROOT/'index.html'
    html = index.read_text()
    for name,d in results:
        entry = f'<p><a href="{name}">{name}</a> — Performance RC: five-minute Cricky widget directory cache; Xbox validation pending.</p>'
        if entry not in html:
            assert html.count('</body>') == 1
            html = html.replace('</body>',entry+'\n</body>')
    index.write_text(html)
