"""Independent candidate monitor logic; no changes to Next Episode service."""
import re
import math

def playing_key(tag):
    media = tag.getMediaType()
    if media == 'movie':
        value = tag.getUniqueID('tmdb')
        prefix = 'movie'
    elif media == 'episode':
        value = tag.getUniqueID('tvshow.tmdb')
        prefix = 'tv'
    else:
        return None
    if not isinstance(value, str) or not re.fullmatch(r'[1-9][0-9]*', value):
        return None
    return prefix + ':' + value

class Viewing:
    def __init__(self):
        self.reset()

    def reset(self):
        self.previous = None
        self.elapsed = 0
        self.done = False

    def sample(self, profile, key, file, position, clock, speed, store):
        if not profile or not key or not file or speed != 1 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in (position,clock)):
            self.reset()
            return False
        session = (profile,key,file)
        previous = self.previous
        self.previous = (session,position,clock)
        if not previous or previous[0] != session:
            self.elapsed = 0
            self.done = False
            return False
        dt = clock - previous[2]
        dp = position - previous[1]
        if not (0 < dt <= 5 and 0 < dp <= dt + 0.5):
            self.elapsed = 0
            return False
        self.elapsed += min(dp,dt)
        if self.elapsed >= 10 and not self.done:
            if key in store.read():
                store.viewed(key,verified=True)
                self.done = True
                return True
            self.done = True
        return False
