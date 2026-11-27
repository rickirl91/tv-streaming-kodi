import unittest
from continue_watching_candidate import identity, dismiss, restore, filter_rows, subsequent_viewing

def row(media, id, extra=''):
    return {'file': 'plugin://plugin.video.themoviedb.helper/?tmdb_type={}&tmdb_id={}{}'.format(media,id,extra), 'resume': 123}

class DismissalTests(unittest.TestCase):
    def test_movie_series_collision(self):
        rows = [row('movie', 12), row('tv', 12, '&season=1&episode=2')]
        self.assertEqual(filter_rows(rows, dismiss({}, 'movie:12', 'Movie')), rows[1:])
    def test_series_all_episodes(self):
        rows = [row('tv', 12, '&season=1&episode=2'), row('tv',12,'&season=2&episode=1'), row('tv',13)]
        self.assertEqual(filter_rows(rows, dismiss({}, 'tv:12','Show')), rows[2:])
    def test_restore_and_verified_viewing(self):
        hidden = dismiss({}, 'tv:12', 'Show')
        self.assertEqual(subsequent_viewing(hidden,'tv:12'), hidden)
        self.assertEqual(subsequent_viewing(hidden,'tv:12',verified=True), {})
        self.assertEqual(restore(hidden,'tv:12'), {})
        self.assertIn('tv:12', hidden)
    def test_unknown_identity_preserved(self):
        rows = [{'file':'plugin://other/?tmdb_type=tv&tmdb_id=12'}, row('tv', '12&tmdb_id=13')]
        self.assertEqual(filter_rows(rows, dismiss({}, 'tv:12','Show')), rows)
        self.assertIsNone(identity(rows[1]['file']))
    def test_invalid_dismissal(self):
        with self.assertRaises(ValueError):
            dismiss({}, 'tv:0','Invalid')
