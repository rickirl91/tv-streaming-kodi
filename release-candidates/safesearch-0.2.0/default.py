"""Native Kodi Search launcher. Never writes skin or profile configuration."""
import sys
import xbmc
import xbmcgui
import core

TITLE = 'Cricky Safe Search'


def launch():
    if not core.allowed_profile(xbmc.getInfoLabel('System.ProfileName')):
        xbmcgui.Dialog().ok(TITLE, 'This test release is restricted to Cricky.')
        return
    if xbmc.Player().isPlaying():
        return
    keyboard = xbmc.Keyboard('', 'Search movies and TV shows')
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return
    if not core.allowed_profile(xbmc.getInfoLabel('System.ProfileName')):
        return
    if xbmc.Player().isPlaying():
        return
    command = core.search_command(keyboard.getText())
    if command:
        xbmc.executebuiltin(command)


def main():
    if sys.argv[1:] not in ([], ['search']):
        return
    try:
        launch()
    except Exception as exc:
        xbmc.log('[Cricky Safe Search] ' + str(exc), xbmc.LOGERROR)
        xbmcgui.Dialog().ok(TITLE, 'Search could not be opened. See Kodi log.')


if __name__ == '__main__':
    main()
