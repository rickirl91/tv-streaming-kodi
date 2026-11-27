import unittest
from unittest.mock import Mock
from continue_watching_render import render
from continue_watching_action import remove

ROW = {'file':'plugin://plugin.video.themoviedb.helper/?info=play&tmdb_type=tv&tmdb_id=12&season=1&episode=2','filetype':'file','uniqueid':{'tvshow.tmdb':'12'},'title':'Episode','showtitle':'Show','season':1,'episode':2,'mediatype':'episode','art':{'poster':'native'},'resume':{'position':300,'total':2400}}

class RenderTests(unittest.TestCase):
    def test_native_metadata(self):
        gui, plugin, command = Mock(), Mock(), Mock(return_value='dismiss')
        item = render(ROW, gui, plugin, 1, command)
        item.getVideoInfoTag().setResumePoint.assert_called_once_with(300.,2400.)
        item.setArt.assert_called_once_with(ROW['art'])
        item.addContextMenuItems.assert_called_once_with([('Remove from Continue Watching','dismiss')])
        command.assert_called_once_with('tv:12')
        plugin.addDirectoryItem.assert_called_once_with(1,ROW['file'],item,isFolder=False)
    def test_action(self):
        store, refresh = Mock(), Mock()
        store.read.return_value = {}
        args = dict(profile='Cricky',current_profile=lambda:'Cricky',rpc=Mock(return_value={'files':[ROW]}),store=store,refresh=refresh)
        self.assertFalse(remove('movie:12',**args))
        store.hide.assert_not_called()
        self.assertTrue(remove('tv:12',**args))
        store.hide.assert_called_once_with('tv:12','Show')
        refresh.assert_called_once()
        args['current_profile'] = lambda:'Ricky'
        self.assertFalse(remove('tv:12',**args))
