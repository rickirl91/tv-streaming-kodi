import unittest
from unittest.mock import Mock
from continue_watching_widget import plan_widget, refresh, SOURCE, WIDGET, PROPERTY

class WidgetTests(unittest.TestCase):
    def test_only_path_changes(self):
        rows = [{'label':'Continue Watching','path':SOURCE,'widget_style':'Poster'}, {'label':'Your AI Suggestions','path':'native'}]
        result = plan_widget(rows)
        self.assertEqual(result[0],dict(rows[0],path=WIDGET))
        self.assertIs(result[1],rows[1])
        self.assertEqual(plan_widget(result,False),rows)
        self.assertIs(plan_widget(result),result)
    def test_unexpected_source(self):
        with self.assertRaises(ValueError):
            plan_widget([{'label':'Continue Watching','path':'other'}])
    def test_refresh(self):
        gui = Mock()
        refresh(gui)
        refresh(gui)
        calls = gui.Window.return_value.setProperty.call_args_list
        self.assertEqual(calls[0].args[0],PROPERTY)
        self.assertNotEqual(calls[0].args[1],calls[1].args[1])
