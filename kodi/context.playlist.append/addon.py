import os
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

def log(msg):
    xbmc.log(str(msg), xbmc.LOGDEBUG)

def write_playlist(folder, playlist, media, mode):
    if not folder:
        folder_list = ['music', 'video']
        result = xbmcgui.Dialog().select('Select a playlist folder', folder_list)
        if result > -1:
            folder = folder_list[result]
    log('Folder: {0}'.format(folder))
    if mode == 'w':
        playlist_name = xbmcgui.Dialog().input('Enter the playlist name', type=xbmcgui.INPUT_ALPHANUM)
        if len(playlist_name) > 1:
            playlist = xbmc.translatePath(os.path.join('special://home/userdata/playlists/{0}'.format(folder), '{0}.m3u'.format(playlist_name)))
        else:
            return
        media = '#EXTM3U\n{0}'.format(media)
    else:
        playlist = xbmc.translatePath(os.path.join('special://home/userdata/playlists/{0}'.format(folder), playlist))
    log('Path: {0}'.format(playlist))
    try:
        with open(playlist, mode) as f:
            f.write(media)
        log('Added: {0}'.format(media))
        return True
    except Exception as e:
        log('Error: {0}'.format(e))
        return False

def filter_playlist(playlists):
    basic_playlists = []
    for p in playlists:
        if p.find('.m3u') > 0:
            basic_playlists.append(p)
    return basic_playlists

def main():
    playlist_folder = playlists['folder']
    if len(basic_playlists) > 0:
        basic_playlists.insert(0, 'New playlist')
        result = xbmcgui.Dialog().select('Select a playlist', basic_playlists)
        if result > -1:
            log('Playlist: {0}'.format(basic_playlists[result]))
            if result == 0:
                status = write_playlist(playlist_folder, None, media, 'w')
            else:
                if not playlists['folder']:
                    playlist_folder = basic_playlists[result][1:6]
                    playlist = basic_playlists[result][8:len(basic_playlists[result])]
                else:
                    playlist = basic_playlists[result]
                status = write_playlist(playlist_folder, playlist, media, 'a')
    else:
        status = write_playlist(playlist_folder, None, media, 'w')
    if status:
        xbmcgui.Dialog().notification(addon_name, 'Added: {0}'.format(media_title), xbmcgui.NOTIFICATION_INFO, 5000)
    else:
        xbmcgui.Dialog().notification(addon_name, 'Failed: {0}'.format(media_title), xbmcgui.NOTIFICATION_ERROR, 5000)

if __name__ == '__main__':
    addon_name = xbmcaddon.Addon().getAddonInfo('name')
    log(addon_name)
    basic_playlists = []
    playlist_folder = False
    playlists = {}
    playlists.update({'music': xbmcvfs.listdir(xbmc.translatePath(os.path.join('special://home/userdata/playlists/music')))[1]})
    playlists.update({'video': xbmcvfs.listdir(xbmc.translatePath(os.path.join('special://home/userdata/playlists/video')))[1]})
    if xbmc.getCondVisibility('Container.Content(songs)') == 1:
        log('Container: songs')
        playlists.update({'folder': 'music'})
        media_title = xbmc.getInfoLabel('ListItem.Label')
        basic_playlists = filter_playlist(playlists['music'])
    elif xbmc.getCondVisibility('Container.Content(episodes)') == 1 or xbmc.getCondVisibility('Container.Content(movies)') == 1:
        log('Container: episodes/movies')
        playlists.update({'folder': 'video'})
        media_title = xbmc.getInfoLabel('ListItem.Title')
        basic_playlists = filter_playlist(playlists['video'])
    elif xbmc.getCondVisibility('Container.Content(musicvideos)') == 1:
        log('Container: music videos')
        playlists.update({'folder': False})
        media_title = xbmc.getInfoLabel('ListItem.Title')
        music_playlist = filter_playlist(playlists['music'])
        for playlist in music_playlist:
            basic_playlists.append('[music] {0}'.format(playlist))
        video_playlist = filter_playlist(playlists['video'])
        for playlist in video_playlist:
            basic_playlists.append('[video] {0}'.format(playlist))
    media = '#EXTINF:0,{0}\n{1}\n'.format(media_title, xbmc.getInfoLabel('ListItem.FileNameAndPath'))
    log('Title: {0}'.format(str(media_title)))
    log('Playlists: {0}'.format(str(basic_playlists)))
    main()