import unittest
from unittest.mock import Mock
from continue_watching_feed import fetch_visible, dismissal_key, SOURCE

class FeedTests(unittest.TestCase):
    def test_verified_filter(self):
        movie = {'file': 'plugin://plugin.video.themoviedb.helper/?tmdb_type=movie&tmdb_id=12', 'uniqueid': {'tmdb': '12'}, 'resume': {'position': 300, 'total': 6000}}
        episode = {'file': 'plugin://plugin.video.themoviedb.helper/?tmdb_type=tv&tmdb_id=12&season=1&episode=2', 'uniqueid': {'tvshow.tmdb': '12'}, 'art': {'poster': 'original'}}
        conflict = dict(movie, uniqueid={'tmdb': '13'})
        rpc = Mock(return_value={'files': [movie, episode, conflict]})
        store = Mock()
        store.read.return_value = {'movie:12': {}}
        result = fetch_visible(rpc, store)
        self.assertEqual(result, [episode, conflict])
        self.assertIs(result[0], episode)
        self.assertEqual(dismissal_key(episode), 'tv:12')
        self.assertIsNone(dismissal_key(conflict))
        self.assertEqual(rpc.call_args.args[1]['directory'], SOURCE)
        store.read.side_effect = OSError('unavailable')
        self.assertEqual(fetch_visible(rpc, store), [movie, episode, conflict])

    def test_invalid_response(self):
        with self.assertRaises(ValueError):
            fetch_visible(Mock(return_value={'error': 'unavailable'}), Mock())
