import importlib.util
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'release-candidates' / 'safesearch-0.1.0'
spec = importlib.util.spec_from_file_location('safesearch_core', SRC / 'core.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
FIXTURE = b'<includes>\n' + core.MARKER + b'\n        <include content="Home_ControlList_Item">\n            <param name="label">$LOCALIZE[137]</param>\n' + core.OLD_LINE + b'\n            <param name="enabled">[!Skin.HasSetting(HomeSwitcher.DisableSearch)]</param>\n        </include>\n    </include>\n    <include name="Other"><control /></include>\n</includes>\n'


class SafeSearch(unittest.TestCase):
    def test_exact_scope_and_profile_fallback(self):
        changed = core.patch(FIXTURE)
        core.validate(changed, patched=True)
        old, new = map(ET.fromstring, (FIXTURE, changed))
        self.assertEqual(ET.tostring(old.find('./include[@name="Other"]')), ET.tostring(new.find('./include[@name="Other"]')))
        self.assertEqual(new.find('./variable/value').get('condition'), 'String.IsEqual(System.ProfileName,Cricky)')
        self.assertEqual(new.findall('./variable/value')[1].text, core.ORIGINAL)
        self.assertIn(b'<param name="label">$LOCALIZE[137]</param>', changed)
        self.assertIn(b'[!Skin.HasSetting(HomeSwitcher.DisableSearch)]', changed)

    def test_reject_unexpected_and_repeated_patch(self):
        for invalid in (b'<bad/>', FIXTURE.replace(core.OLD_LINE, b''), FIXTURE.replace(core.MARKER, core.MARKER + core.MARKER), core.patch(FIXTURE)):
            with self.assertRaises(ValueError):
                core.patch(invalid)

    def test_preserve_crlf(self):
        result = core.patch(FIXTURE.replace(b'\n', b'\r\n'))
        self.assertNotIn(b'\n', result.replace(b'\r\n', b''))

    def test_search_uses_native_video_window_and_escaped_query(self):
        for query in ('You', 'A, B & C (2026)', 'Caf\u00e9'):
            command = core.search_command(query)
            self.assertTrue(command.startswith('ActivateWindow(Videos,plugin://'))
            self.assertTrue(command.endswith(',return)'))
            uri = command[len('ActivateWindow(Videos,'):-len(',return)')]
            params = parse_qs(urlsplit(uri).query)
            self.assertEqual(params, {'info': ['search'], 'tmdb_type': ['both'], 'query': [query]})
            self.assertNotIn('multisearch', command)
        self.assertIsNone(core.search_command('  '))

    def test_no_background_service(self):
        addon = ET.parse(SRC / 'addon.xml').getroot()
        self.assertEqual(addon.get('id'), core.ADDON_ID)
        self.assertEqual(addon.get('version'), '0.1.0')
        self.assertNotIn('xbmc.service', [x.get('point') for x in addon.findall('extension')])
        for p in SRC.glob('*.py'):
            compile(p.read_bytes(), str(p), 'exec')


if __name__ == '__main__':
    unittest.main()
