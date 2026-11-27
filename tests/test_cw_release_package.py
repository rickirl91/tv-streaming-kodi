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

    def test_package_018(self):
        root = Path(__file__).resolve().parents[1] / 'release-candidates'
        source = root / 'homepersonalisation-0.1.8'
        addon = 'plugin.video.tvstreaming.homepersonalisation'
        with ZipFile(root.parent / (addon + '-0.1.8-RC.zip')) as z:
            self.assertIsNone(z.testzip())
            expected = {addon+'/'+p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}
            self.assertEqual(sorted(z.namelist()),sorted(expected))
            for name,data in expected.items():
                self.assertEqual(z.read(name),data,name)
                if name.endswith('.py'):
                    compile(data,name,'exec')
            manifest = ElementTree.fromstring(z.read(addon+'/addon.xml'))
            self.assertEqual(manifest.get('version'),'0.1.8')
            self.assertTrue(any(e.get('point')=='xbmc.service' and e.get('library')=='cw_service.py' for e in manifest.findall('extension')))

    def test_package_019(self):
        root = Path(__file__).resolve().parents[1] / 'release-candidates'
        source = root / 'homepersonalisation-0.1.9'
        addon = 'plugin.video.tvstreaming.homepersonalisation'
        with ZipFile(root.parent / (addon + '-0.1.9-RC.zip')) as z:
            self.assertIsNone(z.testzip())
            expected = {addon+'/'+p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}
            self.assertEqual(sorted(z.namelist()),sorted(expected))
            for name,data in expected.items():
                self.assertEqual(z.read(name),data,name)
                if name.endswith('.py'):
                    compile(data,name,'exec')
            manifest = ElementTree.fromstring(z.read(addon+'/addon.xml'))
            self.assertEqual(manifest.get('version'),'0.1.9')
            self.assertTrue(any(e.get('point')=='xbmc.service' and e.get('library')=='cw_service.py' for e in manifest.findall('extension')))

    def test_package_0110(self):
        root = Path(__file__).resolve().parents[1] / 'release-candidates'
        source = root / 'homepersonalisation-0.1.10'
        addon = 'plugin.video.tvstreaming.homepersonalisation'
        with ZipFile(root.parent / (addon + '-0.1.10-RC.zip')) as z:
            self.assertIsNone(z.testzip())
            expected = {addon+'/'+p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}
            self.assertEqual(sorted(z.namelist()),sorted(expected))
            for name,data in expected.items():
                self.assertEqual(z.read(name),data,name)
                if name.endswith('.py'):
                    compile(data,name,'exec')
            manifest = ElementTree.fromstring(z.read(addon+'/addon.xml'))
            self.assertEqual(manifest.get('version'),'0.1.10')
            self.assertTrue(any(e.get('point')=='xbmc.service' and e.get('library')=='cw_service.py' for e in manifest.findall('extension')))

    def test_package_0111(self):
        root = Path(__file__).resolve().parents[1] / 'release-candidates'
        source = root / 'homepersonalisation-0.1.11'
        addon = 'plugin.video.tvstreaming.homepersonalisation'
        with ZipFile(root.parent / (addon + '-0.1.11-RC.zip')) as z:
            self.assertIsNone(z.testzip())
            expected = {addon+'/'+p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}
            self.assertEqual(sorted(z.namelist()),sorted(expected))
            for name,data in expected.items():
                self.assertEqual(z.read(name),data,name)
                if name.endswith('.py'):
                    compile(data,name,'exec')
            manifest = ElementTree.fromstring(z.read(addon+'/addon.xml'))
            self.assertEqual(manifest.get('version'),'0.1.11')
            self.assertTrue(any(e.get('point')=='xbmc.service' and e.get('library')=='cw_service.py' for e in manifest.findall('extension')))

    def test_package_0112(self):
        root = Path(__file__).resolve().parents[1] / 'release-candidates'
        source = root / 'homepersonalisation-0.1.12'
        addon = 'plugin.video.tvstreaming.homepersonalisation'
        with ZipFile(root.parent / (addon + '-0.1.12-RC.zip')) as z:
            self.assertIsNone(z.testzip())
            expected = {addon+'/'+p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}
            self.assertEqual(sorted(z.namelist()),sorted(expected))
            for name,data in expected.items():
                self.assertEqual(z.read(name),data,name)
                if name.endswith('.py'):
                    compile(data,name,'exec')
            manifest = ElementTree.fromstring(z.read(addon+'/addon.xml'))
            self.assertEqual(manifest.get('version'),'0.1.12')
            self.assertTrue(any(e.get('point')=='xbmc.service' and e.get('library')=='cw_service.py' for e in manifest.findall('extension')))
