import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'release-candidates'/'diagsetup-0.1.0'))
import core

class DiagTests(unittest.TestCase):
    def test_rows(self):
        rows=json.loads(core.planned())
        self.assertEqual(len(rows),10)
        self.assertEqual(len({r['path'] for r in rows}),10)
        for r in rows:
            p=urlparse(r['path'])
            self.assertEqual(p.netloc,'plugin.video.themoviedb.helper')
            self.assertEqual(parse_qs(p.query)['widget'],['true'])
            self.assertEqual(r['widget_style'],'Poster')
    def test_guard(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'profiles'/'diag'
            self.assertEqual(core.verify('diag','skin.arctic.fuse.3',p,d),p.resolve())
            for name,skin,profile in [('Cricky','skin.arctic.fuse.3',p),('diag','skin.estuary',p),('diag','skin.arctic.fuse.3',d),('diag','skin.arctic.fuse.3',p.parent/'Kids')]:
                with self.assertRaises(ValueError):
                    core.verify(name,skin,profile,d)
    def test_apply_restore_exact(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            target=core.safe_path(root,core.REL)
            old=b'[{"label":"original"}]\n'
            core.atomic(target,old)
            core.apply(root,old)
            self.assertEqual(target.read_bytes(),core.planned())
            core.restore(root)
            self.assertEqual(target.read_bytes(),old)
    def test_absent_and_newer_edits(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            target=core.safe_path(root,core.REL)
            core.apply(root,None)
            core.atomic(target,b'[]')
            with self.assertRaises(ValueError):
                core.restore(root)
            core.atomic(target,core.planned())
            core.restore(root)
            self.assertFalse(target.exists())
    def test_changed_before_apply(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            core.atomic(core.safe_path(root,core.REL),b'[]')
            with self.assertRaises(ValueError):
                core.apply(root,None)
            self.assertFalse(core.safe_path(root,core.BACKUP).exists())

if __name__=='__main__':
    unittest.main()
