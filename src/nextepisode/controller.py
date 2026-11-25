"""Playback decisions only; no Kodi calls or implicit playback."""
class Controller:
    def __init__(self):
        self.consecutive = 0
        self.reset()

    def reset(self):
        self.target = None
        self.offered = False
        self.cancelled = False
        self.ended = False

    def begin(self, target, continuation=False):
        if not continuation:
            self.consecutive = 0
        self.reset()
        self.target = target

    def tick(self, elapsed, duration, speed):
        if not self.target or self.cancelled or self.offered or self.ended:
            return None
        if speed != 1 or duration <= 0 or elapsed <= 0 or elapsed >= duration:
            return None
        threshold = 120 if duration >= 1800 else 60
        if duration - elapsed <= threshold:
            self.offered = True
            return "still_watching" if self.consecutive >= 2 else "offer"

    def cancel(self):
        self.cancelled = True

    def advance(self, confirmed=False):
        if not self.target or self.cancelled or self.ended or not self.offered:
            return None
        if self.consecutive >= 2 and not confirmed:
            return None
        self.ended = True
        self.consecutive = 0 if self.consecutive >= 2 else self.consecutive + 1
        return self.target

    def finish(self, natural):
        if not natural:
            self.cancel()
            self.ended = True
            return None
        return self.advance()
