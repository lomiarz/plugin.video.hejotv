import sys
import re
import os
import json

import requests
import xbmcgui
import xbmcvfs
import xbmcplugin
import xbmcaddon
import xbmc

from urllib.parse import parse_qsl, quote, urlencode
import http.cookiejar as cookielib

from resources.lib import jsunpack
from resources.lib.htmldom import HtmlDom

addon_base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.hejotv')

PLUGIN_PATH = addon.getAddonInfo('path')
PROFILE_PATH = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
xbmc.log("Plugin directory = {}".format(PROFILE_PATH), level=xbmc.LOGINFO)
COOKIE_FILE = os.path.join(PROFILE_PATH, 'hejotv.cookie')
BASEURL = 'https://hejo.tv'
fanart = PLUGIN_PATH + 'fanart.jpg'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'
CONFIG_FILE_PATH = os.path.join(PLUGIN_PATH, 'resources', 'data', 'config.json')
with open(CONFIG_FILE_PATH) as f:
    CONFIG = json.load(f)

name = params.get('title', None)
image = params.get('image', None)
try:
    opisb = eval(params.get('opisb', None))
except:
    opisb = params.get('opisb', None)
page = params.get('page', [1])[0]

sess = requests.Session()
sess.cookies = cookielib.LWPCookieJar(COOKIE_FILE)

quality = addon.getSetting('tvqual')


def build_url(query):
    return addon_base_url + '?' + urlencode(query)


def add_item(url, name, image, folder, mode, infoLabels=False, isplay=True, itemcount=1, page=1):
    list_item = xbmcgui.ListItem(label=name)

    if folder:
        list_item.setProperty("IsPlayable", 'false')
    else:
        if isplay:
            list_item.setProperty("IsPlayable", 'true')
        else:
            list_item.setProperty("IsPlayable", 'false')

    if not infoLabels:
        infoLabels = {'title': name, 'plot': name}

    list_item.setInfo(type="video", infoLabels=infoLabels)
    list_item.setArt({
        'thumb': image,
        'poster': image,
        'banner': image,
        'fanart': image,
    })
    xbmcplugin.addDirectoryItem(
        handle=addon_handle,
        url=build_url({
            'mode': mode,
            'url': url,
            'page': page,
            'opisb': infoLabels,
            'image': image,
            'title': name,
        }),
        listitem=list_item,
        isFolder=folder,
    )
    xbmcplugin.addSortMethod(
        addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask="%R, %Y, %P")


def home():
    login()
    # add_item('https://hejo.tv/filmy-online?sort=date_desc', 'Filmy', '', True, "listmovies")
    add_item('https://hejo.tv/series/index?sort=date_desc', 'Seriale', '', True, "get_tv_serials")
    add_item(BASEURL, 'Telewizja', '', True, "get_tv_channels")
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle, True)


def get_url(url, redirect=True):
    sess.headers.update({'User-Agent': USER_AGENT})
    if os.path.isfile(COOKIE_FILE):
        sess.cookies.load(COOKIE_FILE, ignore_discard=True)
    if redirect:
        html = sess.get(url, cookies=sess.cookies, allow_redirects=redirect).text
    else:
        html = sess.get(url, cookies=sess.cookies, allow_redirects=redirect)

    set_session_cookies(html)

    return html


def login():
    username = addon.getSetting('username')
    password = addon.getSetting('password')
    logowanie = addon.getSetting('logowanie')

    if username and password and logowanie == 'true':
        headers = {
            'Host': 'hejo.tv',
            'User-Agent': USER_AGENT,
        }
        response = sess.get(BASEURL).content.decode(encoding='utf-8', errors='strict')
        set_session_cookies(response)
        response = sess.get(BASEURL, headers=headers).content.decode(encoding='utf-8', errors='strict')

        dom = HtmlDom().createDom(response)
        xbmc.log("Login response = {}".format(response), level=xbmc.LOGINFO)

        token = dom.find('meta[name=csrf-token]').first().attr('content')
        headers = {
            'Host': 'hejo.tv',
            'user-agent': USER_AGENT,
            'content-type': 'application/x-www-form-urlencoded',
        }
        data = '_token={}&username={}&password={}'.format(token, username, quote(password))
        response = sess.post('{}/login'.format(BASEURL), data=data, headers=headers).content.decode(
            encoding='utf-8', errors='strict')
        set_session_cookies(response)

        html = sess \
            .get(BASEURL, headers=headers, cookies=sess.cookies) \
            .content \
            .decode(encoding='utf-8', errors='strict')

        dom = HtmlDom().createDom(html)
        is_logged_in = dom.find('a#userDropdownMenuButton').len > 0
        if is_logged_in:
            sess.cookies.save(COOKIE_FILE, ignore_discard=True)
            premium_node = dom.find('span.premium')
            account_type = premium_node.first().text() if premium_node.len >= 0 else '[COLOR red]darmowe[/COLOR]'
            text = 'Zalogowany jako [B][COLOR khaki]{}[/COLOR][/B] - {}'.format(username, account_type)
            add_item('', text, '', False, 'settings')
            return
        else:
            xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', 'Błąd logowania :-(')

    add_item(url='', name='[B]Zaloguj[/B]', mode='settings', image='', folder=False, isplay=False)


def set_session_cookies(html):
    cookie_string = re.findall(
        """setCookie\(['"](.+?)['"],['"](.+?)['"]""",
        unpack_javascript_code(html).replace("\\'", '"')
    )
    if cookie_string:
        nowy_cookie = requests.cookies.create_cookie(cookie_string[0][0], cookie_string[0][1])
        sess.cookies.set_cookie(nowy_cookie)
        sess.cookies.save(COOKIE_FILE, ignore_discard=True)

        return True

    return False


def unpack_javascript_code(html, pattern='(eval\(function\(p,a,c,k,e,d\).+?{}\)\))'):
    regexp = re.compile(pattern)
    found = regexp.findall(html)

    return ''.join(list(map(lambda item: jsunpack.unpack(item), found)))


def get_tv_channels(url):
    response = get_url(url)
    dom = HtmlDom().createDom(response)
    channels_tiles = dom.find('img.channel-poster')

    xbmc.log("Number of channels = {}".format(channels_tiles.len), level=xbmc.LOGDEBUG)

    for channel_tile in channels_tiles:
        channel_name = channel_tile.attr('alt')
        channel_logo = channel_tile.attr('data-src')
        parent = channel_tile.parents('a').first()
        current_program_description = parent.attr('data-qtip') if 'data-qtip' in parent.html() else ''
        current_program = parent.find('.card-title').text().strip().replace('\n', '')
        channel_url = parent.attr('href')

        xbmc.log("Channel: name = {}".format(channel_name), level=xbmc.LOGDEBUG)

        channel_info = {
            'plot': '[B]{}[/B]\n{}'.format(current_program, current_program_description),
            'title': channel_name,
        }

        add_item(
            name=channel_name,
            url=channel_url,
            mode='get_tv_stream',
            image=channel_logo,
            folder=False,
            isplay=False,
            infoLabels=channel_info,
            itemcount=channels_tiles.len
        )

    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle, True)


def get_tv_stream(url):
    stream = get_tv_m3u(url)
    if stream.startswith('//'):
        stream = stream.replace('//', 'https://')

    if stream:
        play_item = xbmcgui.ListItem(path=stream)
        play_item.setInfo(type="Video", infoLabels={"title": name, 'plot': opisb['plot']})
        play_item.setArt({'thumb': image, 'poster': image, 'banner': image, 'fanart': fanart})
        play_item.setProperty("IsPlayable", "true")
        player = xbmc.Player()
        player.play(stream, play_item)
    else:
        play_item = xbmcgui.ListItem(path='')
        xbmcplugin.setResolvedUrl(addon_handle, False, listitem=play_item)


def get_tv_m3u(url):
    sess.headers.update({
        'User-Agent': USER_AGENT,
        'Referer': BASEURL,
    })
    try:
        html = get_url(url)
        unpack = unpack_javascript_code(html, '(eval\(function\(p,a,c,k,e,d\).+?\)\)\))')
        unpack += unpack_javascript_code(html)
        unpack = unpack.replace("\\\'", '"')

        api = re.findall('.get\("([^"]+)",function\(c\)', unpack)[0]
        iframe_url = re.findall("<iframe.*src=\"([^\"]+)\".*</iframe>", html)[0]
        xbmc.log("Next url = {}".format(iframe_url), level=xbmc.LOGINFO)
        api = BASEURL + api if api.startswith('/') else api
        xbmc.log("Api url = {}".format(api), level=xbmc.LOGINFO)

        headers = {
            'User-Agent': USER_AGENT,
            'Referer': url,
        }
        response = sess.get(iframe_url, cookies=sess.cookies, headers=headers)
        referer = response.url
        html = response.content.decode(encoding='utf-8', errors='strict')
        stream_url = re.findall("hls.loadSource\('(.+?)'\)", html)[0]

        m3u = sess.get(stream_url, cookies=sess.cookies, headers=headers). \
            content.decode(encoding='utf-8', errors='strict')
        streams = re.findall('RESOLUTION=(.+?)\\r\\n(htt.+?)\\r', m3u, re.DOTALL)
        xbmc.log("Stream m3u = \n{}".format(streams), level=xbmc.LOGINFO)

        if quality == 'auto':
            stream_url = streams[0][1]
        else:
            find_by_quality = [stream for stream in streams if stream[0] == quality]
            stream_url = find_by_quality[0] if len(find_by_quality) == 1 else streams[0][1]

        return '{}|Referer={}'.format(stream_url, referer)

    except Exception as e:
        xbmc.log("Error while getting stream m3u = {}".format(repr(e)), level=xbmc.LOGERROR)
        xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', 'Błąd pobrania streama')

    return ''


def router():
    mode = params.get('mode', 'home')
    url = params.get('url', None)
    xbmc.log("Mode name = {}, url = {}".format(mode, url), level=xbmc.LOGINFO)

    if mode == 'get_tv_channels':
        get_tv_channels(url)
    if mode == 'get_tv_stream':
        get_tv_stream(url)
    if mode == 'settings':
        addon.openSettings()
        xbmc.executebuiltin('Container.Refresh()')
    if mode == 'home':
        home()


if __name__ == '__main__':
    router()
