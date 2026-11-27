import unittest
from unittest.mock import Mock
from continue_watching_playback import Viewing, playing_key

class PlaybackTests(unittest.TestCase):
    def test_identity(self):
        tag = Mock()
        tag.getMediaType.return_value = 'episode'
        tag.getUniqueID.side_effect = lambda k: {'tmdb':'99','tvshow.tmdb':'12'}.get(k,'')
        self.assertEqual(playing_key(tag),'tv:12')
        tag.getUniqueID.side_effect = lambda k: '99' if k == 'tmdb' else ''
        self.assertIsNone(playing_key(tag))
        tag.getMediaType.return_value = 'movie'
        self.assertEqual(playing_key(tag),'movie:99')

    def test_actual_viewing(self):
        store = Mock()
        store.read.return_value = {'movie:12':{}}
        v = Viewing()
        for t in range(11):
            v.sample('Cricky','movie:12','file',100+t,t,1,store)
        store.viewed.assert_called_once_with('movie:12',verified=True)
        v.sample('Cricky','movie:12','file',111,11,1,store)
        self.assertEqual(store.viewed.call_count,1)

    def test_seek_pause_switch(self):
        store = Mock()
        v = Viewing()
        for t in range(30):
            v.sample('Cricky' if t<8 else 'Ricky','tv:12','file',100*t,t,1,store)
        store.viewed.assert_not_called()
        for t in range(30,60):
            v.sample('Ricky','tv:12','file',3000,t,0,store)
        store.viewed.assert_not_called()
