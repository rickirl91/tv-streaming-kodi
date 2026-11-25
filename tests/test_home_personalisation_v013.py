"""Cricky 0.1.3 targeted Poster-layout regression tests. Offline; no Xbox profile needed."""
from pathlib import Path
from zipfile import ZipFile
import sys, unittest, tempfile, json, importlib.util, hashlib, os, types
ID='plugin.video.tvstreaming.homepersonalisation'
ROOT=Path(__file__).resolve().parents[1]
ZIP=ROOT/'archive'/'releases'/'plugin.video.tvstreaming.homepersonalisation-0.1.3-RC.zip'

class PosterStyleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        with ZipFile(ZIP) as z:
            assert z.testzip() is None
            z.extractall(cls.temp.name)
        cls.path=Path(cls.temp.name)/ID
        spec=importlib.util.spec_from_file_location('cricky_core_013', cls.path/'core.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);cls.core=mod

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def sample(self, with_duplicates=True):
        c=self.core
        rows=[{'label':'Continue Watching','path':'plugin://continue','target':'videos','widget_style':'Poster','other':{'test':123}}]
        rows += [{'label':label,'path':c.widget_path(kind),'target':'videos','extra':{'id':kind}} for kind,label,_ in c.LABELS]
        rows += [{'label':'Up Next Episodes','path':'plugin://next','widget_style':'Landscape'},
                 {'label':'Trending Movies','path':'plugin://trending','widget_style':'Poster'}]
        if with_duplicates: rows += [{'label':'Your Movie Watchlist','path':'plugin://oldm'}, {'label':'Recommended Movies for You','path':'plugin://oldrm'}]
        return rows

    def test_original_create_has_explicit_poster_style(self):
        c=self.core
        old=[{'label':'Continue Watching','path':'plugin://continue'}, {'label':'Action Movies','path':'plugin://action'}]
        plan=c.plan_home(old)
        self.assertEqual([r.get('widget_style') for r in plan[1:4]],['Poster']*3)
        self.assertEqual(plan[0],old[0]);self.assertEqual(plan[4],old[1]);self.assertEqual(old[0],{'label':'Continue Watching','path':'plugin://continue'})

    def test_existing_three_are_only_changes(self):
        c=self.core
        orig=self.sample();snap=c.serialize_home(orig)
        expected=[1,2,3]
        self.assertEqual([i for i,r in c.poster_style_candidates(orig)],expected)
        edited=c.plan_poster_style(orig)
        self.assertEqual(len(orig),len(edited))
        self.assertEqual([x['label'] for x in orig],[x['label'] for x in edited])
        for i in range(len(orig)):
            if i in expected:
                self.assertEqual(edited[i],{**orig[i], 'widget_style':'Poster'})
                self.assertEqual(orig[i].get('widget_style'),None)
            else:self.assertEqual(edited[i],orig[i]);self.assertIs(edited[i],orig[i])
        self.assertEqual(c.serialize_home(orig),snap,'source rows were mutated')

    def test_partially_poster_already(self):
        c=self.core;orig=self.sample()
        orig[1]['widget_style']='Poster'
        self.assertEqual([i for i,r in c.poster_style_candidates(orig)],[2,3])
        out=c.plan_poster_style(orig)
        self.assertIs(out[1],orig[1]);self.assertEqual([r.get('widget_style') for r in out[1:4]],['Poster']*3)
        self.assertEqual(c.poster_style_candidates(out),[])

    def test_rejects_different_hub_or_path(self):
        c=self.core
        for i,mismatch in ((0,'Wrong Continue Watching'),(2,'Different Personalisation'),(3,'From Your List')):
            orig=self.sample();orig[i]['label']=mismatch
            with self.subTest(i=i),self.assertRaises(ValueError): c.plan_poster_style(orig)
        orig=self.sample();orig[2]['path']='plugin://untrusted'
        with self.assertRaises(ValueError):c.plan_poster_style(orig)

    def test_exact_backup_and_restore_with_changed_style(self):
        c=self.core
        with tempfile.TemporaryDirectory() as folder:
            home=Path(folder)/c.TARGET_NAME
            orig=self.sample();raw=c.serialize_home(orig)
            home.write_bytes(raw)
            backup=c.apply_home(home,Path(folder)/'backups',c.sha256(raw),planner=c.plan_poster_style)
            self.assertIsNotNone(backup)
            updated=home.read_bytes();self.assertNotEqual(raw,updated)
            manifest=json.loads((backup/'manifest.json').read_text())
            self.assertEqual((backup/c.TARGET_NAME).read_bytes(),raw)
            self.assertEqual(manifest['before_sha256'],c.sha256(raw))
            self.assertEqual(manifest['after_sha256'],c.sha256(updated))
            self.assertEqual(c.restore_home(home,backup),'restored')
            self.assertEqual(home.read_bytes(),raw)

    def test_conflicting_restore_refused(self):
        c=self.core
        with tempfile.TemporaryDirectory() as folder:
            home=Path(folder)/c.TARGET_NAME;raw=c.serialize_home(self.sample());home.write_bytes(raw)
            backup=c.apply_home(home,Path(folder)/'backups',c.sha256(raw),planner=c.plan_poster_style)
            home.write_bytes(home.read_bytes()+b'\n')
            with self.assertRaises(RuntimeError):c.restore_home(home,backup)

    def test_cleanup_still_available_after_style(self):
        c=self.core
        planned=c.plan_poster_style(self.sample())
        candidates=c.cleanup_candidates(planned)
        self.assertEqual([x['label'] for i,x in candidates],['Your Movie Watchlist','Recommended Movies for You'])
        cleaned=c.plan_cleanup(planned)
        self.assertEqual(len(cleaned),len(planned)-2)
        self.assertEqual([r['widget_style'] for r in cleaned[1:4]],['Poster']*3)
        self.assertEqual(cleaned[4]['label'],'Up Next Episodes')

    def test_installer_maintains_feed_and_artwork(self):
        with ZipFile(ZIP) as z:
            ui=z.read(ID+'/default.py').decode()
            self.assertIn("'poster_apply'",ui)
            self.assertIn("'poster_preview'",ui)
            self.assertIn("planner=core.plan_poster_style",ui)
            self.assertIn("'override_landscape'",ui)
            self.assertIn('sync_becauseyouwatched',z.read(ID+'/core.py').decode())
            self.assertEqual(len(z.namelist()),4)
            self.assertIn('version="0.1.3"',z.read(ID+'/addon.xml').decode())

if __name__=='__main__':unittest.main(verbosity=2)
