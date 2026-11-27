#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from xml.etree import ElementTree as ET
import hashlib

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'release-candidates' / 'safesearch-0.1.0'
ADDON = 'script.tvstreaming.safesearch'
NAME = ADDON + '-0.1.0-RC.zip'
files = {ADDON + '/' + name: (SRC / name).read_bytes() for name in ('addon.xml', 'core.py', 'default.py')}
for path, data in files.items():
    if path.endswith('.py'):
        compile(data, path, 'exec')
manifest = ET.fromstring(files[ADDON + '/addon.xml'])
assert manifest.get('id') == ADDON and manifest.get('version') == '0.1.0'
assert not any(x.get('point') == 'xbmc.service' for x in manifest.findall('extension'))
with ZipFile(ROOT / NAME, 'w') as out:
    for path, data in sorted(files.items()):
        info = ZipInfo(path, (2026, 11, 27, 0, 0, 0))
        info.external_attr = 0o100644 << 16
        out.writestr(info, data, compress_type=ZIP_DEFLATED, compresslevel=9)
with ZipFile(ROOT / NAME) as out:
    assert out.testzip() is None and set(out.namelist()) == set(files)
    assert all(out.read(k) == v for k, v in files.items())
digest = hashlib.sha256((ROOT / NAME).read_bytes()).hexdigest()
checksums = ROOT / 'SHA256SUMS.txt'
lines = [line for line in checksums.read_text().splitlines() if not line.endswith('  ' + NAME)]
checksums.write_text('\n'.join(lines + [digest + '  ' + NAME]) + '\n')
index = ROOT / 'index.html'
html = index.read_text()
entry = '<p><a href="' + NAME + '">' + NAME + '</a> — Cricky Safe Search; explicit reversible AF3 3.5.11 patch, Xbox acceptance pending.</p>'
if entry not in html:
    assert html.count('</body>') == 1
    index.write_text(html.replace('</body>', entry + '\n</body>'))
print('PASS', NAME, digest)
