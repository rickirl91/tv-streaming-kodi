import xbmc
import xbmcvfs
import core
def root():
    return core.verify(xbmc.getInfoLabel('System.ProfileName'),xbmc.getSkinDir(),
        xbmcvfs.translatePath('special://profile/'),xbmcvfs.translatePath('special://masterprofile/'))
