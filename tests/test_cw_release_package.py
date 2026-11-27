import unittest
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree

class ContinueWatchingPackageTests(unittest.TestCase):
    def test_package(self):
        root = Path(__file__).resolve().parents[1] / 'release-candidates'
        source = root / 'homepersonalisation'
        addon = 'plugin.video.tvstreaming.homepersonalisation'
        with ZipFile(root / (addon + '-0.1.7-RC.zip')) as z:
            self.assertIsNone(z.testzip())
            expected = {addon+'/'+p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}
            self.assertEqual(sorted(z.namelist()),sorted(expected))
            for name,data in expected.items():
                self.assertEqual(z.read(name),data,name)
                if name.endswith('.py'):
                    compile(data,name,'exec')
            manifest = ElementTree.fromstring(z.read(addon+'/addon.xml'))
            self.assertEqual(manifest.get('version'),'0.1.7')
            self.assertTrue(any(e.get('point')=='xbmc.service' and e.get('library')=='cw_service.py' for e in manifest.findall('extension')))
