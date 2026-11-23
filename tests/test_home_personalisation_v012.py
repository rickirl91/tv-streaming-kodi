"""Offline regression tests for the v0.1.2 Cricky See All tile fix.
No Kodi/Xbox credentials or installed profile files are needed.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from urllib.parse import parse_qs, urlparse
from zipfile import ZipFile

ZIP=Path(__file__).resolve().parents[1]/'plugin.video.tvstreaming.homepersonalisation-0.1.2-RC.zip'
ID='plugin.video.tvstreaming.homepersonalisation'

class Item:
    def __init__(self,label='',path=''):
        self.label,self.path=label,path
        self.art={}
        self.props={}
    def setArt(self,art): self.art.update(art)
    def setInfo(self,*args): pass
    def setProperty(self,k,v): self.props[k]=v
    def getVideoInfoTag(self): return types.SimpleNamespace(setUniqueIDs=lambda x:None)

class TestWidget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        with ZipFile(ZIP) as z:
            assert z.testzip() is None
            z.extractall(cls.temp.name)
        cls.root=Path(cls.temp.name)/ID
        cls.oldmodules={name:sys.modules.get(name) for name in ('core','xbmc','xbmcgui','xbmcplugin','xbmcaddon','xbmcvfs')}
        cls.events=[]
        cls.art_exists=True
        cls.movie_path='plugin://plugin.video.themoviedb.helper/?info=details&tmdb_type=movie&tmdb_id=1'
        cls.tv_path='plugin://plugin.video.themoviedb.helper/?info=details&tmdb_type=tv&tmdb_id=2'
        xbmc=types.ModuleType('xbmc')
        xbmc.LOGINFO=1;xbmc.LOGWARNING=2;xbmc.LOGERROR=3
        xbmc.log=lambda *a:None
        xbmc.getInfoLabel=lambda key:'Cricky'
        xbmc.getSkinDir=lambda:'skin.arctic.fuse.3'
        def jsonrpc(q):
            kind=parse_qs(urlparse(json.loads(q)['params']['directory']).query)['tmdb_type'][0]
            return json.dumps({'result':{'files':[{'label':'Get Fast' if kind=='movie' else 'Top Gear',
                  'file':cls.movie_path if kind=='movie' else cls.tv_path,
                  'art':{'fanart':'file://get-fast-hero.jpg' if kind=='movie' else 'file://top-gear-hero.jpg',
                         'poster':'file://movie-poster.jpg' if kind=='movie' else 'file://tv-poster.jpg'},
                  'filetype':'directory','uniqueid':{'tmdb': '1' if kind=='movie' else '2'}}]}})
        xbmc.executeJSONRPC=jsonrpc
        xbmc.getCondVisibility=lambda *args:True
        gui=types.ModuleType('xbmcgui');gui.ListItem=Item;gui.Dialog=lambda:types.SimpleNamespace()
        plugin=types.ModuleType('xbmcplugin')
        plugin.addDirectoryItem=lambda handle,path,item,isFolder=True:cls.events.append((path,item,isFolder))
        plugin.setContent=lambda *a:None;plugin.endOfDirectory=lambda *a,**kw:None
        addon=types.ModuleType('xbmcaddon')
        addon.Addon=lambda n=None:types.SimpleNamespace(getAddonInfo=lambda key:'/kodi/addons/plugin.video.streamrow')
        vfs=types.ModuleType('xbmcvfs')
        vfs.exists=lambda s:cls.art_exists
        vfs.translatePath=lambda s:s
        for mod in (xbmc,gui,plugin,addon,vfs):sys.modules[mod.__name__]=mod
        sys.path.insert(0,str(cls.root))
        import core
        sys.modules['core']=core
        spec=importlib.util.spec_from_file_location('cricky_012',cls.root/'default.py')
        m=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        cls.mod=m

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(str(cls.root))
        for key,val in cls.oldmodules.items():
            if val is None:sys.modules.pop(key,None)
            else:sys.modules[key]=val
        cls.temp.cleanup()

    def setUp(self): self.events.clear();type(self).art_exists=True
    def test_widget_all_three_sections_use_neutral_landscape_with_hero(self):
        for kind in ('recommended','because','watchlist'):
            with self.subTest(kind=kind):
                self.events.clear()
                self.mod.handle_feed(5,{'kind':[kind],'mode':['widget']})
                self.assertEqual(len(self.events),3)
                path,item,_=self.events[0]
                neutral='/kodi/addons/plugin.video.streamrow/resources/media/see_all_miami_neutral_v024.png'
                self.assertTrue(item.label.startswith('See All - '))
                self.assertEqual(item.art['landscape'],neutral)
                self.assertEqual(item.art['poster'],neutral)
                self.assertEqual(item.art['thumb'],neutral)
                self.assertEqual(item.art['icon'],neutral)
                self.assertEqual(item.props['override_landscape'],neutral)
                self.assertEqual(item.art['fanart'],'file://get-fast-hero.jpg')
                self.assertEqual(self.events[1][0],self.movie_path)
                self.assertEqual(self.events[2][0],self.tv_path)
                self.assertIn('mode=all',path)
    def test_see_all_folder_not_inserted_in_full_directory(self):
        self.mod.handle_feed(5,{'kind':['because'],'mode':['all']})
        self.assertEqual([i.label for _,i,_ in self.events],['Get Fast','Top Gear'])
    def test_missing_streamrow_uses_neutral_fallback_not_first_title(self):
        type(self).art_exists=False
        self.mod.handle_feed(5,{'kind':['because'],'mode':['widget']})
        item=self.events[0][1]
        self.assertEqual(item.art['landscape'],'special://skin/extras/icons/folder.png')
        self.assertEqual(item.props['override_landscape'],item.art['landscape'])
        self.assertEqual(item.art['fanart'],'file://get-fast-hero.jpg')
    def test_upgrade_retains_backup_planner_and_feed_ids(self):
        with ZipFile(ZIP) as z:
            contents=z.namelist()
            self.assertEqual(len(contents),4)
            self.assertIn(b'version="0.1.2"',z.read(ID+'/addon.xml'))
            self.assertIn(b'apply_home(path, backups_path()',z.read(ID+'/default.py'))
            self.assertIn(b'plan_cleanup',z.read(ID+'/core.py'))
            self.assertIn(b'sync_becauseyouwatched',z.read(ID+'/core.py'))

if __name__=='__main__': unittest.main(verbosity=2)
