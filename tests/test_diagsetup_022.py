import tempfile, unittest, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'release-candidates'/'diagsetup-0.2.2'))
import core

class TestDiag(unittest.TestCase):
    def test_paths(self):
        rows=json.loads(core.deferred())
        self.assertEqual(len(rows),10)
        for i,r in enumerate(rows):
            self.assertIn(core.prop(i),r['path'])
            self.assertTrue(core.native(i).startswith('plugin://plugin.video.themoviedb.helper/'))
        self.assertEqual([r['label'] for r in rows],[r['label'] for r in json.loads(core.planned())])
    def test_upgrade_restore(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            target=core.safe_path(root,core.REL)
            backup=core.safe_path(root,core.BACKUP)
            core.atomic(target,core.planned())
            core.atomic(backup,b'{"original":null}')
            core.apply(root,core.planned(),'staggered')
            self.assertEqual(core.mode(root),'staggered')
            core.apply(root,core.deferred(),'lazy')
            self.assertEqual(core.mode(root),'lazy')
            self.assertEqual(backup.read_bytes(),b'{"original":null}')
            core.restore(root)
            self.assertFalse(target.exists())
            self.assertEqual(core.mode(root),'standard')
    def test_guard(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'profiles'/'diag'
            self.assertEqual(core.verify('diag','skin.arctic.fuse.3',p,d),p)
            with self.assertRaises(ValueError):
                core.verify('Cricky','skin.arctic.fuse.3',p,d)
            with self.assertRaises(ValueError):
                core.verify('diag','skin.arctic.fuse.3',d,d)
    def test_stagger(self):
        s=core.Scheduler('staggered')
        self.assertEqual(s.tick(0,True,None,{}),[0,1])
        self.assertEqual(s.tick(1,True,None,{}),[])
        self.assertEqual(s.tick(2,False,None,{0:True}),[])
        self.assertEqual(s.tick(3,True,None,{0:True}),[2])
        self.assertEqual(len(s.pending),2)
        self.assertEqual(s.tick(4,True,None,{1:True,2:True}),[3,4])
    def test_lazy(self):
        s=core.Scheduler('lazy')
        self.assertEqual(s.tick(0,True,None,{}),[0,1])
        self.assertEqual(s.tick(2,True,0,{0:True,1:True}),[])
        self.assertEqual(s.tick(3,True,1,{}),[2])
        self.assertEqual(s.tick(4,False,8,{2:True}),[])
        self.assertEqual(s.tick(5,True,2,{2:True}),[3])
        self.assertEqual(s.tick(6,True,0,{3:True}),[])
    def test_timeout(self):
        s=core.Scheduler('staggered')
        s.tick(0,True,None,{})
        self.assertEqual(s.tick(46,True,None,{}),[])
        self.assertTrue(s.failed)
        self.assertEqual(s.tick(47,True,None,{0:True,1:True}),[])
    def test_newer_edit(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            core.apply(root,None,'lazy')
            target=core.safe_path(root,core.REL)
            core.atomic(target,b'[]')
            with self.assertRaises(ValueError):
                core.apply(root,b'[]','standard')
            with self.assertRaises(ValueError):
                core.restore(root)

class TestLaunch(unittest.TestCase):
    def test_directory_root_and_action(self):
        import types
        from unittest.mock import Mock, patch
        fake={n:types.ModuleType(n) for n in ('xbmc','xbmcgui','xbmcaddon','xbmcplugin','xbmcvfs')}
        fake['xbmcgui'].ListItem=Mock()
        fake['xbmcplugin'].addDirectoryItem=Mock()
        fake['xbmcplugin'].setContent=Mock()
        fake['xbmcplugin'].endOfDirectory=Mock()
        with patch.dict(sys.modules,fake):
            import plugin
            with patch.object(plugin,'root',return_value=Path('.')),patch.object(plugin,'run') as run:
                plugin.directory(['plugin://script.tvstreaming.diagsetup/','1',''])
                self.assertEqual(fake['xbmcplugin'].addDirectoryItem.call_count,5)
                fake['xbmcplugin'].endOfDirectory.assert_called_with(1,succeeded=True,cacheToDisc=False)
                plugin.directory(['plugin://script.tvstreaming.diagsetup/','1','?action=1'])
                run.assert_called_once_with(1)
                fake['xbmcplugin'].endOfDirectory.assert_called_with(1,succeeded=True,cacheToDisc=False)


class TestStatus(unittest.TestCase):
    def test_config_kind(self):
        self.assertEqual(core.config_kind(core.planned()),'standard')
        self.assertEqual(core.config_kind(core.deferred()),'deferred')
        rows=json.loads(core.deferred())
        for x in rows:
            x['guid']='example'
        self.assertEqual(core.config_kind(json.dumps(rows).encode()),'deferred')
        rows[0]['path']='unexpected'
        self.assertEqual(core.config_kind(json.dumps(rows).encode()),'other')
        self.assertEqual(core.config_kind(None),'missing')
    def test_status(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self.assertEqual(core.read_status(root),{})
            data={'mode':'lazy','state':'active','loaded':2}
            core.write_status(root,data)
            self.assertEqual(core.read_status(root),data)

if __name__=='__main__':
    unittest.main()
