import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'release-candidates'/'widget-performance-001'))
import widget_cache as c

class CacheTests(unittest.TestCase):
    def test_hit_and_expiry(self):
        with tempfile.TemporaryDirectory() as root:
            calls=[]
            def fetch():
                calls.append(1)
                return [{'file':'plugin://example','art':{'poster':'poster'},'playcount':1}]
            with patch.object(c.time,'time',return_value=1000):
                a=c.cached(root,'uri',fetch)
                self.assertEqual(c.cached(root,'uri',fetch),a)
                self.assertEqual(len(calls),1)
            with patch.object(c.time,'time',return_value=1300):
                self.assertEqual(c.cached(root,'uri',fetch),a)
            self.assertEqual(len(calls),2)
    def test_empty_failure_and_profile_guard(self):
        with tempfile.TemporaryDirectory() as root:
            calls=[]
            def empty():
                calls.append(1)
                return []
            c.cached(root,'uri',empty)
            c.cached(root,'uri',empty)
            self.assertEqual(len(calls),2)
            def bad():
                raise RuntimeError('upstream')
            with self.assertRaises(RuntimeError):
                c.cached(root,'uri',bad)
            c.cached(root,'uri',lambda:[{'x':1}])
            self.assertEqual(c.cached(root,'uri',lambda:[{'x':2}],lambda:False),[{'x':2}])
    def test_profile_and_uri_isolation(self):
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            self.assertEqual(c.cached(a,'a',lambda:[{'x':1}]),[{'x':1}])
            self.assertEqual(c.cached(b,'a',lambda:[{'x':2}]),[{'x':2}])
            self.assertEqual(c.cached(a,'b',lambda:[{'x':3}]),[{'x':3}])
    def test_corruption_and_size(self):
        with tempfile.TemporaryDirectory() as root:
            c.cached(root,'uri',lambda:[{'x':1}])
            path=next(Path(root).rglob('*.json'))
            path.write_text('{broken')
            self.assertEqual(c.cached(root,'uri',lambda:[{'x':2}]),[{'x':2}])
            with patch.object(c,'MAX_BYTES',20):
                self.assertEqual(c.cached(root,'uri',lambda:[{'x':'a'*100}]),[{'x':'a'*100}])
    def test_cache_is_bounded(self):
        with tempfile.TemporaryDirectory() as root:
            for i in range(130):
                c.cached(root,str(i),lambda:[{'x':i}])
            self.assertLessEqual(len(list(Path(root).rglob('*.json'))),c.SLOTS)
            self.assertLessEqual(len(list(Path(root).rglob('*.lock'))),c.SLOTS)

if __name__ == '__main__':
    unittest.main()
