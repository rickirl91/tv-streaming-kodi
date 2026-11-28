from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from xml.etree import ElementTree as ET
import hashlib
root=Path(__file__).resolve().parents[1]
src=root/'release-candidates'/'diagsetup-0.2.1'
addon='script.tvstreaming.diagsetup'
name=addon+'-0.2.1-RC.zip'
files={addon+'/'+n:(src/n).read_bytes() for n in ('addon.xml','core.py','default.py','guard.py','service.py','plugin.py')}
for n,b in files.items():
    if n.endswith('.py'):
        compile(b,n,'exec')
m=ET.fromstring(files[addon+'/addon.xml'])
assert m.get('id')==addon and m.get('version')=='0.2.1'
assert sum(x.get('point')=='xbmc.service' for x in m.findall('extension'))==1
with ZipFile(root/name,'w') as z:
    for n,b in sorted(files.items()):
        i=ZipInfo(n,(2026,11,28,0,0,0))
        i.external_attr=0o100644<<16
        z.writestr(i,b,compress_type=ZIP_DEFLATED,compresslevel=9)
with ZipFile(root/name) as z:
    assert z.testzip() is None and set(z.namelist())==set(files)
    assert all(z.read(n)==b for n,b in files.items())
digest=hashlib.sha256((root/name).read_bytes()).hexdigest()
p=root/'SHA256SUMS.txt'
p.write_text('\n'.join([l for l in p.read_text().splitlines() if not l.endswith('  '+name)]+[digest+'  '+name])+'\n')
p=root/'index.html'
h=p.read_text()
entry=f'<p><a href="{name}">{name}</a> — Diag-only standard, staggered and lazy row loading test.</p>'
if entry not in h:
    assert h.count('</body>')==1
    p.write_text(h.replace('</body>',entry+'\n</body>'))
print('PASS',name,digest)
