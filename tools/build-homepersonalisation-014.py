#!/usr/bin/env python3
"""Build and verify the opt-in 0.1.14 installer from committed source."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from xml.etree import ElementTree as ET
import hashlib

root = Path(__file__).resolve().parents[1]
source = root / 'release-candidates' / 'homepersonalisation-0.1.14'
addon = 'plugin.video.tvstreaming.homepersonalisation'
name = addon + '-0.1.14-RC.zip'
output = root / name
files = {addon+'/'+p.name: p.read_bytes() for p in sorted(source.iterdir()) if p.is_file()}
assert len(files) == 13, sorted(files)
for path, data in files.items():
    if path.endswith('.py'):
        compile(data, path, 'exec')
manifest = ET.fromstring(files[addon+'/addon.xml'])
assert manifest.get('id') == addon and manifest.get('version') == '0.1.14'
assert any(e.get('point')=='xbmc.service' and e.get('library')=='cw_service.py' for e in manifest.findall('extension'))
with ZipFile(output, 'w') as z:
    for path, data in files.items():
        info = ZipInfo(path, (2026,11,27,0,0,0))
        info.external_attr = 0o100644 << 16
        z.writestr(info, data, compress_type=ZIP_DEFLATED, compresslevel=9)
with ZipFile(output) as z:
    assert z.testzip() is None
    assert sorted(z.namelist()) == sorted(files)
    assert all(z.read(p)==d for p,d in files.items())
checksum = root/'SHA256SUMS.txt'
lines = [l for l in checksum.read_text().splitlines() if not l.endswith('  '+name)]
lines.append(hashlib.sha256(output.read_bytes()).hexdigest()+'  '+name)
checksum.write_text('\n'.join(lines)+'\n')
index = root/'index.html'
html = index.read_text()
old = '<p><a href="plugin.video.tvstreaming.homepersonalisation-0.1.13-RC.zip">plugin.video.tvstreaming.homepersonalisation-0.1.13-RC.zip</a> — Recency ordering and deferred refresh candidate.</p>'
new = f'<p><a href="{name}">{name}</a> — Durable playback queue and idle-only restoration candidate; Xbox validation pending.</p>'
if new not in html:
    assert old in html
    index.write_text(html.replace(old, old+'\n'+new, 1))
print('PASS', name, output.stat().st_size)
