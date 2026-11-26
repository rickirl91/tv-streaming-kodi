"""Small non-modal controller dialog over fullscreen video."""
import xbmcgui


class Overlay(xbmcgui.WindowXMLDialog):
    def __init__(self, *args):
        self.choice = None
        self.ready = False

    def onClick(self, control):
        if control in (10, 11):
            self.choice = control == 10

    def onAction(self, action):
        if action.getId() in (9, 10, 92):
            self.choice = False

    def onInit(self):
        self.ready = True
        self.update(*self.content)

    def display(self, *content):
        self.content = content
        if self.ready:
            self.update(*content)

    def update(self, target, confirmation, remaining):
        self.getControl(1).setLabel("Still Watching?" if confirmation else "Next Episode")
        self.getControl(2).setLabel(target["show"])
        self.getControl(3).setLabel("S{:02d} E{:02d}  •  {}".format(
            target["season"], target["episode"], target["title"]))
        self.getControl(4).setLabel(
            "Waiting for confirmation" if remaining is None else
            "{}:{:02d} remaining".format(*divmod(remaining, 60)))
        if getattr(self, "art", None) != target["art"]:
            self.art = target["art"]
            self.getControl(5).setImage(self.art)
        self.getControl(10).setLabel("Continue Watching" if confirmation else "Next Episode")
