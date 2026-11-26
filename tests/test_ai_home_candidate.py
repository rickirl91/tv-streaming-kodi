import unittest
import copy
from ai_home_candidate import plan_ai_suggestions, widget_path, LABELS, AI_PATH

class AIHomeTests(unittest.TestCase):
    def setUp(self):
        self.original = [dict(label='Continue Watching', path='existing', custom=True)]
        self.original += [dict(label=label, path=widget_path(kind), widget_style='Poster')
                          for kind, label, _ in LABELS]
        self.original.append(dict(label='Trending', path='existing-trending'))

    def test_exact_insertion(self):
        before = copy.deepcopy(self.original)
        result = plan_ai_suggestions(self.original)
        self.assertEqual(result[1]['path'], AI_PATH)
        self.assertEqual(result[1]['widget_style'], 'Poster')
        self.assertEqual(result[:1] + result[2:], before)
        self.assertEqual(self.original, before)

    def test_idempotent(self):
        result = plan_ai_suggestions(self.original)
        self.assertEqual(plan_ai_suggestions(result), result)

    def test_conflict(self):
        self.original.append(dict(label='Your AI Suggestions', path='unexpected'))
        with self.assertRaises(ValueError):
            plan_ai_suggestions(self.original)

    def test_wrong_layout(self):
        self.original[1]['path'] = 'unexpected'
        with self.assertRaises(ValueError):
            plan_ai_suggestions(self.original)
