import base64
import json
import os
import pickle
import sys
import urllib
import urlparse
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import requests
# import pyxbmct.addonwindow as pyxbmct
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

# http://forum.kodi.tv/showthread.php?tid=240195&pid=2116746#pid2116746
class Gui(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.header = kwargs.get('header')
        self.content = kwargs.get('content')

    def onInit(self):
        self.getControl(1).setLabel(self.header)
        self.getControl(5).setText(self.content)

def log(msg, notify=False):
    if debug:
        xbmc.log('{0} - {1}'.format(addon_name, msg))
    if notify:
        xbmcgui.Dialog().notification(addon_name, msg, xbmcgui.NOTIFICATION_INFO, 5000)

def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)

def load_cache():
    with open(data, 'rb') as f:
        cache = pickle.load(f)
    return cache
    
def git_pull(git):
    if os.path.isfile(data):
        log('Loading data from cache')
        cache = load_cache()
    else:
        log('No cache available')
        cache = {}
    log('Loading repo content')
    content = json.loads(git.text)
    for item in content['tree']:
        file_name = item['path']
        if file_name.find('.') > -1:
            file_key = file_name[0:file_name.rfind('.')]
            file_name_ext = file_name[file_name.rfind('.'):len(file_name)]
            file_sha = item['sha']
            file_url = item['url']
            log('{0}{1} - {2} - {3}'.format(file_key, file_name_ext, file_sha, file_url))
            if file_name_ext == '.txt':
                if file_key not in cache or 'description_sha' not in cache[file_key].keys():
                    log('Adding description: {0}'.format(file_name))
                    if file_key in cache:
                        cache[file_key].update({'description': get_description(file_url), 'description_sha': file_sha})
                    else:
                        cache.update({file_key: {'description': get_description(file_url), 'description_sha': file_sha}})
                elif file_sha != cache[file_key]['description_sha']:
                    log('Updating description: {0}'.format(file_name))
                    cache[file_key].update({'description': get_description(file_url), 'description_sha': file_sha})
            else:
                if file_key not in cache or 'sha' not in cache[file_key].keys():
                    log('Adding {0} URL'.format(file_name))
                    if file_key in cache:
                        cache[file_key].update({'sha': file_sha, 'url': file_url})
                    else:
                        cache.update({file_key: {'sha': file_sha, 'url': file_url}})
                elif file_sha != cache[file_key]['sha']:
                    log('Updating {0} URL'.format(file_name))
                    cache[file_key].update({'sha': file_sha, 'url': file_url})
    log('Caching repo content')
    with open(data, 'wb') as f:
        pickle.dump(cache, f)

def git_fetch():
    log('Conditional request: {0}'.format(addon.getSetting('etag')))
    git = requests.get(repo, headers={'If-None-Match': addon.getSetting('etag')})
    status = git.headers['status']
    log('Status: {0} - Remaining: {1}/{2}'.format(status, git.headers['X-RateLimit-Remaining'], git.headers['X-RateLimit-Limit']))
    if status == '304 Not Modified':
        return False
    elif status == '200 OK':
        etag = git.headers['etag']
        addon.setSetting(id='etag', value=etag[2:len(etag)])
        log('etag: {0}'.format(etag))
        return git
    return False

def download_keymap(file_name, file_url):
    log('Downloading keymap: {0} to {1}'.format(file_name, addon_data))
    file_content = json.loads(requests.get(file_url).text)
    save_location = xbmc.translatePath(os.path.join(addon_data, file_name))
    with open(save_location, 'wb') as f:
        f.write(base64.decodestring(file_content['content']))
    log('Downloaded keymap: {0}'.format(file_name))
    xbmc.executebuiltin('Container.Refresh')

def copy_keymap(file_name, source, destination):
    log('Copying {0} from {1} to {2}'.format(file_name, source, destination))
    xbmcvfs.copy(source, destination)
    log('Copied keymap: {0}'.format(file_name), True)
    xbmc.executebuiltin('Container.Refresh')

def delete_keymap(file_name, copy=False):
    log('Deleting keymap: {0}'.format(file_name))
    xbmcvfs.delete(file_name)
    log('Deleted keymap: {0}'.format(file_name), True)
    xbmc.executebuiltin('Container.Refresh')

def get_description(file_url):
    log('Fetching text: {0}'.format(file_url))
    file_content = json.loads(requests.get(file_url).text)
    return base64.decodestring(file_content['content'])
    
def build_keymap_list():
    keymap_list = []
    keymaps = load_cache()
    loaded_keymaps = xbmcvfs.listdir(keymap_folder)[1]
    local_keymaps = xbmcvfs.listdir(addon_data)[1]
    for keymap in keymaps:
        context_menu = []
        file_name = '{0}.xml'.format(keymap)
        addon_keymap = xbmc.translatePath(os.path.join(addon_data, file_name))
        kodi_keymap = xbmc.translatePath(os.path.join(keymap_folder, file_name))
        display_name = keymap
        if file_name in loaded_keymaps:
            display_name = '[loaded] {0}'.format(keymap)
            url = build_url({'mode': 'delete', 'file_name': file_name, 'source': kodi_keymap, 'destination': kodi_keymap})
        elif file_name in local_keymaps:
            display_name = '[local] {0}'.format(keymap)
            url = build_url({'mode': 'copy', 'file_name': file_name, 'source': addon_keymap, 'destination': kodi_keymap})
        else:
            url = build_url({'mode': 'download', 'keymap': keymap, 'file_name': file_name, 'file_url': keymaps[keymap]['url']})
        li = xbmcgui.ListItem(label=display_name)
        description_url = build_url({'mode': 'display', 'file_name': keymap, 'file_url': keymaps[keymap]['url']})
        context_menu.append(('Keymap Info', 'RunPlugin({0})'.format(description_url)))
        if file_name in local_keymaps:
            delete_local_url = build_url({'mode': 'delete', 'file_name': file_name, 'source': addon_keymap, 'destination': addon_keymap})
            context_menu.append(('Delete local add-on copy', 'RunPlugin({0})'.format(delete_local_url)))
        li.addContextMenuItems(context_menu, replaceItems=True)
        keymap_list.append((url, li, False))
    xbmcplugin.addDirectoryItems(addon_handle, keymap_list, len(keymap_list))
    xbmcplugin.setContent(addon_handle, 'files')
    xbmcplugin.endOfDirectory(addon_handle)

def display_info(keymap, text):
    log('{0} - {1}'.format(keymap, text))
    dialog = Gui('DialogTextViewer.xml', '', header=keymap, content=text).doModal()
    del dialog

def main():
    args = urlparse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)
    if mode is None:
        git = git_fetch()
        if git:
            log('Pulling new data')
            git_pull(git)
        else:
            log('No new data')
        build_keymap_list()
    elif mode[0] == 'display':
        description = load_cache()[args['file_name'][0]]['description']
        display_info(args['file_name'][0], description)
    elif mode[0] == 'download':
        short_description = load_cache()[args['keymap'][0]]['description'][0:100]
        if xbmcgui.Dialog().yesno('Download - {0}'.format(args['file_name'][0]), short_description) == True:
            download_keymap(args['file_name'][0], args['file_url'][0])
    elif mode[0] == 'copy':
        copy_keymap(args['file_name'][0], args['source'][0], args['destination'][0])
    elif mode[0] == 'delete':
        delete_keymap(args['source'][0])
    
if __name__ == '__main__':
    repo = 'https://api.github.com/repos/curtisgalvez/test/git/trees/master'
    addon_data = 'special://home/userdata/addon_data/plugin.program.keymaps'
    keymap_folder = 'special://home/userdata/keymaps'
    data = xbmc.translatePath(os.path.join(addon_data, 'data'))
    addon = xbmcaddon.Addon()
    addon_name = addon.getAddonInfo('name')
    if addon.getSetting('debug') == 'true':
        debug = True
    else:
        debug = False
    if sys.argv == ['']:
        log('Launching from programs')
        xbmc.executebuiltin('RunAddon(plugin.program.keymaps)')
        sys.exit(0)
    addon_handle = int(sys.argv[1])
    main()