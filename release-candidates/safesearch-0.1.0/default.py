"""Explicit opt-in patch, native search and byte-exact guarded rollback."""
import os
import sys
import tempfile
from pathlib import Path
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import core

DIALOG = xbmcgui.Dialog()
TITLE = 'Cricky Safe Search'


def require_profile():
    if xbmc.getInfoLabel('System.ProfileName').strip().casefold() != 'cricky':
        raise RuntimeError('Cricky profile required. Nothing changed.')


def require_idle_skin():
    require_profile()
    if xbmc.Player().isPlaying():
        raise RuntimeError('Stop playback first.')
    if xbmc.getSkinDir() != core.SKIN_ID:
        raise RuntimeError('Switch to Arctic Fuse 3 first.')
    skin = xbmcaddon.Addon(core.SKIN_ID)
    if skin.getAddonInfo('version') != core.SKIN_VERSION:
        raise RuntimeError('Unsupported Arctic Fuse 3 version. Nothing changed.')
    return Path(xbmcvfs.translatePath(skin.getAddonInfo('path'))) / '1080i' / 'Includes_Home.xml'


def backup_path():
    return (Path(xbmcvfs.translatePath('special://profile/')) / 'addon_data'
            / core.ADDON_ID / 'backups' / ('Includes_Home-' + core.SKIN_VERSION + '.xml'))


def atomic_write(path, data, expected=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.safesearch-', suffix='.tmp', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        if Path(tmp).read_bytes() != data:
            raise RuntimeError('Temporary file verification failed.')
        if expected is not None and path.read_bytes() != expected:
            raise RuntimeError('File changed during confirmation. Nothing overwritten.')
        os.replace(tmp, path)
        if path.read_bytes() != data:
            raise RuntimeError('Saved file verification failed.')
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def apply():
    path = require_idle_skin()
    old = path.read_bytes()
    backup = backup_path()
    if core.VARIABLE.encode('ascii') in old:
        if backup.is_file() and core.patch(backup.read_bytes()) == old:
            DIALOG.ok(TITLE, 'Already applied. Fully restart Kodi if needed.')
            return
        raise RuntimeError('An unknown or modified Search patch exists. Nothing changed.')
    new = core.patch(old)
    if backup.exists() and backup.read_bytes() != old:
        raise RuntimeError('An earlier backup differs from the installed file. Nothing changed.')
    if not DIALOG.yesno(TITLE, 'Replace only the Home Search action for Cricky? The shared skin XML is backed up; all other profiles retain their original Search route. Restart required.'):
        return
    if require_idle_skin() != path or path.read_bytes() != old:
        raise RuntimeError('Skin or profile changed. Nothing changed.')
    if not backup.exists():
        atomic_write(backup, old)
    if backup.read_bytes() != old:
        raise RuntimeError('Backup verification failed.')
    atomic_write(path, new, expected=old)
    DIALOG.ok(TITLE, 'Safe Search applied. Fully quit and restart Kodi. Keep this add-on installed until you restore the original action.')


def restore():
    path = require_idle_skin()
    current = path.read_bytes()
    if core.VARIABLE.encode('ascii') not in current:
        DIALOG.ok(TITLE, 'No Safe Search patch detected. Nothing changed.')
        return
    backup = backup_path()
    if not backup.is_file():
        raise RuntimeError('Verified original backup not found. Nothing changed.')
    original = backup.read_bytes()
    if core.patch(original) != current:
        raise RuntimeError('Skin file has other edits. Refusing to overwrite them.')
    if not DIALOG.yesno(TITLE, 'Restore the exact original Search skin file? Fully restart Kodi afterwards.'):
        return
    if require_idle_skin() != path or backup.read_bytes() != original:
        raise RuntimeError('Skin, profile or backup changed. Nothing changed.')
    atomic_write(path, original, expected=current)
    DIALOG.ok(TITLE, 'Original skin file restored exactly. Fully quit and restart Kodi.')


def search():
    require_profile()
    if xbmc.Player().isPlaying():
        return
    kb = xbmc.Keyboard('', 'Search movies and TV shows')
    kb.doModal()
    if not kb.isConfirmed():
        return
    require_profile()
    command = core.search_command(kb.getText())
    if command:
        xbmc.executebuiltin(command)


def main():
    try:
        require_profile()
        if len(sys.argv) > 1:
            if sys.argv[1:] != ['search']:
                raise RuntimeError('Unknown command.')
            search()
            return
        selected = DIALOG.select(TITLE, ['Test native Search (no changes)', 'Apply safe Home Search', 'Restore original Home Search'])
        if selected == 0:
            search()
        elif selected == 1:
            apply()
        elif selected == 2:
            restore()
    except Exception as exc:
        xbmc.log('[Cricky Safe Search] ' + str(exc), xbmc.LOGERROR)
        DIALOG.ok(TITLE, str(exc))


if __name__ == '__main__':
    main()
