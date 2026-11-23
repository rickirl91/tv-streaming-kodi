#!/usr/bin/env python3
"""Build the standalone Cricky Home Personalisation v0.1.3 installer.

Use the committed source files; preserve the working plugin ID. Does not
access Kodi profiles or external services.
"""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import hashlib

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src' / 'homepersonalisation'
ADDON_ID = 'plugin.video.tvstreaming.homepersonalisation'
OUTPUT = ROOT / 'plugin.video.tvstreaming.homepersonalisation-0.1.3-RC.zip'
FILENAMES = ('README.txt', 'addon.xml', 'core.py', 'default.py')

for name in ('core.py', 'default.py'):
    compile((SOURCE / name).read_bytes(), name, 'exec')
assert 'version="0.1.3"' in (SOURCE / 'addon.xml').read_text()
with ZipFile(OUTPUT, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
    for name in FILENAMES:
        data = (SOURCE / name).read_bytes()
        info = ZipInfo(ADDON_ID + '/' + name, (2026, 11, 23, 0, 0, 0))
        info.compress_type = ZIP_DEFLATED
        info.external_attr = (0o100644 << 16)
        archive.writestr(info, data, compress_type=ZIP_DEFLATED, compresslevel=9)
with ZipFile(OUTPUT) as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == {ADDON_ID + '/' + n for n in FILENAMES}
print('PASS', OUTPUT.name, OUTPUT.stat().st_size, 'SHA256', hashlib.sha256(OUTPUT.read_bytes()).hexdigest())
