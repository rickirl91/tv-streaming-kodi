#!/usr/bin/env python3
"""Reproducible, offline ZIP packager for Cricky Home Personalisation v0.1.2.

Run from any directory: python tools/build-homepersonalisation-012.py
Never connects to Kodi, Trakt, the Xbox, or the Internet.
"""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from xml.etree import ElementTree as ET
import ast
import hashlib

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'plugin.video.tvstreaming.homepersonalisation'
SOURCE = ROOT / 'src' / 'homepersonalisation'
OUTPUT = ROOT / (PREFIX + '-0.1.2-RC.zip')
FILES = ('README.txt', 'addon.xml', 'core.py', 'default.py')

meta = ET.parse(SOURCE / 'addon.xml').getroot()
assert meta.attrib['id'] == PREFIX
assert meta.attrib['version'] == '0.1.2'
for name in ('default.py', 'core.py'):
    ast.parse((SOURCE / name).read_text(encoding='utf-8'))
src = (SOURCE / 'default.py').read_text(encoding='utf-8')
assert "'landscape': artwork" in src
assert "properties={'override_landscape': artwork}" in src

with ZipFile(OUTPUT, 'w', compression=ZIP_DEFLATED, compresslevel=9) as z:
    for name in FILES:
        info = ZipInfo(PREFIX + '/' + name, date_time=(2026, 11, 23, 0, 0, 0))
        info.compress_type = ZIP_DEFLATED
        info.create_system = 3
        info.external_attr = (0o100644 << 16)
        z.writestr(info, (SOURCE / name).read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)
with ZipFile(OUTPUT) as z:
    assert z.testzip() is None
    assert len(z.namelist()) == len(FILES)
    for name in FILES:
        assert z.read(PREFIX + '/' + name) == (SOURCE / name).read_bytes()
print(OUTPUT.name, OUTPUT.stat().st_size, hashlib.sha256(OUTPUT.read_bytes()).hexdigest())
