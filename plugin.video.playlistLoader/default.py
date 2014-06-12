# -*- coding: utf-8 -*-
#code by Avigdor 
import urllib, sys, xbmcplugin ,xbmcgui, xbmcaddon, xbmc, os, json

AddonID = 'plugin.video.playlistLoader'
Addon = xbmcaddon.Addon(AddonID)
#localizedString = Addon.getLocalizedString
icon = Addon.getAddonInfo('icon')

addonDir = Addon.getAddonInfo('path').decode("utf-8")

libDir = os.path.join(addonDir, 'resources', 'lib')
sys.path.insert(0, libDir)
import common, chardet

addon_data_dir = os.path.join(xbmc.translatePath("special://userdata/addon_data" ).decode("utf-8"), AddonID)
if not os.path.exists(addon_data_dir):
	os.makedirs(addon_data_dir)
	
playlistsFile = os.path.join(addon_data_dir, "playLists.txt")
tmpListFile = os.path.join(addon_data_dir, 'tempList.txt')
favoritesFile = os.path.join(addon_data_dir, 'favorites.txt')
if  not (os.path.isfile(favoritesFile)):
	f = open(favoritesFile, 'w') 
	f.write('[]') 
	f.close() 
	
def Categories():
	AddDir("[COLOR yellow][B]Add a new list[/B][/COLOR]" , "settings" , 20, os.path.join(addonDir, "resources", "images", "NewList.ico"), isFolder=False)
	AddDir("[COLOR yellow][B]Add a new local-list[/B][/COLOR]" , "settings" , 21, os.path.join(addonDir, "resources", "images", "NewList.ico"), isFolder=False)
	AddDir("[COLOR white][B][Favorites][/B][/COLOR]", "favorites" ,30 ,os.path.join(addonDir, "resources", "images", "bright_yellow_star.png"))
	
	list = common.ReadList(playlistsFile)
	for item in list:
		mode = 1 if item["url"].find(".plx") > 0 else 2
		AddDir("[COLOR blue][{0}][/COLOR]".format(item["name"]).encode('utf-8') ,item["url"], mode, "")

def AddNewList(method = "url"):
	listName = GetKeyboardText("Playlist name").strip()
	if len(listName) < 1:
		return
	
	if method == "url":
		listUrl = GetKeyboardText("Playlist URL").strip()
	else:
		listUrl = xbmcgui.Dialog().browse(int(1), "Choose list", 'myprograms','.plx|.m3u').decode("utf-8")
		if not listUrl:
			return
	
	if len(listUrl) < 1:
		return

	list = common.ReadList(playlistsFile)
	for item in list:
		if item["url"].lower() == listUrl.lower():
			xbmc.executebuiltin('Notification(Playlist Loader, "{0}" already in playlists, 5000, {1})'.format(listName, icon))
			return
	list.append({"name": listName, "url": listUrl})
	if common.SaveList(playlistsFile, list):
		xbmc.executebuiltin("XBMC.Container.Update('plugin://{0}')".format(AddonID))
	
def RemoveFromLists(url):
	list = common.ReadList(playlistsFile)
	for item in list:
		if item["url"].lower() == url.lower():
			list.remove(item)
			if common.SaveList(playlistsFile, list):
				xbmc.executebuiltin("XBMC.Container.Update('plugin://{0}')".format(AddonID))
			break
			
def PlxCategory(url):
	tmpList = []
	list = common.plx2list(url)
	background = list[0]["background"]
	for channel in list[1:]:
		iconimage = "" if not channel.has_key("thumb") else channel["thumb"].decode(chardet.detect(channel["thumb"])["encoding"]).encode("utf-8")
		name = channel["name"].decode(chardet.detect(channel["name"])["encoding"]).encode("utf-8")
		if channel["type"] == 'playlist':
			AddDir("[COLOR blue][{0}][/COLOR]".format(name) ,channel["url"], 1, iconimage, background=background)
		else:
			AddDir(name, channel["url"], 3, iconimage, isFolder=False, background=background)
			tmpList.append({"url": channel["url"], "image": iconimage, "name": name})
			
	common.SaveList(tmpListFile, tmpList)
			
def m3uCategory(url):	
	tmpList = []
	list = common.m3u2list(url)
	for channel in list:
		iconimage = ""
		#iconimage = "" if not channel.has_key("tvg_logo") else channel["tvg_logo"]
		name = channel["display_name"].decode(chardet.detect(channel["display_name"])["encoding"]).encode("utf-8")
		AddDir(name ,channel["url"], 3, iconimage, isFolder=False)
		tmpList.append({"url": channel["url"], "image": iconimage, "name": name})
		
	common.SaveList(tmpListFile, tmpList)
	
def PlayUrl(name, url, iconimage=None):
	print '--- Playing "{0}". {1}'.format(name, url)
	listitem = xbmcgui.ListItem(path=url, thumbnailImage=iconimage)
	listitem.setInfo(type="Video", infoLabels={ "Title": name })
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)

def AddDir(name, url, mode, iconimage, description="", isFolder=True, background=None):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)

	liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description})
	if background:
		liz.setProperty('fanart_image', background)
	if mode == 1 or mode == 2:
		#items = []
		#items.append(('Remove from Playlist Loader', 'XBMC.RunPlugin({0}?url={1}&mode=22)'.format(sys.argv[0], urllib.quote_plus(url), iconimage, name)))
		liz.addContextMenuItems(items = [('Remove from Playlist Loader', 'XBMC.RunPlugin({0}?url={1}&mode=22)'.format(sys.argv[0], urllib.quote_plus(url)))])
	elif mode == 3:
		liz.setProperty('IsPlayable', 'true')
		liz.addContextMenuItems(items = [('Add to Playlist Loader favorites', 'XBMC.RunPlugin({0}?url={1}&mode=31&iconimage={2}&name={3})'.format(sys.argv[0], urllib.quote_plus(url), iconimage, name))])
	elif mode == 32:
		liz.setProperty('IsPlayable', 'true')
		liz.addContextMenuItems(items = [('Remove from Playlist Loader favorites', 'XBMC.RunPlugin({0}?url={1}&mode=33&iconimage={2}&name={3})'.format(sys.argv[0], urllib.quote_plus(url), iconimage, name))])
		
	xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder)

def GetKeyboardText(title = "", defaultText = ""):
	keyboard = xbmc.Keyboard(defaultText, title)
	keyboard.doModal()
	text =  "" if not keyboard.isConfirmed() else keyboard.getText()
	return text

def AddFavorites(url, iconimage, name):
	favList = common.ReadList(favoritesFile)
	for item in favList:
		if item["url"].lower() == url.lower():
			xbmc.executebuiltin("Notification('Playlist Loader', '{0}' is already in favorites, 5000, {1})".format(name, icon))
			return
    
	list = common.ReadList(tmpListFile)	
	for channel in list:
		if channel["name"].lower() == name.lower():
			url = channel["url"]
			iconimage = channel["image"]
			break
			
	if not iconimage:
		iconimage = ""
		
	data = {"url": url, "image": iconimage, "name": name}
	
	favList.append(data)
	common.SaveList(favoritesFile, favList)
	xbmc.executebuiltin("Notification('Playlist Loader', '{0}' added to favorites, 5000, {1})".format(name, icon))
	
def ListFavorites():
	AddDir("[COLOR yellow][B]Add a new channel[/B][/COLOR]", "favorites" ,34 ,os.path.join(addonDir, "resources", "images", "bright_yellow_star.png"), isFolder=False)
	list = common.ReadList(favoritesFile)
	for channel in list:
		name = channel["name"].encode("utf-8")
		iconimage = channel["image"].encode("utf-8")
		AddDir(name, channel["url"], 32, iconimage, isFolder=False) 
		
def RemoveFavorties(url):
	list = common.ReadList(favoritesFile) 
	for channel in list:
		if channel["url"].lower() == url.lower():
			list.remove(channel)
			break
			
	common.SaveList(favoritesFile, list)
	xbmc.executebuiltin("XBMC.Container.Update('plugin://{0}?mode=30&url=favorites')".format(AddonID))
	
def AddNewFavortie():
	chName = GetKeyboardText("Channel name").strip()
	if len(chName) < 1:
		return
	chUrl = GetKeyboardText("Channel URL").strip()
	if len(chUrl) < 1:
		return
		
	favList = common.ReadList(favoritesFile)
	for item in favList:
		if item["url"].lower() == url.lower():
			xbmc.executebuiltin("Notification('Playlist Loader', '{0}' is already in favorites, 5000, {1})".format(chName, icon))
			return
			
	data = {"url": chUrl, "image": "", "name": chName}
	
	favList.append(data)
	if common.SaveList(favoritesFile, favList):
		xbmc.executebuiltin("XBMC.Container.Update('plugin://{0}?mode=30&url=favorites')".format(AddonID))
		
def get_params():
	param = []
	paramstring = sys.argv[2]
	if len(paramstring) >= 2:
		params = sys.argv[2]
		cleanedparams = params.replace('?','')
		if (params[len(params)-1] == '/'):
			params = params[0:len(params)-2]
		pairsofparams = cleanedparams.split('&')
		param = {}
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			if (len(splitparams)) == 2:
				param[splitparams[0].lower()] = splitparams[1]
	return param

	
params=get_params()
url=None
name=None
mode=None
iconimage=None
description=None

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.unquote_plus(params["name"])
except:
	pass
try:
	iconimage = urllib.unquote_plus(params["iconimage"])
except:
	pass
try:        
	mode = int(params["mode"])
except:
	pass
try:        
	description = urllib.unquote_plus(params["description"])
except:
	pass

	
if mode == None or url == None or len(url) < 1:
	Categories()
elif mode == 1:
	PlxCategory(url)
elif mode == 2:
	m3uCategory(url)
elif mode == 3 or mode == 32:
	PlayUrl(name, url, iconimage)
elif mode == 20:
	AddNewList("url")
elif mode == 21:
	AddNewList("file")
elif mode == 22:
	RemoveFromLists(url)
elif mode == 30:
	ListFavorites()
elif mode == 31: 
	AddFavorites(url, iconimage, name) 
elif mode == 33:
	RemoveFavorties(url)
elif mode == 34:
	AddNewFavortie()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
