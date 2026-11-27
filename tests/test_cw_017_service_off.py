import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

class ServiceOffTests(unittest.TestCase):
    def test_only_manifest_differs(self):
        root = Path(__file__).resolve().parents[1] / 'release-candidates'
        old, new = [root / ('homepersonalisation-' + v) for v in ('0.1.16','0.1.17')]
        self.assertEqual(sorted(p.name for p in old.iterdir() if p.is_file()), sorted(p.name for p in new.iterdir() if p.is_file()))
        for p in old.iterdir():
            if p.is_file() and p.name != 'addon.xml':
                self.assertEqual(p.read_bytes(), (new/p.name).read_bytes(), p.name)
        manifest = ET.parse(new/'addon.xml').getroot()
        self.assertEqual(manifest.get('version'),'0.1.17')
        self.assertFalse(any(e.get('point')=='xbmc.service' for e in manifest.findall('extension')))
        self.assertTrue(any(e.get('point')=='xbmc.python.pluginsource' for e in manifest.findall('extension')))
