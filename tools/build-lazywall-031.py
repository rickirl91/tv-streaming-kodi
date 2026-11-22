#!/usr/bin/env python3
"""Build v0.3.1 RC from the existing v0.3.0 ZIP and the auditable patch."""
from pathlib import Path
import hashlib
import subprocess
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
    subprocess.run(['patch', '-p1', '--batch', '--forward', '-i', str(PATCH)], cwd=directory, check=True)
    addon = directory / 'addon.xml'
    addon_text = addon.read_text(encoding='utf-8')
    assert 'version="0.3.0"' in addon_text
    addon.write_text(addon_text.replace('version="0.3.0"', 'version="0.3.1"', 1), encoding='utf-8')
    readme = directory / 'README.txt'
    readme.write_text(readme.read_text(encoding='utf-8') + '''
0.3.1 RC: For custom bulk rollout TMDb Helper lists, remove single-page
widget restrictions and follow the native Next Page directory item when
available. Preserve genre/TV/provider filters, action links, movie-details,
YouTube trailers and navigation state. Xbox validation is required.
''', encoding='utf-8')
    with zipfile.ZipFile(NEW, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(directory.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(stage).as_posix())

with zipfile.ZipFile(NEW) as archive:
    assert archive.testzip() is None
    source = archive.read(ZIP_ROOT + '/default.py')
    compile(source, ZIP_ROOT + '/default.py', 'exec')
    assert b'def next_page_directory_path(' in source
    assert b'nextpage' in source
    assert b'version="0.3.1"' in archive.read(ZIP_ROOT + '/addon.xml')

mirror = ROOT / 'zips/script.tvstreaming.lazywall' / NEW_NAME
mirror.parent.mkdir(parents=True, exist_ok=True)
mirror.write_bytes(NEW.read_bytes())
checksum = hashlib.sha256(NEW.read_bytes()).hexdigest()
sums_file = ROOT / 'SHA256SUMS.txt'
sums = sums_file.read_text(encoding='utf-8')
assert NEW_NAME not in sums
sums_file.write_text(sums.rstrip() + f'\n{checksum}  {NEW_NAME}\n{checksum}  zips/script.tvstreaming.lazywall/{NEW_NAME}\n', encoding='utf-8')

index_file = ROOT / 'index.html'
index = index_file.read_text(encoding='utf-8')
assert NEW_NAME not in index
assert '<ul>' in index
index_file.write_text(index.replace('<ul>', '<ul>\n<li><a href="' + NEW_NAME + '">' + NEW_NAME + '</a> — <strong>Pagination fix:</strong> TMDb Helper next-page browsing for streaming providers, Trending, Recently Released and TV categories; update Lazy Wall only (v0.3.1 RC).</li>', 1), encoding='utf-8')

notes = ROOT / 'TV_STREAMING_RC_031_ACCEPTANCE.md'
notes.write_text('''# TV Streaming Lazy Wall v0.3.1 RC — multi-source pagination

## Fault
Bulk rollout v0.3.0 showed only 20 items and “end of catalogue” in non-genre source lists, including Apple TV+ Movies and Apple TV+ Series. Action Movies already paged beyond 20.

## Scoped fix
For TMDb Helper source lists, remove widget-only/single-page restrictions and use the add-on’s Next Page directory path when present. Retain the configured source filters and only probe a following numbered page when the first results batch is complete. No changes to StreamRow, Bulk Setup, Trakt, genre playback, user profiles or skin settings.

## Xbox check
Install script.tvstreaming.lazywall-0.3.1-RC.zip via Kodi’s existing rickirl91 source. Test Apple TV+ Movies, Apple TV+ Series and Trending TV; scroll past the first 20 to verify a further batch. Retest Action Movies; check movie Play/Trailer and return-to-position. If a row still has only 20 items, record its exact widget source path for a targeted follow-up.

**Status:** Locally packaged and syntax validated; live Xbox browsing remains to be confirmed.
''', encoding='utf-8')
print('PASS', NEW_NAME, NEW.stat().st_size, 'bytes SHA256', checksum)
