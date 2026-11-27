import ast
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'release-candidates' / 'safesearch-0.2.0'
spec = importlib.util.spec_from_file_location('safe_core_020', SRC / 'core.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


class SafeSearch(unittest.TestCase):
    def test_native_combined_search_and_history(self):
        for query in ('You', 'A, B & C (2026)', 'Caf\u00e9', 'a%20b', 'a/b?x=y'):
            command = core.search_command('  ' + query + ' ')
            self.assertTrue(command.startswith('ActivateWindow(Videos,plugin://'))
            self.assertTrue(command.endswith(',return)'))
            uri = command[len('ActivateWindow(Videos,'):-len(',return)')]
            self.assertEqual(urlsplit(uri).netloc, core.HELPER)
            self.assertEqual(parse_qs(urlsplit(uri).query), {
                'info': ['search'], 'tmdb_type': ['both'], 'query': [query], 'history': ['true']})
            self.assertNotIn('multisearch', command)
        self.assertIsNone(core.search_command('  '))

    def test_profile_guard(self):
        self.assertTrue(core.allowed_profile(' Cricky '))
        for name in ('Kids', 'Ross', 'Ria', 'Guest', 'Ricky', 'Christine', ''):
            self.assertFalse(core.allowed_profile(name))

    def test_no_service_or_skin_writes(self):
        manifest = ET.parse(SRC / 'addon.xml').getroot()
        self.assertEqual(manifest.get('id'), core.ADDON_ID)
        self.assertEqual(manifest.get('version'), '0.2.0')
        self.assertEqual([e.get('point') for e in manifest.findall('extension')],
                         ['xbmc.python.script', 'xbmc.addon.metadata'])
        for p in SRC.glob('*.py'):
            code = p.read_text()
            compile(code, str(p), 'exec')
            imports = [alias.name for n in ast.walk(ast.parse(code)) if isinstance(n, ast.Import) for alias in n.names]
            self.assertFalse(set(imports) & {'os', 'pathlib', 'xbmcvfs', 'xbmcaddon', 'tempfile'})
            self.assertNotIn('Includes_Home', code)

    def load_launcher(self, profile='Cricky', confirmed=True, query='You', playing=False):
        xbmc = MagicMock()
        gui = MagicMock()
        xbmc.getInfoLabel.return_value = profile
        xbmc.Player.return_value.isPlaying.return_value = playing
        xbmc.Keyboard.return_value.isConfirmed.return_value = confirmed
        xbmc.Keyboard.return_value.getText.return_value = query
        spec = importlib.util.spec_from_file_location('safe_launch_020', SRC / 'default.py')
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'xbmc': xbmc, 'xbmcgui': gui, 'core': core}):
            spec.loader.exec_module(module)
        return module, xbmc, gui

    def test_launch_once(self):
        mod, xbmc, _ = self.load_launcher()
        mod.launch()
        xbmc.executebuiltin.assert_called_once_with(core.search_command('You'))

    def test_cancel_blank_other_profile_and_active_playback(self):
        for kwargs in ({'confirmed': False}, {'query': ' '}, {'profile': 'Kids'}, {'playing': True}):
            mod, xbmc, _ = self.load_launcher(**kwargs)
            mod.launch()
            xbmc.executebuiltin.assert_not_called()

    def test_profile_switch_during_keyboard(self):
        mod, xbmc, _ = self.load_launcher()
        xbmc.getInfoLabel.side_effect = ['Cricky', 'Kids']
        mod.launch()
        xbmc.executebuiltin.assert_not_called()


if __name__ == '__main__':
    unittest.main()
