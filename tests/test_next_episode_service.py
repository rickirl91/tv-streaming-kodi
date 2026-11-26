import importlib.util
import sys
import unittest
from collections import deque
from pathlib import Path
from threading import Lock
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1] / "src" / "nextepisode"
sys.path.insert(0, str(ROOT))
from catalogue import verified_successor


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.current = dict(series_id="123", show="A Show", title="First",
                            season=1, episode=1, imdb="tt123")
        self.show = dict(id=123, name="A Show", number_of_seasons=2,
                         number_of_episodes=3, external_ids={"imdb_id": "tt123"},
                         seasons=[dict(season_number=0, id=1, episode_count=4),
                                  dict(season_number=1, id=2, episode_count=2),
                                  dict(season_number=2, id=3, episode_count=1)])
        self.seasons = {
            1: self.season(1, ["First", "Second"]),
            2: self.season(2, ["Third"]),
        }

    def season(self, number, names):
        return dict(id=number + 1, season_number=number, episodes=[
            dict(id=number * 100 + index, name=name, season_number=number,
                 episode_number=index, air_date="2020-01-01")
            for index, name in enumerate(names, 1)])

    def fetch(self, media, show_id, *args, **kwargs):
        if (media, show_id) == ("tv", "episode_group"):
            return self.group
        self.assertEqual((media, show_id), ("tv", "123"))
        if not args:
            return self.show
        self.assertEqual(args[0], "season")
        if len(args) > 2:
            row = self.seasons[args[1]]["episodes"][args[3] - 1]
            return dict(id=row["id"], external_ids={"imdb_id": "tt789"})
        return self.seasons[args[1]]

    def target(self):
        return verified_successor(self.fetch, self.current)

    def test_progression_transition_and_finale(self):
        self.assertEqual(self.target()["episode_id"], "123:1:2")
        self.current.update(episode=2, title="Second")
        self.assertEqual(self.target()["episode_id"], "123:2:1")
        self.current.update(season=2, episode=1, title="Third")
        self.assertIsNone(self.target())

    def test_episode_scoped_imdb_validates_only_exact_episode(self):
        self.current["imdb"] = "tt789"
        self.assertEqual(self.target()["episode_id"], "123:1:2")
        self.current["imdb"] = "tt999"
        self.assertIsNone(self.target())

    def test_unknown_or_unreleased_successor(self):
        row = self.seasons[1]["episodes"][1]
        for date in ("", "2099-12-31"):
            row["air_date"] = date
            self.assertIsNone(self.target())

    def test_verified_alternative_order(self):
        summary = dict(id="alt", group_count=1, episode_count=3)
        self.show["episode_groups"] = {"results": [summary]}
        first, second = self.seasons[1]["episodes"]
        third = self.seasons[2]["episodes"][0]
        self.group = dict(summary, groups=[dict(id="one", order=0, episodes=[
            dict(third, order=2), dict(first, order=1), dict(second, order=0)])])
        self.current["group"] = "alt"
        target = self.target()
        self.assertEqual((target["episode_id"], target["virtual_episode"]), ("123:2:1", 3))
        self.group["episode_count"] = 4
        self.assertIsNone(self.target())

    def test_incomplete_and_paginated_catalogues(self):
        self.seasons[1]["total_pages"] = 2
        self.assertIsNone(self.target())
        self.seasons[1].pop("total_pages")
        self.seasons[1]["episodes"].pop()
        self.assertIsNone(self.target())
        self.show["seasons"].pop()
        self.assertIsNone(self.target())

    def test_title_mismatch_and_duplicate_identity(self):
        self.current["title"] = "Different"
        self.assertIsNone(self.target())
        self.current["title"] = "First"
        self.seasons[1]["episodes"][1]["id"] = 101
        self.assertIsNone(self.target())


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.profile, self.playing, self.paused = "Cricky", True, False
        self.upnext, self.queued, self.enabled, self.order = False, 1, True, "default"
        self.kodi = SimpleNamespace(
            Player=object, PLAYLIST_VIDEO=1, LOGWARNING=2, executebuiltin=Mock(),
            getInfoLabel=lambda key: self.profile, getSkinDir=lambda: "skin.arctic.fuse.3",
            PlayList=lambda _: SimpleNamespace(size=lambda: self.queued),
            getCondVisibility=self.visible)
        addon = SimpleNamespace(getAddonInfo=lambda key: "/addon",
                                getSettingBool=lambda key: self.enabled,
                                getSetting=lambda key: self.order if key == "player_episode_groups"
                                else "tmdbmovies.json play_episode")
        with patch.dict(sys.modules, {
                "xbmc": self.kodi, "xbmcaddon": SimpleNamespace(Addon=lambda _: addon),
                "xbmcgui": SimpleNamespace(Window=lambda _: Mock(), WindowXMLDialog=object),
                "xbmcvfs": SimpleNamespace(translatePath=lambda _: "/profiles/" + self.profile),
        }):
            spec = importlib.util.spec_from_file_location("next_service_test", ROOT / "service.py")
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)
        self.module.Overlay = Mock(side_effect=lambda *args: Mock(choice=None))
        self.module.validate_player = Mock(return_value=True)
        self.player = Mock(events=deque(), lock=Lock())
        self.player.isPlayingVideo.side_effect = self.player.isPlaying.side_effect = lambda: self.playing
        self.player.getPlayingFile.return_value = "episode-one"
        self.player.getTime.return_value = 1680
        self.player.getTotalTime.return_value = 1800
        self.monitor = Mock()
        self.monitor.abortRequested.return_value = False
        self.service = self.module.Service(self.player, self.monitor)
        self.service.step(0)
        self.service.probe = Mock()  # Catalogue resolution tested independently.
        self.service.armed = True
        self.service.file = "episode-one"
        self.target = dict(series_id="123", season=1, episode=2, show="Show",
                           title="Second", art="")
        self.target["url"] = self.module.playback_url("123", self.target, "tmdbmovies.json")
        self.service.controller.begin(self.target)

    def test_native_service_adapter(self):
        candidate = Path(__file__).resolve().parent / "native_service_candidate.py"
        with patch.dict(sys.modules, {"xbmc": self.kodi,
                "xbmcaddon": SimpleNamespace(), "xbmcgui": SimpleNamespace(WindowXMLDialog=object),
                "xbmcvfs": SimpleNamespace()}):
            spec = importlib.util.spec_from_file_location("native_service_test", candidate)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        current = dict(series_id="1622", show="Supernatural", title="Dead in the Water",
                       season=1, episode=3, imdb="tt0713613", group="")
        with patch.object(module, "directory_successor", return_value=dict(
                season=1, episode=4, title="Phantom Traveler", episode_id="1622:1:4")) as resolver:
            target = module.resolve(current, "tmdbmovies.json")
            self.assertEqual(target["art"], "")
            query = parse_qs(urlparse(target["url"]).query)
            self.assertEqual(query["tmdb_id"], ["1622"])
            self.assertEqual(query["episode"], ["4"])
            self.assertEqual(query["player"], ["tmdbmovies.json"])
            self.assertEqual(query["allow_playlist"], ["false"])
            resolver.assert_called_once()
        with patch.object(module, "directory_successor", return_value=None):
            self.assertIsNone(module.resolve(current, "tmdbmovies.json"))

    def visible(self, condition):
        return {
            "System.AddonIsEnabled(service.upnext)": self.upnext,
            "System.AddonIsEnabled(plugin.video.themoviedb.helper)": True,
            "Player.Playing": self.playing and not self.paused,
            "Player.Paused": self.paused,
            "Window.IsVisible(fullscreenvideo)": self.playing,
        }.get(condition, False)

    def event(self, name, now):
        self.player.events.append(name)
        self.service.step(now)

    def end(self, now):
        self.player.getTime.return_value = 1799
        self.service.step(now)
        self.playing = False
        self.event("ended", now + 0.5)

    def test_pause_seek_and_threshold(self):
        self.player.getTime.return_value = 1679
        self.service.step(1)
        self.assertIsNone(self.service.overlay)
        self.player.getTime.return_value = 1680
        self.service.step(2)
        self.assertIsNotNone(self.service.overlay)
        self.paused = True
        self.service.step(3)
        self.assertIsNone(self.service.overlay)
        self.paused = False
        self.service.step(4)
        self.assertIsNotNone(self.service.overlay)
        self.player.getTime.return_value = 1400
        self.event("seek", 5)
        self.assertIsNone(self.service.overlay)
        self.kodi.executebuiltin.assert_not_called()

    def test_manual_launch_only_once_and_player_route(self):
        query = parse_qs(urlparse(self.target["url"]).query)
        self.assertEqual(query["allow_playlist"], ["false"])
        self.assertEqual(query["player"], ["tmdbmovies.json"])
        self.service.step(1)
        self.service.overlay.choice = True
        self.service.step(2)
        self.event("stopped", 2.25)
        self.event("starting", 2.5)
        self.event("started", 2.75)
        self.service.adopt(self.target, self.target)
        self.assertEqual(self.service.controller.consecutive, 1)
        self.kodi.executebuiltin.assert_called_once()

    def test_natural_end_and_duplicate_callbacks(self):
        self.end(1)
        self.kodi.executebuiltin.assert_not_called()
        self.event("ended", 3)
        self.event("ended", 4)
        self.kodi.executebuiltin.assert_called_once()

    def test_stop_error_cancel_and_profile_switch(self):
        for interruption in ("stopped", "error", "cancel", "profile", "shutdown"):
            with self.subTest(interruption=interruption):
                self.setUp()
                self.end(1)
                if interruption == "cancel":
                    self.service.overlay.choice = False
                elif interruption == "profile":
                    self.profile = "Other"
                elif interruption == "shutdown":
                    self.monitor.abortRequested.return_value = True
                else:
                    self.player.events.append(interruption)
                self.service.step(3)
                self.kodi.executebuiltin.assert_not_called()

    def test_still_watching_decline_timeout_or_single_continuation(self):
        for choice in (False, None, True):
            with self.subTest(choice=choice):
                self.setUp()
                self.service.controller.consecutive = 2
                self.end(1)
                self.service.step(3)
                self.kodi.executebuiltin.assert_not_called()
                self.service.overlay.choice = choice
                self.service.step(4)
                self.service.step(49)
                self.assertEqual(self.kodi.executebuiltin.call_count, int(choice is True))
                self.assertEqual(self.service.controller.consecutive, 0)

    def test_conflicting_autoplay_and_route_changes(self):
        self.upnext = True
        self.assertIsNone(self.module.active_route())
        self.upnext, self.queued = False, 2
        self.assertIsNone(self.module.active_route())
        self.queued, self.order = 1, "select"
        self.assertIsNone(self.module.active_route())
        self.order = "default"
        self.end(1)
        self.module.validate_player.return_value = False
        self.service.step(3)
        self.kodi.executebuiltin.assert_not_called()
