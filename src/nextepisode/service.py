"""Cricky playback adapter. Kodi callbacks enqueue; the service owns decisions."""
import math
import json
import re
from collections import deque
from threading import Lock, Thread
from time import monotonic

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from catalogue import playback_url, verified_successor
from controller import Controller
from diagnostic import snapshot
from overlay import Overlay

HELPER = "plugin.video.themoviedb.helper"
SERVICE = "service.tvstreaming.nextepisode"


class Player(xbmc.Player):
    def __init__(self):
        super().__init__()
        self.events = deque()
        self.lock = Lock()

    def emit(self, kind):
        with self.lock:
            self.events.append(kind)

    def onPlayBackStarted(self):
        self.emit("starting")

    def onAVStarted(self):
        self.emit("started")

    def onPlayBackEnded(self):
        self.emit("ended")

    def onPlayBackStopped(self):
        self.emit("stopped")

    def onPlayBackError(self):
        self.emit("error")

    def onPlayBackSeek(self, time, seekOffset):
        self.emit("seek")


def playback_identity(player):
    tag = player.getVideoInfoTag()
    parent = tag.getUniqueID("tvshow.tmdb")
    values = {
        "show": xbmc.getInfoLabel("VideoPlayer.TVShowTitle") or tag.getTVShowTitle(),
        "title": xbmc.getInfoLabel("VideoPlayer.Title") or tag.getTitle(),
        "series_id": parent or tag.getUniqueID("tmdb"),
        "parent_verified": bool(parent),
        "group": tag.getUniqueID("group_tmdb"),
        "imdb": tag.getUniqueID("imdb") or xbmc.getInfoLabel("VideoPlayer.IMDBNumber"),
    }
    for field, number in (("season", tag.getSeason()), ("episode", tag.getEpisode())):
        label = xbmc.getInfoLabel("VideoPlayer." + field.capitalize())
        if number < 0 and label.isdecimal():
            number = int(label)
        if number < 1 or (label.isdecimal() and number != int(label)):
            return None
        values[field] = number
    if not values["show"] or not values["title"]:
        return None
    return values


def resolve(current, filename, report=lambda reason: None):
    from tmdbhelper_lib.api.tmdb.api import TMDb

    fetch = TMDb().get_response_json
    if not current["parent_verified"]:
        imdb = current["imdb"] or ""
        if re.fullmatch(r"tt[0-9]+", imdb):
            # IMDb lookup disambiguates tags whose TMDb ID is episode scoped.
            found = fetch("find", imdb, external_source="imdb_id") or {}
            matches = (
                [row["id"] for row in found.get("tv_results", [])]
                + [row["show_id"] for row in found.get("tv_episode_results", [])
                   if (row.get("season_number"), row.get("episode_number")) ==
                   (current["season"], current["episode"])]
            )
            if len(matches) > 1:
                return None
            if matches:
                current["series_id"] = str(matches[0])
    if not re.fullmatch(r"[1-9][0-9]*", current["series_id"] or ""):
        return None
    next_episode = verified_successor(fetch, current, report)
    if next_episode:
        next_episode.update(show=current["show"], series_id=current["series_id"],
                            group=current.get("group") or None,
                            url=playback_url(current["series_id"], next_episode, filename))
    return next_episode


def active_route():
    if (xbmc.getInfoLabel("System.ProfileName").strip().casefold() != "cricky"
            or xbmc.getSkinDir() != "skin.arctic.fuse.3"
            or not xbmcaddon.Addon(SERVICE).getSettingBool("exclusive_autoplay")
            or xbmc.getCondVisibility("System.AddonIsEnabled(service.upnext)")
            or not xbmc.getCondVisibility(f"System.AddonIsEnabled({HELPER})")
            or xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size() > 1):
        return None
    helper = xbmcaddon.Addon(HELPER)
    order = helper.getSetting("player_episode_groups")
    if order not in ("default", "group"):
        return None
    setting = helper.getSetting("default_player_episodes")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+\.json play_episode", setting):
        return None
    return xbmcvfs.translatePath("special://profile/"), setting.split()[0], order


def validate_player(filename, order):
    from tmdbhelper_lib.player.config.files import PlayerFiles
    player = PlayerFiles().dictionary.get(filename) or {}
    return (bool(player.get("play_episode"))
            and str(player.get("make_playlist", False)).lower() == "false"
            and (player.get("episode_groups") or order) == order)


def future_matches(target, identity):
    if not identity or (target["season"], target["episode"]) != (
            identity["season"], identity["episode"]):
        return False
    # A continuation is counted only after the catalogue validates the series.
    return (target["series_id"] == identity["series_id"]
            and target.get("group") == (identity.get("group") or None))


class Service:
    def __init__(self, player, monitor):
        self.player = player
        self.monitor = monitor
        self.controller = Controller()
        self.pending = None
        self.route = None
        self.overlay = None
        self.worker = None
        self.result = None
        self.generation = 0
        self.armed = False
        self.file = None
        self.ending = None
        self.confirm_until = None
        self.last_remaining = None
        self.next_probe = 0
        self.attempts = 0
        self.path = xbmcaddon.Addon(SERVICE).getAddonInfo("path")
        self.diagnostic_window = xbmcgui.Window(10000)

    def close(self):
        if self.overlay:
            self.overlay.close()
            self.overlay = None
        self.controller.hide()

    def reset(self, preserve_pending=False):
        self.close()
        self.generation += 1
        self.controller.begin(None, continuation=preserve_pending)
        if not preserve_pending:
            self.pending = None
        self.armed = False
        self.file = None
        self.ending = self.confirm_until = self.last_remaining = None
        self.next_probe = 0
        self.attempts = 0

    def read_catalogue(self, generation, current, filename, order):
        target = None
        status = 'player_or_order_rejected'
        try:
            group = current["group"] or ""
            if (validate_player(filename, order) and
                    (order == "default" and not group or
                     order == "group" and re.fullmatch(r"[A-Za-z0-9_-]{1,64}", group))):
                reasons = []
                target = resolve(current, filename, reasons.append)
                status = 'successor_verified' if target else (reasons[-1] if reasons else 'catalogue_rejected_or_no_successor')
        except Exception as exc:
            status = 'catalogue_exception:' + type(exc).__name__
            xbmc.log("[TV Streaming Next Episode] Catalogue or player unavailable", xbmc.LOGWARNING)
        self.result = generation, current, target, status

    def probe(self, now):
        if self.worker and self.worker.is_alive():
            return
        if self.result is not None:
            generation, identity, target, status = self.result
            self.result = None
            if generation == self.generation and self.armed:
                self.record_status(status)
                if target or status == 'no_eligible_successor' or self.attempts >= 3:
                    self.adopt(identity, target)
                else:
                    self.next_probe = now + 10
                return
        if not self.armed or now < self.next_probe or not self.player.isPlayingVideo():
            return
        self.next_probe = now + 2
        if self.file is None:
            self.file = self.player.getPlayingFile()
        try:
            self.diagnostic_window.setProperty("tvstreaming.nextdiagnostic", snapshot())
        except Exception:
            pass
        current = playback_identity(self.player)
        if not current or not self.file:
            self.record_status('metadata_not_ready')
            return
        self.attempts += 1
        self.record_status('catalogue_pending')
        self.worker = Thread(target=self.read_catalogue, daemon=True,
                             args=(self.generation, current, *self.route[1:]))
        self.worker.start()
        self.next_probe = math.inf

    def record_status(self, status, section='resolution', **details):
        try:
            data = json.loads(self.diagnostic_window.getProperty('tvstreaming.nextdiagnostic') or '{}')
            data[section] = {'status': status, 'attempt': self.attempts, **details}
            self.diagnostic_window.setProperty('tvstreaming.nextdiagnostic', json.dumps(data))
        except Exception:
            pass

    def adopt(self, identity, target):
        # Verify the actual successor AV start before retaining the streak.
        if self.pending:
            expected, _, _ = self.pending
            continuation = bool(target and future_matches(expected, identity))
            self.pending = None
        else:
            continuation = False
        self.controller.begin(target, continuation)

    def launch(self, target, now, natural):
        if not self.route or not validate_player(*self.route[1:]):
            self.reset()
            return
        self.close()
        with self.player.lock:
            valid = (not self.player.isPlaying() if natural else
                     self.player.isPlayingVideo() and self.file == self.player.getPlayingFile())
            if (valid and not self.player.events and not self.monitor.abortRequested()
                    and active_route() == self.route):
                self.pending = target, now + 90, not natural
                self.armed = False
                self.ending = self.confirm_until = None
                # Kodi posts this builtin asynchronously with wait=False.
                xbmc.executebuiltin("PlayMedia({})".format(target["url"]), False)
                return
        self.reset()

    def events(self, now):
        with self.player.lock:
            events = tuple(self.player.events)
            self.player.events.clear()
        for kind in events:
            if kind in ("starting", "started"):
                if kind == "started" and self.armed:
                    continue
                self.reset(preserve_pending=bool(self.pending))
                self.armed = kind == "started"
                if self.armed:
                    self.next_probe = now + 5
            elif kind == "stopped" and self.pending and self.pending[2] and not self.armed:
                # Kodi may stop the replaced stream as PlayMedia opens the next.
                self.pending = self.pending[0], self.pending[1], False
            elif kind in ("stopped", "error"):
                self.reset()
            elif kind == "seek":
                self.last_remaining = None
                self.close()
            elif kind == "ended" and self.armed and self.ending is None:
                self.armed = False
                # Reject stale/misattributed end events and give Kodi time to
                # deliver a queued stop/error or start its own playlist item.
                if self.last_remaining is not None and self.last_remaining <= 8:
                    self.ending = now + 1
                else:
                    self.reset()

    def show(self, target, confirmation, remaining):
        if not self.overlay:
            self.overlay = Overlay("NextEpisode.xml", self.path, "Default", "1080i")
            self.overlay.display(target, confirmation, remaining)
            self.overlay.show()
            self.record_status("shown", "overlay")
        else:
            self.overlay.display(target, confirmation, remaining)

    def choice(self, now, natural):
        if not self.overlay or self.overlay.choice is None:
            return False
        if not self.overlay.choice:
            self.close()
            self.controller.cancel()
            self.confirm_until = None
        else:
            target = self.controller.advance(confirmed=True)
            if target:
                self.launch(target, now, natural)
        return True

    def step(self, now):
        route = active_route()
        if route != self.route or not route:
            self.reset()
            self.route = route
            with self.player.lock:
                self.player.events.clear()
            return
        if self.pending and now >= self.pending[1]:
            self.pending = None
            self.controller.consecutive = 0
        # Honour Cancel even when the end callback was delivered in this poll.
        if self.overlay and self.overlay.choice is False:
            self.choice(now, natural=False)
        self.events(now)
        if self.ending is not None:
            if now < self.ending:
                return
            self.ending = None
            if self.player.isPlaying() or self.controller.cancelled:
                self.reset()
                return
            if self.overlay and self.overlay.choice is True:
                self.choice(now, natural=True)
                return
            target = self.controller.finish(True)
            if target:
                self.launch(target, now, natural=True)
            elif self.controller.target and self.controller.consecutive >= 2:
                self.confirm_until = now + 45
                self.show(self.controller.target, True, None)
            return
        if self.confirm_until is not None:
            if now >= self.confirm_until or self.player.isPlaying():
                self.reset()
            else:
                self.choice(now, natural=True)
            return
        if not self.armed:
            return
        self.probe(now)
        if not self.player.isPlayingVideo():
            return
        if self.file and self.file != self.player.getPlayingFile():
            self.reset()
            return
        elapsed, duration = self.player.getTime(), self.player.getTotalTime()
        remaining = max(0, duration - elapsed)
        normal_speed = (xbmc.getCondVisibility("Player.Playing")
                        and not xbmc.getCondVisibility("Player.Paused")
                        and not xbmc.getCondVisibility("Player.Forwarding")
                        and not xbmc.getCondVisibility("Player.Rewinding"))
        self.last_remaining = remaining if normal_speed and duration > 0 else None
        threshold = 120 if duration >= 1800 else 60
        fullscreen = xbmc.getCondVisibility("Window.IsVisible(fullscreenvideo)")
        if remaining <= threshold:
            self.record_status("threshold_reached", "playback", remaining=round(remaining), normal_speed=normal_speed, fullscreen=fullscreen, target_verified=bool(self.controller.target))
        if not normal_speed or remaining > threshold or not fullscreen:
            self.close()
            return
        if self.choice(now, natural=False):
            return
        offer = self.controller.tick(elapsed, duration, int(normal_speed))
        if offer or self.overlay:
            self.show(self.controller.target, self.controller.consecutive >= 2,
                      math.ceil(remaining))


def run():
    player, monitor = Player(), xbmc.Monitor()
    service = Service(player, monitor)
    try:
        while not monitor.abortRequested():
            try:
                service.step(monotonic())
            except Exception as exc:
                service.record_status(type(exc).__name__, "service_error")
                service.reset()
                xbmc.log("[TV Streaming Next Episode] Playback state unavailable", xbmc.LOGWARNING)
            if monitor.waitForAbort(0.25):
                break
    finally:
        service.reset()
        xbmcgui.Window(10000).clearProperty("tvstreaming.nextdiagnostic")


if __name__ == "__main__":
    run()
