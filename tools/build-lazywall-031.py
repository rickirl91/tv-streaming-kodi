#!/usr/bin/env python3
"""Reproducibly build Lazy Wall v0.3.1 RC using exact verified v0.3.0 source."""
from pathlib import Path
import ast
import difflib
import hashlib
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'script.tvstreaming.lazywall-0.3.0-RC.zip'
NEW_NAME = 'script.tvstreaming.lazywall-0.3.1-RC.zip'
NEW = ROOT / NEW_NAME
PATCH = ROOT / 'tools/lazywall-031-paging.patch'
ZIP_ROOT = 'script.tvstreaming.lazywall'

with tempfile.TemporaryDirectory(prefix='lazywall031-') as dirname:
    stage = Path(dirname)
    with zipfile.ZipFile(OLD) as archive:
        assert archive.testzip() is None
        archive.extractall(stage)
    directory = stage / ZIP_ROOT
    source_file = directory / 'default.py'
    original = source_file.read_text(encoding='utf-8')
    modified = original

    def replace_once(before, after):
        global modified
        count = modified.count(before)
        assert count == 1, 'Expected one source anchor, found {}: {}'.format(count, before[:100])
        modified = modified.replace(before, after, 1)

    replace_once('from urllib.parse import parse_qs, urlparse',
                 'from urllib.parse import parse_qs, urlencode, urlparse, urlunparse')

    helpers = '''
def normalise_source_directory(path):
    """Remove widget-only flags, preserving every source/provider/genre filter."""
    parsed = urlparse(path)
    if parsed.scheme != 'plugin' or parsed.netloc != 'plugin.video.themoviedb.helper':
        return path
    query = parse_qs(parsed.query, keep_blank_values=True)
    for key in ('widget', 'reload', 'cacheonly', 'nextpage', 'limit', 'length'):
        query.pop(key, None)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params,
                       urlencode(query, doseq=True), parsed.fragment))


def numbered_next_page(path):
    """Cautious fallback when TMDb Helper does not expose its Next Page tile."""
    parsed = urlparse(path)
    if parsed.scheme != 'plugin' or parsed.netloc != 'plugin.video.themoviedb.helper':
        return None
    query = parse_qs(parsed.query, keep_blank_values=True)
    current = query.get('page', ['1'])[0]
    if not str(current).isdigit():
        return None
    query['page'] = [str(int(current) + 1)]
    query.pop('widget', None)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params,
                       urlencode(query, doseq=True), parsed.fragment))


'''
    replace_once('\ndef split_page(entries):\n', '\n' + helpers + 'def split_page(entries):\n')
    replace_once("            self._root_directory = source['url']",
                 "            self._root_directory = normalise_source_directory(source['url'])")

    register_before = '''    def _register_next(self, path):
        if not path or not path.startswith('plugin://plugin.video.themoviedb.helper/'):
            self._end_reached = True
        elif path in self._paths:
            # Guard plugin pagination loops; no artificial catalogue cap.
            self._end_reached = True
            log('Stopping repeated TMDb Helper page URL', xbmc.LOGWARNING)
        else:
            self._paths.append(path)
'''
    register_after = '''    def _register_next(self, path, page_size=0):
        # Prefer TMDb Helper's actual Next Page directory. A full 20-title
        # batch with no advertised link is not proof that a catalogue ends.
        # Probe the next numbered directory once; the existing dedupe/end
        # logic stops if the source ignores page=N or returns no new titles.
        if not path and page_size >= 20:
            path = numbered_next_page(self._paths[-1])
        if not path or not path.startswith('plugin://plugin.video.themoviedb.helper/'):
            self._end_reached = True
        elif path in self._paths:
            self._end_reached = True
            log('Stopping repeated TMDb Helper page URL', xbmc.LOGWARNING)
        else:
            self._paths.append(path)
'''
    replace_once(register_before, register_after)

    replace_once('''            self._loaded_pages = 1
            self._register_next(next_path)
''', '''            self._loaded_pages = 1
            self._register_next(next_path, len(movies))
''')

    replace_once('''                if index == len(self._paths) - 1:
                    self._register_next(next_path)
''', '''                if index == len(self._paths) - 1:
                    self._register_next(next_path, len(data))
''')

    assert modified != original
    compile(modified, str(source_file), 'exec')
    source_file.write_text(modified, encoding='utf-8')

    # Keep an exact, reviewable patch rather than an unverified guessed diff.
    PATCH.write_text(''.join(difflib.unified_diff(
        original.splitlines(keepends=True), modified.splitlines(keepends=True),
        fromfile='a/default.py', tofile='b/default.py')), encoding='utf-8')

    addon = directory / 'addon.xml'
    addon_text = addon.read_text(encoding='utf-8')
    assert 'version="0.3.0"' in addon_text
    addon.write_text(addon_text.replace('version="0.3.0"', 'version="0.3.1"', 1), encoding='utf-8')
    readme = directory / 'README.txt'
    readme.write_text((readme.read_text(encoding='utf-8') if readme.exists() else '') + '''
0.3.1 RC: Expanded full TMDb Helper lists now request directory mode;
follow native Next Page or cautiously probe another numbered page when
there are 20 titles but no page link. Preserve filters, selection, details,
trailers and playback. Test on Xbox before marking accepted.
''', encoding='utf-8')
    with zipfile.ZipFile(NEW, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(directory.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(stage).as_posix())

with zipfile.ZipFile(NEW) as archive:
    assert archive.testzip() is None
    source = archive.read(ZIP_ROOT + '/default.py')
    compile(source, ZIP_ROOT + '/default.py', 'exec')
    assert b'def normalise_source_directory(' in source
    assert b'def numbered_next_page(' in source
    assert b'version="0.3.1"' in archive.read(ZIP_ROOT + '/addon.xml')

# Exercise pure URL transformations without Kodi imports.
module = ast.parse(source.decode('utf-8'))
url_functions = [n for n in module.body if isinstance(n, ast.FunctionDef)
                 and n.name in ('normalise_source_directory', 'numbered_next_page')]
assert len(url_functions) == 2
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
ns = {'parse_qs': parse_qs, 'urlencode': urlencode,
      'urlparse': urlparse, 'urlunparse': urlunparse}
exec(compile(ast.Module(body=url_functions, type_ignores=[]), '<url-tests>', 'exec'), ns)
sample = 'plugin://plugin.video.themoviedb.helper/?info=discover&tmdb_type=movie&with_watch_providers=2&widget=true&reload='
normal = ns['normalise_source_directory'](sample)
q = parse_qs(urlparse(normal).query)
assert q.get('info') == ['discover'] and q.get('with_watch_providers') == ['2']
assert 'widget' not in q and 'reload' not in q
next_page = ns['numbered_next_page'](normal)
assert parse_qs(urlparse(next_page).query)['page'] == ['2']
assert parse_qs(urlparse(ns['numbered_next_page'](next_page)).query)['page'] == ['3']

mirror = ROOT / 'zips/script.tvstreaming.lazywall' / NEW_NAME
mirror.parent.mkdir(parents=True, exist_ok=True)
mirror.write_bytes(NEW.read_bytes())
checksum = hashlib.sha256(NEW.read_bytes()).hexdigest()
sums_file = ROOT / 'SHA256SUMS.txt'
sums = sums_file.read_text(encoding='utf-8')
if NEW_NAME not in sums:
    sums_file.write_text(sums.rstrip() + f'\n{checksum}  {NEW_NAME}\n{checksum}  zips/script.tvstreaming.lazywall/{NEW_NAME}\n', encoding='utf-8')
else:
    assert checksum in sums, 'Existing checksum differs; stop before overwrite'

index_file = ROOT / 'index.html'
index = index_file.read_text(encoding='utf-8')
if NEW_NAME not in index:
    assert '<ul>' in index
    index_file.write_text(index.replace('<ul>', '<ul>\n<li><a href="' + NEW_NAME + '">' + NEW_NAME + '</a> — <strong>Pagination fix (RC):</strong> TMDb Helper full-directory mode plus cautious next-page fallback for provider and TV catalogues. Update Lazy Wall only.</li>', 1), encoding='utf-8')

notes = ROOT / 'TV_STREAMING_RC_031_ACCEPTANCE.md'
notes.write_text('''# TV Streaming Lazy Wall v0.3.1 RC — bulk source pagination

## Fault
After bulk rollout v0.3.0, some Apple TV+ Movies and Apple TV+ Series lists show exactly 20 titles and incorrectly say end of catalogue. Action Movies successfully pages.

## Scoped fix
For configured TMDb Helper source directories, remove widget-only restrictions but keep every source filter; retain Next Page links where present; cautiously try page 2 if page 1 has 20 results but no Next Page. Duplicate/empty results stop pagination. Native genre paths, 200-poster window, Play, trailer and return-position logic are unchanged.

## Xbox acceptance
Install script.tvstreaming.lazywall-0.3.1-RC.zip. Open Apple TV+ Movies, Apple TV+ Series and a Trending TV or Movie source, scroll after title 20, and confirm whether more titles load. Retest Action Movies, movie Play/Trailer and return-to-position. If no additional results, capture exact provider source URL for further diagnosis.

**Status:** Package and Python syntax/URL transformations verified in automated build; Xbox behaviour requires testing.
''', encoding='utf-8')
print('PASS', NEW_NAME, NEW.stat().st_size, 'bytes SHA256', checksum)
