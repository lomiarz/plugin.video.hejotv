from resources.lib import jsunpack
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


try:
    # For Python 3.0 and later
    from urllib.parse import parse_qsl, quote, urlencode
    import http.cookiejar as cookielib
except ImportError:
    # Python 2
    xbmc.log("Pyton error...", level=xbmc.LOGINFO)
    from urlparse import parse_qsl
    import cookielib
    from urllib import unquote, quote, urlencode


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))

xbmcplugin.addSortMethod(handle=int(
    sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(handle=int(
    sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_DATE)
xbmcplugin.addSortMethod(handle=int(
    sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE)
xbmcplugin.addSortMethod(handle=int(
    sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_LABEL)
xbmcplugin.addSortMethod(handle=int(
    sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_LASTPLAYED)


addon = xbmcaddon.Addon(id='plugin.video.hejotv')
BASEURL = 'https://hejo.tv/home'
PATH = addon.getAddonInfo('path')
try:
    DATAPATH = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
except:
    DATAPATH = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')

if isinstance(DATAPATH, bytes):
    DATAPATH = DATAPATH.decode('utf-8')
if isinstance(PATH, bytes):
    PATH = PATH.decode('utf-8')

COOKIEFILE = os.path.join(DATAPATH, 'hejotv.cookie')
BASEURL2 = 'https://hejo.tv'
RESOURCES = PATH+'/resources/'
FANART = PATH+'fanart.jpg'

CONFIG_FILE_PATH = os.path.join(PATH, 'resources', 'data', 'config.json')
xbmc.log("Reading config....", level=xbmc.LOGINFO)
with open(CONFIG_FILE_PATH) as f:
  CONFIG = json.load(f)

kukz = ''
kukz2 = ''
packer = re.compile('(eval\(function\(p,a,c,k,e,(?:r|d).*)')


if PY3:
    # for Python 3
    from resources.lib.cmf3 import parseDOM
    from resources.lib.cmf3 import replaceHTMLCodes

else:
    # for Python 2
    from resources.lib.cmf2 import parseDOM
    from resources.lib.cmf2 import replaceHTMLCodes


exlink = params.get('url', None)
name = params.get('title', None)
rys = params.get('image', None)
try:
    opisb = eval(params.get('opisb', None))
except:
    opisb = params.get('opisb', None)
page = params.get('page', [1])[0]
sess = requests.Session()
sess.cookies = cookielib.LWPCookieJar(COOKIEFILE)
UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'
jakosc = addon.getSetting('tvqual')
headersok = {
    'User-Agent': UA,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
    'Referer': 'https://hejo.tv/home',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0', }


def build_url(query):
    return base_url + '?' + urlencode(query)


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
    add_item('https://hejo.tv/filmy-online?sort=date_desc', 'Filmy', '', True, "listmovies")
    add_item('https://hejo.tv/series/index?sort=date_desc', 'Seriale', '', True, "listserials")
    add_item('https://hejo.tv/', 'Telewizja', '', True, "listtv")
    add_item('', '[COLOR lightblue]Szukaj filmu lub serialu[/COLOR]', '', True, "search")
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle, True)


def cookieString(COOKIEFILE):
    sc = ''
    if os.path.isfile(COOKIEFILE):
        sess.cookies.load(COOKIEFILE)
        sc = ''.join(['%s=%s;' % (c.name, c.value) for c in sess.cookies])
    return sc


def getUrl(url, redir=True):
    sess.headers.update({'User-Agent': UA})
    if os.path.isfile(COOKIEFILE):
        sess.cookies.load(COOKIEFILE, ignore_discard=True)
    if redir:
        html = sess.get(url, cookies=sess.cookies,
                        verify=False, allow_redirects=redir).text
    else:
        html = sess.get(url, cookies=sess.cookies,
                        verify=False, allow_redirects=redir)
    if 'function setCookie' in html:
        try:
            kk = dodajKuki(html)
            if kk:
                getUrl(url)
            else:
                pass
        except:
            pass

    return html


def dodajKuki(html):
    packer2 = re.compile('(eval\(function\(p,a,c,k,e,d\).+?{}\)\))')

    unpacked = ''
    packeds = packer2.findall(html)
    for packed in packeds:
        unpacked += jsunpack.unpack(packed)
    unpacked = unpacked.replace("\\'", '"')
    kukz = re.findall(
        """setCookie\(['"](.+?)['"],['"](.+?)['"]""", unpacked)  # [0]
    if kukz:
        kukz = kukz[0]
        nowy_cookie = requests.cookies.create_cookie(kukz[0], kukz[1])
        sess.cookies.set_cookie(nowy_cookie)
        sess.cookies.save(COOKIEFILE, ignore_discard=True)
        return True
    else:
        return False


def zalogujponownie(exlink):
    sess.cookies.clear()
    username = addon.getSetting('username')
    password = addon.getSetting('password')
    logowanie = addon.getSetting('logowanie')

    if username and password and logowanie == 'true':
        headers = {
            'Host': 'hejo.tv',
            'User-Agent': UA,
            'Accept': 'text/html',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        }

        response = sess.get('http://hejo.tv/',
                            headers=headers, verify=False).content
        if PY3:
            response = response.decode(encoding='utf-8', errors='strict')
        packer2 = re.compile('(eval\(function\(p,a,c,k,e,d\).+?{}\)\))')
        unpacked = ''
        packeds = packer2.findall(response)  # [0]
        for packed in packeds:
            unpacked += jsunpack.unpack(packed)
        unpacked = unpacked.replace("\\'", '"')
        try:
            kukz = re.findall(
                """setCookie\(['"](.+?)['"],['"](.+?)['"]""", unpacked)[0]
            nowy_cookie = requests.cookies.create_cookie(kukz[0], kukz[1])

            sess.cookies.set_cookie(nowy_cookie)
            response = sess.get('http://hejo.tv/', verify=False).content
            if PY3:
                response = response.decode(encoding='utf-8', errors='strict')
        except:
            pass
        token = parseDOM(response, 'meta', attrs={
                         'name': 'csrf-token'}, ret='content')[0]
        data = {'_token': token, 'username': username, 'password': password}
        response = sess.post('https://hejo.tv/login',
                             data=data, verify=False).content
        if PY3:
            response = response.decode(encoding='utf-8', errors='strict')
        packer2 = re.compile('(eval\(function\(p,a,c,k,e,d\).+?{}\)\))')
        unpacked = ''
        packeds = packer2.findall(response)  # [0]
        for packed in packeds:
            unpacked += jsunpack.unpack(packed)
        unpacked = unpacked.replace("\\'", '"')
        kukz = re.findall(
            """setCookie\(['"](.+?)['"],['"](.+?)['"]""", unpacked)[0]
        nowy_cookie = requests.cookies.create_cookie(kukz[0], kukz[1])
        sess.cookies.set_cookie(nowy_cookie)
        html = sess.get('https://hejo.tv/login', verify=False).content
        if PY3:
            html = html.decode(encoding='utf-8', errors='strict')
        if html.find('logowany jako') > 0:
            sess.cookies.save(COOKIEFILE, ignore_discard=True)
    return


def login():
    username = addon.getSetting('username')
    password = addon.getSetting('password')
    logowanie = addon.getSetting('logowanie')

    if username and password and logowanie == 'true':
        headers = {
            'Host': 'hejo.tv',
            'User-Agent': UA,
            'Accept': 'text/html',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        }

        response = sess.get('http://hejo.tv/', verify=False).content
        if PY3:
            response = response.decode(encoding='utf-8', errors='strict')
        packer2 = re.compile('(eval\(function\(p,a,c,k,e,d\).+?{}\)\))')
        unpacked = ''
        packeds = packer2.findall(response)  # [0]
        for packed in packeds:
            unpacked += jsunpack.unpack(packed)
        unpacked = unpacked.replace("\\'", '"')
        xbmc.log("Unpacked = {}".format(unpacked), level=xbmc.LOGINFO)
        try:
            kukz = re.findall(
                """setCookie\(['"](.+?)['"],['"](.+?)['"]""", unpacked)[0]
            nowy_cookie = requests.cookies.create_cookie(kukz[0], kukz[1])
            sess.cookies.set_cookie(nowy_cookie)
            response = sess.get('http://hejo.tv/',
                                headers=headers, verify=False).content
            if PY3:
                response = response.decode(encoding='utf-8', errors='strict')
        except:
            pass
        token = parseDOM(response, 'meta', attrs={
                         'name': 'csrf-token'}, ret='content')[0]
        headers2 = {
            'Host': 'hejo.tv',
            'user-agent': UA,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-language': 'pl,en-US;q=0.7,en;q=0.3',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://hejo.tv',
            'referer': 'https://hejo.tv/',
            'upgrade-insecure-requests': '1',
            'te': 'trailers', }

       # data = {'_token': token,'username': username,'password': password}
        data = '_token={}&username={}&password={}'.format(
            token, username, quote(password))

        response = sess.post('https://hejo.tv/login',
                             data=data, headers=headers2, verify=False).content
        if PY3:
            response = response.decode(encoding='utf-8', errors='strict')
        packer2 = re.compile('(eval\(function\(p,a,c,k,e,d\).+?{}\)\))')
        unpacked = ''
        packeds = packer2.findall(response)  # [0]

        for packed in packeds:
            unpacked += jsunpack.unpack(packed)
        unpacked = unpacked.replace("\\'", '"')
        kukz = re.findall(
            """setCookie\(['"](.+?)['"],['"](.+?)['"]""", unpacked)  # [0]
        if kukz:
            kukz = kukz[0]
            nowy_cookie = requests.cookies.create_cookie(kukz[0], kukz[1])
            sess.cookies.set_cookie(nowy_cookie)
        html = sess.get('https://hejo.tv/login', headers=headers,
                        cookies=sess.cookies, verify=False).content
        if PY3:
            html = html.decode(encoding='utf-8', errors='strict')
        if html.find('> Wyloguj się<') > 0:
            sess.cookies.save(COOKIEFILE, ignore_discard=True)
            if 'Wykup konto premium' in html:
                typ = ' [COLOR red](darmowe)[/COLOR]'
            else:
                info = (re.findall('>(Premium do.+?)</a>', html)[0]).lower()
                typ = ' [COLOR khaki](%s)[/COLOR]' % info
                log1 = re.findall(
                    """class="fa fa-user" aria-hidden="true"></i>([^<]+)<""", html)[0]
                zalog = 'Zalogowany jako [COLOR khaki]%s[/COLOR]' % log1.strip()
                add_item('', '[B](%s)[/B] -%s' %
                         (zalog, typ), '', False, 'settings')
        else:
            s = xbmcgui.Dialog().ok(
                '[COLOR red]Problem[/COLOR]', 'Błąd logowania :-(')
            add_item(url='', name='[B]Zaloguj[/B]',  mode='settings',
                     image='', folder=False, isplay=False)
    else:
        add_item(url='', name='[B]Zaloguj[/B]',  mode='settings',
                 image='', folder=False, isplay=False)


def ListSport(exlink):
    links = getSport(exlink)
    if links:
        itemz = links
        items = len(links)
        mud = 'getTvStream'
        fold = False
        ispla = False
        for f in itemz:
            infoL = {'plot': f.get('plot'), 'title': f.get('title')}
            add_item(name=f.get('title'), url=f.get('href'), mode=mud, image=f.get(
                'img'), folder=fold, isplay=ispla, infoLabels=infoL, itemcount=items)
        xbmcplugin.setContent(addon_handle, 'videos')
        xbmcplugin.endOfDirectory(addon_handle, True)

    else:
        s = xbmcgui.Dialog().ok(
            '[COLOR red]Problem[/COLOR]', 'Tylko konta premium :-(')


def ListMovies(exlink, page):

    page = int(page) if page else 1
    links, pagin = getMovies(exlink, page)

    if pagin[0]:
        add_item(name='[COLOR blue]<< poprzednia strona <<[/COLOR]',
                 url=exlink, mode='__page__M', image='', folder=True, page=pagin[0])

    itemz = links
    items = len(links)
    mud = 'getLinks'
    fold = False
    for f in itemz:

        add_item(name=f.get('title'), url=f.get('href'), mode=mud, image=f.get(
            'img'), folder=fold, infoLabels=f.get('ilab'), itemcount=items)
    if pagin[1]:
        add_item(name='[COLOR blue]>> Nastepna strona >>[/COLOR]',
                 url=exlink, mode='__page__M', image='', folder=True, page=pagin[1])
    xbmcplugin.setContent(addon_handle, 'movies')
    xbmcplugin.endOfDirectory(addon_handle, True)


def ListSerials(exlink, page):
    page = int(page) if page else 1
    links, pagin = getSerials(exlink, page)
    if pagin[0]:
        add_item(name='[COLOR blue]<< poprzednia strona <<[/COLOR]',
                 url=exlink, mode='__page__S', image='', folder=True, page=pagin[0])

    itemz = links
    items = len(links)
    mud = 'listseasons'
    fold = True
    for f in itemz:
        infoL = {'plot': f.get('plot'), 'title': f.get('title')}
        add_item(name=f.get('title'), url=f.get('href'), mode=mud, image=f.get(
            'img'), folder=fold, infoLabels=infoL, itemcount=items)
    if pagin[1]:
        add_item(name='[COLOR blue]>> Nastepna strona >>[/COLOR]',
                 url=exlink, mode='__page__S', image='', folder=True, page=pagin[1])
    xbmcplugin.setContent(addon_handle, 'tvshows')
    xbmcplugin.endOfDirectory(addon_handle, True)


def ListSeasons(exlink):
    links = getSeasons(exlink)
    if links:
        itemz = links
        items = len(links)
        mud = 'listepisodes'
        fold = True
        for f in itemz:
            infoL = {'plot': f.get('plot'), 'title': f.get('title')}
            add_item(name=f.get('title'), url=f.get('href'), mode=mud, image=f.get(
                'img'), folder=fold, infoLabels=infoL, itemcount=items)
        xbmcplugin.setContent(addon_handle, 'tvshows')
        xbmcplugin.endOfDirectory(addon_handle, True)
    else:
        s = xbmcgui.Dialog().ok(
            '[COLOR red]Problem[/COLOR]', 'Brak materiału do wyświetlenia')


def ListEpisodes(exlink):

    exlink = exlink.split('|')
    nazw = exlink[1]
    exlin = exlink[0]
    links = getEpisodes(exlin, nazw)
    itemz = links
    items = len(links)
    mud = 'getLinks'
    fold = False
    for f in itemz:
        infoL = {'plot': f.get('plot'), 'title': f.get('title')}
        add_item(name=f.get('title'), url=f.get('href'), mode=mud, image=f.get(
            'img'), folder=fold, infoLabels=infoL, itemcount=items)
    xbmcplugin.setContent(addon_handle, 'episodes')
    xbmcplugin.endOfDirectory(addon_handle, True)


def ListTv(exlink):
    if 'category/' in exlink:
        links = getTVcat(exlink)
    else:
        links = getTV(exlink)
    if links:
        itemz = links
        items = len(links)
        mud = 'getTvStream'
        fold = False
        for f in itemz:
            infoL = {'plot': f.get('plot'), 'title': f.get('title')}
            add_item(name=f.get('title'), url=f.get('href'), mode=mud, image=f.get(
                'img'), folder=fold, isplay=False, infoLabels=infoL, itemcount=items)
        xbmcplugin.setContent(addon_handle, 'videos')
        xbmcplugin.endOfDirectory(addon_handle, True)
    else:
        s = xbmcgui.Dialog().ok(
            '[COLOR red]Problem[/COLOR]', 'Brak materiałów do wyświetlenia')


def getSport(url):
    out = []
    try:
        kuk = cookieString(COOKIEFILE)
        html = getUrl(url)
        result = parseDOM(html, 'table', attrs={
                          'class': "table table-striped.+?"})[0]
        linksy = re.findall("tion='(.+?)'\;", result)
        counter = 0
        links = parseDOM(result, 'tr', attrs={'style': "cursor: pointer;"})
        for link in links:
            href = PLchar(linksy[counter])
            imag = parseDOM(link, 'img', ret='src')[0]
            title = (parseDOM(link, 'td')[1]).replace('ONLINE', '')
            title2 = parseDOM(link, 'td')[2]
            czas = parseDOM(link, 'td')[4]
            title = str(PLchar(title)).strip()
            title2 = str(PLchar(title2)).strip()
            czas = PLchar(czas)
            href = href.replace('http:', 'https:')
            tytul = '[B]'+title+'[/B]'+' - '+title2
            out.append({'title': '[B][COLOR yellowgreen]'+czas+' - [/B][/COLOR] '+tytul, 'href': href, 'plot': '[B][COLOR yellowgreen]' +
                       czas+' - [/B][/COLOR] '+tytul, 'img': imag+'|User-Agent='+quote(UA)+'&Referer='+BASEURL+'&Cookie='+quote(kuk)})
            counter += 1
    except:
        pass
    return out


def getTV(url):
    out = []
    kuk = cookieString(COOKIEFILE)
    html = ''

    html += getUrl(url)
    # for x in range(1, 6):
    #    urlk='https://hejo.tv/home?page=%s'%x
    #    html += getUrl(urlk)
    content = getHtml()
    links = parseDOM(html, 'div', attrs={
                     'class': "col-lg-3 col-md-4 col-sm-6 col-12 p-2"})

    for link in links:

        href = parseDOM(link, 'a', ret='href')[0]
        imag = parseDOM(link, 'img', ret='src')[0]
        imag = 'https://hejo.tv'+imag if imag.startswith('/upload') else imag
        title = parseDOM(link, 'img', ret='alt')[0]

        if title:
            plot = ''
            plot = getPlot(title, content)

        online = parseDOM(link, 'span', attrs={'style': "border-radius: 0px;"})[0].replace(
            '<i class="fa fa-check"></i>', '').replace('\t', '').replace('\n', '')  # style="border-radius: 0px;">
        online = online.strip()
        title = PLchar(title)
        online = PLchar(online)
        out.append({'title': title+'[B][COLOR yellowgreen] ('+online+')[/B][/COLOR]', 'href': href,
                   'img': imag+'|User-Agent='+quote(UA)+'&Referer='+BASEURL+'&Cookie='+quote(kuk), 'plot': plot})
    return out


def getTVcat(url):
    kuk = cookieString(COOKIEFILE)
    out = []
    html = getUrl(url)
    content = getHtml()
    links = parseDOM(html, 'div', attrs={
                     'class': "col-lg-3 col-md-3 col-xs-4 col-xxs-12"})
    imag = parseDOM(html, 'div', attrs={
                    'style': "background-image.+?"}, ret="style")
    c = 0
    if links:
        for link in links:
            img = re.findall("url\('(.+?)'", imag[c])[0]
            href = parseDOM(link, 'a', ret='href')[0]
            title = parseDOM(link, 'h4')[0]
            if title:
                plot = getPlot(title, content)
            # .replace('<i class="fa fa-flag"></i>','').replace('\t','').replace('\n','')   #style="border-radius: 0px;">
            online = parseDOM(link, 'div', attrs={'class': "status live"})[0]
            online = online.strip()
            title = PLchar(title)
            online = PLchar(online)
            out.append({'title': title+'[B][COLOR yellowgreen] ('+online+')[/B][/COLOR]', 'href': href,
                       'img': img+'|User-Agent='+quote(UA)+'&Referer='+BASEURL+'&Cookie='+quote(kuk), 'plot': plot})
            c += 1
    return out


def getMovies(url, page=1):
    if '&page=' in url:
        url = url.replace('&page=', '&page=%d' % page)
    else:
        url = url + '&page=%d' % page
    html = getUrl(url)

    kuk = cookieString(COOKIEFILE)
    out = []
    serout = []

    prevpage = False
    nextpage = False
    if html.find('rel="next">') > 0:
        nextpage = page+1

    links = parseDOM(html, 'div', attrs={'class': "ml-item"})
    for link in links:
        link = replaceHTMLCodes(link)
        imag = parseDOM(link, 'img', ret='src')[0]
        title = parseDOM(link, 'a', ret='title')[0]
        year = parseDOM(link, 'div', attrs={'class': "jt-info"})
        if year:
            try:
                year = re.findall('(\d+)', year[0])[0]
            except:
                year = ''

        else:
            year = ''
        plot = parseDOM(link, 'p', attrs={'class': "f-desc"})
        plot = plot[1] if plot else ''
        #genre = re.findall('"category tag">([^<]+)<',link)

        #genres = ','.join([(x.strip()).lower() for x in genre]) if genre else ''

        genres = re.findall('Kategorie\:(.+?)<', link, re.DOTALL+re.IGNORECASE)
        genres = (genres[0].strip()).lower() if genres else ''

        lang = parseDOM(link, 'div', attrs={'class': "jt-info jt-imdb"})

        #lang = re.findall('33ff0069">([^<]+)<',link)
        lang = lang[1].strip() if lang else ''
        href = parseDOM(link, 'a', ret='href')[0]
        out.append({'title': PLchar(title)+'[B][COLOR yellowgreen] ('+PLchar(lang)+')[/B][/COLOR]', 'href': PLchar(href), 'img': 'https://hejo.tv'+PLchar(
            imag)+'|User-Agent='+quote(UA)+'&Referer='+BASEURL+'&Cookie='+quote(kuk), 'ilab': {'plot': PLchar(plot), 'genre': PLchar(genres), 'year': year, 'lang': lang}})
    prevpage = page-1 if page > 1 else False
    return (out, (prevpage, nextpage))


def getSerials(url, page):
    if '&page=' in url:
        url = url.replace('&page=', '&page=%d' % page)
    else:
        url = url + '&page=%d' % page

    html = getUrl(url)
    kuk = cookieString(COOKIEFILE)
    out = []
    prevpage = False
    nextpage = False
    if html.find('rel="next">') > 0:
        nextpage = page+1

    # =  <div class="ml-item">
    links = parseDOM(html, 'div', attrs={'class': "ml-item"})

    for link in links:

        link = replaceHTMLCodes(link)

        img = parseDOM(link, 'img', ret='src')[0]
        imag = BASEURL2+img if img.startswith('/') else img

        href = parseDOM(link, 'a', ret='href')[0]
        title = parseDOM(link, 'a', ret='title')[0]
        #title = parseDOM(link, 'h5')[0]
        plot = '[COLOR yellowgreen][B]' + \
            PLchar(title)+'[/B][/COLOR]'  # [CR]'+PLchar(plot)
        #odc = parseDOM(link, 'span', attrs={'class': "badge badge-info"})[0]

        odc = re.findall('"text-center">(.+?)<', link)[0]

        out.append({'title': PLchar(title)+'[B][COLOR yellowgreen] [ '+PLchar(odc)+' ][/B][/COLOR]', 'href': PLchar(
            href), 'img': imag+'|User-Agent='+quote(UA)+'&Referer='+BASEURL+'&Cookie='+quote(kuk), 'plot': plot})
    prevpage = page-1 if page > 1 else False
    return (out, (prevpage, nextpage))


def getSeasons(url):
    html = getUrl(url)
    kuk = cookieString(COOKIEFILE)
    out = []
    result = parseDOM(html, 'div', attrs={'class': "pt-\d+ pb-\d+"})[0]
    links = parseDOM(result, 'div', attrs={
                     'class': "col-lg-4 col-md-4 col-sm-4 col-6 col-xxs-12"})
    plot1 = re.findall('-100">([^<]+)<', result)[0].strip()
    plot = re.findall('<hr>([^<]+)</div>', result)[0].strip()
    plot = '[COLOR yellowgreen][B]' + \
        PLchar(plot1)+'[/B][/COLOR][CR]'+PLchar(plot)
    img = parseDOM(result, 'img', ret='src')[0]
    imag = BASEURL2+img if img.startswith('/') else img
    titles = parseDOM(result, 'strong')  # [0]
    for title in titles:
        out.append({'title': PLchar(plot1)+' - '+PLchar(title), 'href': url+'|'+title, 'img': imag +
                   '|User-Agent='+quote(UA)+'&Referer='+BASEURL+'&Cookie='+quote(kuk), 'plot': plot})
    return out


def getEpisodes(url, tit):

    html = getUrl(url)
    kuk = cookieString(COOKIEFILE)
    out = []
    result = parseDOM(html, 'div', attrs={'class': "pt-\d+ pb-\d+"})[0]
    plot1 = re.findall('-100">([^<]+)<', result)[0].strip()
    plotx = re.findall('<hr>([^<]+)</div>', result)[0].strip()
    img = parseDOM(result, 'img', ret='src')[0]
    imag = BASEURL2+img if img.startswith('/') else img
    resk = re.findall(tit+'</strong>(.+?)</ul>', html, re.DOTALL)[0]
    resk = replaceHTMLCodes(resk)
    wsio = re.findall(
        'data-playerid="(.+?)" data-season="(\d+)" data-episode="(\d+)">', resk, re.DOTALL)
    for playid, seas, epis in wsio:

        nrsez = '{:>02d}'.format(int(seas))
        nrodc = '{:>02d}'.format(int(epis))
        title = '%s - S%se%s' % (PLchar(plot1), nrsez, nrodc)
        plot = '[COLOR yellowgreen][B]' + \
            PLchar(plot1)+'[/COLOR][COLOR blue] [' + \
            title+'][/B][/COLOR][CR]'+PLchar(plotx)
        out.append({'title': PLchar(title), 'href': playid, 'img': imag+'|User-Agent=' +
                   quote(UA)+'&Referer='+BASEURL+'&Cookie='+quote(kuk), 'plot': plot})

    return out


def getTvStream(exlink):

    stream = getTVm3u(exlink)
    if stream.startswith('//'):
        stream = stream.replace('//', 'https://')

    if stream:
        play_item = xbmcgui.ListItem(path=stream)
        play_item.setInfo(type="Video", infoLabels={
                          "title": name, 'plot': opisb['plot']})

        play_item.setArt({'thumb': rys, 'poster': rys,
                         'banner': rys, 'fanart': FANART})

        play_item.setProperty("IsPlayable", "true")
        Player = xbmc.Player()
        Player.play(stream, play_item)

    else:
        play_item = xbmcgui.ListItem(path='')
        xbmcplugin.setResolvedUrl(addon_handle, False, listitem=play_item)


def getTVm3u(url):

    sess.headers.update({
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Referer': 'https://hejo.tv/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    try:

        html = getUrl(url)
        unpack = ''
        htmlsy = re.findall('script.defer(.+?)$', html, re.DOTALL)  # [0]
        htmlsy = htmlsy[0] if htmlsy else html
        pack3 = re.compile('(eval\(function\(p,a,c,k,e,d\).+?\)\)\))')
        results = pack3.findall(htmlsy)  # [0]

        for result in results:
            unpack += jsunpack.unpack(result)
        packer2 = re.compile('(eval\(function\(p,a,c,k,e,d\).+?{}\)\))')
        results = packer2.findall(htmlsy)  # [0]
        for result in results:

            unpack += jsunpack.unpack(result)

        unpack = unpack.replace("\\\'", '"')
        if 'setCookie' in unpack:
            zalogujponownie()
            getTVm3u(url)
        api = re.findall('.get\("([^"]+)",function\(c\)', unpack)[0]
        nxturl = parseDOM(html, 'iframe', attrs={
                          'name': "livetv", "src": ".+?"}, ret='src')[0]
        api = 'https://hejo.tv'+api if api.startswith('/') else api
        chTbl = []

        headers2 = {
            'User-Agent': UA,
            'Accept': '*/*',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': url,
            'TE': 'Trailers',
        }

        chTbl = sess.get(api, cookies=sess.cookies,
                         headers=headers2, verify=False).json()
        headers = {
            'User-Agent': UA,
            'Accept': '*/*',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'Referer': url,
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'TE': 'Trailers', }
        html = sess.get(nxturl, cookies=sess.cookies,
                        headers=headers, verify=False)  # .content
        ref = html.url
        html = html.content
        if PY3:
            html = html.decode(encoding='utf-8', errors='strict')
        stream_url = re.findall("hls.loadSource\('(.+?)'\)", html)[0]

        pol = sess.get(stream_url, cookies=sess.cookies,
                       headers=headers, verify=False).content
        if PY3:
            pol = pol.decode(encoding='utf-8', errors='strict')
        jakoscstream_url = re.findall(
            'RESOLUTION=(.+?)\\r\\n(htt.+?)\\r', pol, re.DOTALL)
        if jakoscstream_url:
            if jakosc == 'auto':
                stream_url = jakoscstream_url[0][1]
            else:
                try:
                    for jak, href in jakoscstream_url:
                        if jakosc == jak:
                            stream_url = href
                        else:
                            continue

                except:
                    stream_url = jakoscstream_url[0][1]

            streamy = stream_url+'|Referer='+ref
        else:
            streamy = ''  # stream_url+'|Referer='+ref
    except Exception as e:
        sel = xbmcgui.Dialog().ok(
            '[COLOR red]Problem[/COLOR]', 'Tylko konta premium :-(')
        streamy = ''
    return streamy


def getLinks(exlink):
    if '/' not in exlink:
        stream = getSerialLink(exlink)
    else:
        stream = getVideosOk(exlink)
    if stream:
        if stream.startswith('//'):
            stream = stream.replace('//', 'https://')
        if 'filmo-sfera' in stream or 'film.hejo.tv/v-' in stream or 'internetowa.tv' in stream:
            stream_url = stream
        if stream_url:
            stream_url, hd = stream_url.split('|')
            play_item = xbmcgui.ListItem(path=stream_url)
            if PY3:
                play_item.setProperty('inputstream', 'inputstream.adaptive')
            else:
                play_item.setProperty('inputstreamaddon',
                                      'inputstream.adaptive')
            play_item.setProperty('inputstream.adaptive.stream_headers', hd)
            play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            play_item.setMimeType('application/vnd.apple.mpegurl')
            xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
        else:
            play_item = xbmcgui.ListItem(path='')
            xbmcplugin.setResolvedUrl(addon_handle, False, listitem=play_item)
    else:
        s = xbmcgui.Dialog().ok(
            '[COLOR red]Problem[/COLOR]', 'Brak działającego linka', '')


def getVideosOk(url):
    html = getUrl(url)

    packeds = packer.findall(html)

    for packed in packeds:

        unpack = jsunpack.unpack(packed)
        try:
            player = re.findall('"(\/player.+?)"', unpack)
            if not player:
                player = re.findall('"(.+?\/player.*?)"', unpack)
            if player:
                player = player[0]
                break
        except:
            pass
    nexturl = player if player.startswith('http') else 'https://hejo.tv'+player

    html = getUrl(nexturl)
    stream = re.findall('src="(.+?)"', html)[0]
    stream = 'https:'+stream if stream.startswith('//') else stream
    if not 'mp4' in stream:
        stream = getUrl(stream, False)
        stream = stream.headers['Location']
    kuk = cookieString(COOKIEFILE)
    return stream+'|User-Agent='+quote(UA)+'&Referer='+BASEURL+'&Cookie='+quote(kuk)


def getSerialLink(playid):
    url = 'https://hejo.tv/series/%s/player' % playid
    html = getUrl(url)
    stream = ''
    stream = re.findall('src="(.+?)"', html)  # [0]
    if stream:
        kuk = cookieString(COOKIEFILE)
        stream = stream[0].replace(
            '&amp;', '&')+'|User-Agent='+quote(UA)+'&Referer='+BASEURL+'&Cookie='+quote(kuk)
    return stream


def getGatunek(exlink):
    out = []
    par = exlink.split('|')
    if 'filmy' in par[1]:
        url_main = 'https://hejo.tv/filmy-online'
    else:
        url_main = 'https://hejo.tv/'
    html = getUrl(url_main)
    result = parseDOM(html, 'form', attrs={'id': "filter-form"})  # [0]
    result = result[0] if result else ''
    result2 = parseDOM(html, 'div', attrs={
                       'aria-labelledby': "navbarDropdownMenuLink"})  # [0]
    result2 = result2[0] if result2 else ''
    if 'kategorie:' in exlink:
        valdan = re.findall('name="(.+?)"\s*value="(.+?)"', result)

        for val, dan in valdan:
            genre = dan

            url = url_main+'?'+val+'='+dan+'&sort=date_desc'
            out.append((genre, url))
    if 'rok:' in exlink:
        link = parseDOM(result, 'select', attrs={'multiple name': "years\[\]"})[
            0]  # multiple name="languages[]"years[]
        dane = re.findall('value="(\d+)">(.+?)<', link)
        for dan in dane:
            year = dan[1]
            url = url_main+'?years[]='+dan[0]+'&sort=date_desc'
            out.append((year, url))
    if 'wersje:' in exlink:
        link = parseDOM(result, 'select', attrs={
                        'multiple name': "languages[]"})[0]
        dane = re.findall('value="(\d+)">(.+?)<', link)
        for dan in dane:
            vers = dan[1]
            url = url_main+'?languages[]='+dan[0]+'&sort=date_desc'
            out.append((vers, url))
    if 'kanał' in exlink:
        dane = re.findall('href="(.+?)">(.+?)<', result2)
        for dan in dane:
            chan = dan[1]
            url = dan[0]
            out.append((chan, url))
    return out


def search(q='batman'):
    kuk = cookieString(COOKIEFILE)
    out = []
    html = getUrl('https://hejo.tv/search?q='+q)

    linksf = parseDOM(html, 'div', attrs={
                      'class': "col-lg-\d+ col-md-\d+ col-sm-\d+ col-\d+ p-\d+ _mv-link-item"})
    dupa = parseDOM(html, 'div', attrs={'class': "ml-item"})
    # col-lg-4 col-md-4 col-sm-4 col-6 col-xxs-12
    linkss = parseDOM(html, 'div', attrs={
                      'class': "col-lg-\d+ col-md-\d+ col-sm-\d+ col-\d+ col-xxs-\d+"})
    # parseDOM(html, 'div', attrs={'class': "col-lg-\d+ col-md-\d+ col-xs-\d+ col-xxs-\d+"}) #col-lg-4 col-md-4 col-sm-4 col-6 col-xxs-12
    linksch = re.findall(
        '"col-lg-\d+ col-md-\d+ col-xs-\d+ col-xxs-\d+"(.+?)div class="meta">', html, re.DOTALL)
    if linksch:
        xbmc.log("linksch", level=xbmc.LOGINFO)
        for link in linksch:
            img = re.findall("url\('(.+?)'", link)[0]
            imag = BASEURL2+img if img.startswith('/') else img
            href = parseDOM(link, 'a', ret='href')[0]
            title = parseDOM(link, 'h4')[0]
            plot = ''
            online = parseDOM(link, 'div', attrs={'class': "status live"})[0]
            online = online.strip()
            title = PLchar(title)
            online = PLchar(online)
            out.append({'title': title+'[B][COLOR yellowgreen] ('+online+')[/B][/COLOR]', 'href': href,
                       'img': imag+'|User-Agent='+quote(UA)+'&Referer='+BASEURL+'&Cookie='+quote(kuk), 'plot': plot})
    if linksf:
        xbmc.log("linksf", level=xbmc.LOGINFO)
        for link in linksf:
            link = replaceHTMLCodes(link)
            imag = parseDOM(link, 'img', ret='src')[0]
            title = parseDOM(link, 'h5')[0]
            year = re.findall('fa-calendar"><\/i>([^<]+)<', link)
            year = int(year[0].strip()) if year else ''
            plot = re.findall('Opis</strong><br>([^<]+)<', link)
            plot = plot[0].strip() if plot else ''
            genres = re.findall('5px\;">([^<]+)<', link)
            genres = genres[0].strip() if genres else ''
            lang = re.findall('fa-flag"><\/i>([^<]+)<', link)
            lang = lang[0].strip() if lang else ''
            href = parseDOM(link, 'a', ret='href')[0]
            out.append({'title': PLchar(title)+'[B][COLOR yellowgreen] ('+PLchar(lang)+')[/B][/COLOR]', 'href': PLchar(href), 'img': 'https://hejo.tv'+PLchar(
                imag)+'|User-Agent='+quote(UA)+'&Referer='+BASEURL+'&Cookie='+quote(kuk), 'plot': PLchar(plot), 'genre': PLchar(genres), 'year': year, 'lang': lang})
    if linkss:
        xbmc.log("linkss", level=xbmc.LOGINFO)
        for link in linkss:
            link = replaceHTMLCodes(link)
            img = re.findall("url\('(.+?)'", link)[0]
            imag = BASEURL2+img if img.startswith('/') else img
            href = parseDOM(link, 'a', ret='href')[0]
            title = parseDOM(link, 'h4')[0]
            odc = parseDOM(link, 'span', attrs={
                           'class': "badge badge-info"})[0]
            out.append({'title': PLchar(title)+'[B][COLOR yellowgreen] [ '+PLchar(odc)+' ][/B][/COLOR]', 'href': PLchar(
                href), 'img': imag+'|User-Agent='+quote(UA)+'&Referer='+BASEURL+'&Cookie='+quote(kuk)})
    return out


def getPlot(title, html):
    plot = ''
    title = title.replace('+', '.')
    if "Fabu" in title:
        title = quote(PLchar(title))
    regex = title+"(.+?)timeline-station"
    try:
        dane = re.findall(regex, html, re.DOTALL)[0]
        plots = re.findall(
            """class="title.+?>(.+?)<.+?class="time">(.+?)<.+?class="time-stop">(.+?)<""", dane, re.DOTALL)
        plot = ''
        if plots:
            for tyt, rozp, zakon in plots:
                zakon = zakon.replace('&nbsp;-', ' -')
                tyt = tyt.replace('&quot;', "''").replace('&#39;', "'")
                plot += '[B][COLOR yellowgreen]'+rozp + \
                    zakon+'[/COLOR] '+tyt+'[/B][CR]'
        else:
            plot = ''
    except:
        plot = ''
        return plot
    return plot


def getHtml():
    res = requests.post('https://m.teleman.pl/profile', data={ 'stations': CONFIG['stations'] }, timeout=30, verify=False)
    html = requests.get('https://m.teleman.pl/timeline', cookies=res.cookies, timeout=30, verify=False).content

    if PY3:
        html = html.decode(encoding='utf-8', errors='strict')
    html = parseDOM(html, 'div', attrs={'class': "timeline"})[0]
    html = html.replace('stations/TVP-1"', 'TVP 1 ONLINE"')
    html = html.replace('stations/TVP-2"', 'TVP 2 ONLINE"')
    html = html.replace('stations/TVN"', 'TVN ONLINE"')
    html = html.replace('stations/Polsat"', 'POLSAT ONLINE"')
    html = html.replace('stations/TV4"', 'TV4 ONLINE"')
    html = html.replace('stations/Puls"', 'PULS ONLINE"')
    html = html.replace('stations/TV6"', 'TV6 ONLINE"')
    html = html.replace('stations/TVN-Siedem"', 'TVN7 ONLINE"')
    html = html.replace('stations/TVN24', 'TVN24 ONLINE')
    html = html.replace('stations/TVP-Info', 'TVP INFO ONLINE')
    html = html.replace('stations/Polsat-News', 'POLSAT NEWS ONLINE')
    html = html.replace('stations/TVN-24-Biznes-i-Swiat', 'TVN24 BIS ONLINE')
    html = html.replace('stations/HBO"', 'HBO ONLINE')
    html = html.replace('stations/HBO2', 'HBO 2 ONLINE')
    html = html.replace('stations/HBO3', 'HBO 3 ONLINE')
    html = html.replace('stations/CanalPlus"', 'CANAL +"')
    html = html.replace('stations/CanalPlus-Sport"', 'CANAL+ SPORT"')
    html = html.replace('stations/CanalPlus-Sport-2"', 'CANAL+ SPORT 2"')
    html = html.replace('stations/CanalPlus-Film', 'CANAL+ FILM ONLINE')
    html = html.replace('stations/Polsat-Sport"', 'POLSAT SPORT ONLINE')
    html = html.replace('stations/Polsat-Sport-Extra',
                        'POLSAT SPORT EXTRA ONLINE')
    html = html.replace('stations/TVP-Sport', 'TVP SPORT ONLINE')
    html = html.replace('stations/nSport', 'nSport ONLINE')
    html = html.replace('stations/Eurosport"', 'EUROSPORT 1 ONLINE')
    html = html.replace('stations/Eurosport-2', 'EUROSPORT 2 ONLINE')
    html = html.replace('stations/Eleven-Sports-1', 'ELEVEN SPORTS 1 ONLINE')
    html = html.replace('stations/Eleven-Sports-2', 'ELEVEN SPORTS 2 ONLINE')
    html = html.replace('stations/Eleven-Sports-3', 'ELEVEN SPORTS 3 ONLINE')
    html = html.replace('stations/Nat-Geo-Wild', 'NAT GEO WILD ONLINE')
    html = html.replace('stations/National-Geographic',
                        'NATIONAL GEOGRAPHIC ONLINE')
   # html=html.replace('/stations/History"','HISTORY ONLINE"')
    html = html.replace('stations/TVP-Historia', 'TVP HISTORIA ONLINE')
    html = html.replace('stations/Discovery-Channel', 'DISCOVERY ONLINE')
    html = html.replace('stations/TVN-Style', 'TVN STYLE ONLINE')
    html = html.replace('stations/Polsat-Film', 'POLSAT FILM ONLINE')
    html = html.replace('stations/Polsat-2', 'POLSAT 2 ONLINE')
    html = html.replace('stations/Cinemax"', 'CINEMAX ONLINE"')
    html = html.replace('stations/Cinemax2', 'CINEMAX 2 ONLINE')
    html = html.replace('stations/Discovery-Historia',
                        'DISCOVERY HISTORIA ONLINE')
    html = html.replace('stations/Discovery-Science',
                        'DISCOVERY SCIENCE ONLINE')
    html = html.replace('stations/Cartoon-Network', 'CARTOON NETWORK ONLINE')
    html = html.replace('stations/TVP-Seriale', 'TVP SERIALE ONLINE')
    html = html.replace('stations/AXN"', 'AXN ONLINE"')
    html = html.replace('stations/FOX-Comedy', 'FOX COMEDY ONLINE')
    html = html.replace('stations/FOX"', 'FOX ONLINE')
    html = html.replace('stations/TNT', 'TNT ONLINE')
    html = html.replace('stations/TTV', 'TTV ONLINE')
    html = html.replace('stations/TV-Republika', 'REPUBLIKA ONLINE')
    html = html.replace('stations/TVN-Turbo', 'TVN TURBO ONLINE')
    html = html.replace('stations/Kino-Polska', 'KINO POLSKA ONLINE')
    html = html.replace('stations/CanalPlus-Family', 'CANAL+ FAMILY ONLINE')
    html = html.replace('stations/CanalPlus-Discovery',
                        'CANAL+ DISCOVERY ONLINE')
    html = html.replace('stations/MTV-Polska', 'MTV ONLINE')
    html = html.replace('stations/Kino TV', 'KINO TV ONLINE')
    html = html.replace('stations/Filmbox-Action', 'FILMBOX ACTION ONLINE')
    html = html.replace('stations/Polsat-Cafe', 'POLSAT CAFE ONLINE')
    html = html.replace('stations/13-Ulica', '13 ULICA ONLINE')
    html = html.replace('stations/SCI-FI', 'SCIFI UNIVERSAL ONLINE')
    html = html.replace('stations/MiniMini', 'MINI MINI ONLINE')
    html = html.replace('stations/TVP-ABC', 'TVP ABC ONLINE')
    html = html.replace('stations/Disney-Channel', 'DISNEY CHANNEL ONLINE')
    html = html.replace('stations/TVP-Rozrywka', 'TVP ROZRYWKA ONLINE')
    html = html.replace('stations/TVP-Polonia', 'TVP POLONIA ONLINE')
    html = html.replace('stations/Superstacja', 'SUPERSTACJA ONLINE')
    html = html.replace('stations/CanalPlus-Seriale', 'CANAL + SERIALE ONLINE')
    html = html.replace('stations/Comedy-Central', 'COMEDY CENTRAL ONLINE')
    html = html.replace('stations/Polsat-Sport-Premium-1',
                        'POLSAT SPORT PREMIUM')
    html = html.replace('stations/Polsat-Sport-Premium-2',
                        'POLSAT SPORT PREMIUM 2')
    html = html.replace('stations/Polsat-Play', 'POLSAT PLAY')
    html = html.replace('stations/Polsat-Sport-News', 'POLSAT SPORT NEWS')

    html = html.replace('/stations/Polsat-Sport-News', 'POLSAT SPORT NEWS')
    html = html.replace('/stations/TVN-Fabula', quote('TVN Fabuła'))
    # html=html.replace(#','Polsat Sport Premium 3')
    # html=html.replace(#','Polsat Sport Premium 4')
    html = html.replace('/stations/Eleven-4', 'ELEVEN SPORTS 4 ONLINE')
    html = html.replace('/stations/Kuchnia-TV', 'KUCHNIA+ ONLINE')
    html = html.replace('/stations/Planete', 'PLANETE+ ONLINE')
    html = html.replace('/stations/TLC', 'TLC ONLINE')
    html = html.replace('/stations/Animal-Planet-HD', 'ANIMAL PLANET ONLINE')
    html = html.replace('/stations/Extreme', 'EXTREM SPORTS ONLINE')
    html = html.replace('/stations/History"', 'History  online"')
    html = html.replace('/stations/Stopklatka-TV', 'STOPKLATKA TV')
    html = html.replace('/stations/Viasat-History', 'VIASAT HISTORY')
    html = html.replace('/stations/Viasat-Explorer', 'POLSAT  VIASAT EXPLORE')
    html = html.replace('/stations/Viasat-Nature', 'POLSAT VIASAT NATURE')
    html = html.replace('/stations/Filmbox-Family', 'FILMBOX FAMILY')
    html = html.replace('/stations/Ale-Kino', 'ALEKINO')

    html = html.replace('/stations/Nat-Geo-People"', 'NAT GEO PEOPLE"')

   # html=html.replace('/stations/Nat-Geo-People"','CANAL+ DISCOVERY"'                        )

    return html


def PLchar(char):
    if type(char) is not str:
        char = char.encode('utf-8')
    char = char.replace('\\u0105', '\xc4\x85').replace('\\u0104', '\xc4\x84')
    char = char.replace('\\u0107', '\xc4\x87').replace('\\u0106', '\xc4\x86')
    char = char.replace('\\u0119', '\xc4\x99').replace('\\u0118', '\xc4\x98')
    char = char.replace('\\u0142', '\xc5\x82').replace('\\u0141', '\xc5\x81')
    char = char.replace('\\u0144', '\xc5\x84').replace('\\u0144', '\xc5\x83')
    char = char.replace('\\u00f3', '\xc3\xb3').replace('\\u00d3', '\xc3\x93')
    char = char.replace('\\u015b', '\xc5\x9b').replace('\\u015a', '\xc5\x9a')
    char = char.replace('\\u017a', '\xc5\xba').replace('\\u0179', '\xc5\xb9')
    char = char.replace('\\u017c', '\xc5\xbc').replace('\\u017b', '\xc5\xbb')
    char = char.replace('&#8217;', "'")
    char = char.replace('&#8211;', "-")
    char = char.replace('&#8230;', "...")
    char = char.replace('&quot;', '"')
    char = char.replace('&#039;', "'").replace('&#39;', "'")
    char = char.replace('Napisy PL', "[COLOR lightblue](napisy pl)[/COLOR]")
    char = char.replace('Lektor PL', "[COLOR lightblue](lektor pl)[/COLOR]")
    char = char.replace('Dubbing PL', "[COLOR lightblue](dubbing pl)[/COLOR]")
    return char


def router(paramstr):
    params = dict(parse_qsl(paramstr))
    mode = params.get('mode', None)
    if mode:
        #mode = params.get('mode', None)

        # if  mode is None:
        #    home()
        if mode == 'listmovies':
            ListMovies(exlink, page)
        elif mode == 'listserials':
            ListSerials(exlink, page)
        elif mode == 'listseasons':
            ListSeasons(exlink)
        elif mode == 'listepisodes':
            ListEpisodes(exlink)
        elif mode == 'listtv':
            ListTv(exlink)
        elif mode == 'listsport':
            ListSport(exlink)
        elif mode == 'getLinks':
            getLinks(exlink)
        elif mode == 'getTvStream':
            getTvStream(exlink)

        elif mode == 'gatunek':
            data = getGatunek(exlink)
            par = exlink.split('|')
            if data:
                label = [x[0].strip() for x in data]
                url = [x[1].strip() for x in data]
                s = xbmcgui.Dialog().select('Wybierz '+par[0], label)
                if s > -1:
                    ListMovies(url[s], 1)
        elif mode == 'gatunektv':
            data = getGatunek(exlink)
            par = exlink.split('|')
            if data:
                label = [x[0].strip() for x in data]
                url = [x[1].strip() for x in data]
                s = xbmcgui.Dialog().select('Wybierz '+par[0], label)
                if s > -1:
                    ListTv(url[s])
        elif mode == 'settings':
            addon.openSettings()
            xbmc.executebuiltin('Container.Refresh()')

        elif mode == '__page__M':
            url = build_url({'mode': 'listmovies', 'foldername': '',
                            'url': exlink, 'page': page, 'hejotvsession': kukz})
            xbmc.executebuiltin('Container.Refresh(%s)' % url)
            xbmcplugin.endOfDirectory(addon_handle, True)

        elif mode == '__page__S':
            url = build_url({'mode': 'listserials', 'foldername': '',
                            'url': exlink, 'page': page, 'hejotvsession': kukz})
            xbmc.executebuiltin('Container.Refresh(%s)' % url)
            xbmcplugin.endOfDirectory(addon_handle, True)

        elif mode == 'search':
            query = xbmcgui.Dialog().input(u'Szukaj, Podaj tytuł filmu',
                                           type=xbmcgui.INPUT_ALPHANUM)
            xbmc.log("Query = {}".format(query), level=xbmc.LOGINFO)
            if query:
                links = search(query.replace(' ', '+'))
                if links:
                    itemz = links
                    items = len(links)
                    mud = 'getLinks'
                    fold = False
                    for f in itemz:
                        if '/series/' in f.get('href'):
                            mud = 'listseasons'
                            fold = True
                        elif '/channel/' in f.get('href'):
                            mud = 'getTvStream'
                        add_item(name=f.get('title'), url=f.get('href'), mode=mud, image=f.get(
                            'img'), folder=fold, infoLabels=f, itemcount=items)
                    xbmcplugin.setContent(addon_handle, 'videos')
                    xbmcplugin.endOfDirectory(addon_handle, True)
                else:
                    s = xbmcgui.Dialog().ok(
                        '[COLOR red]Problem[/COLOR]', 'Brak materiału do wyświetlenia')
    else:
        home()


if __name__ == '__main__':
    router(sys.argv[2][1:])
