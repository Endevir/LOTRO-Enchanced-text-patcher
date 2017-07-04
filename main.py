#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os.path
from appfunc import *
import wx
import http.client
from myFrame import *

import GlobalVars as gl

reload(sys)  
sys.setdefaultencoding('utf8')
sys.stdout = open(os.getenv("APPDATA") + "\\Cenchanced\\stdout.log", 'a', 0)
sys.stderr = open(os.getenv("APPDATA") + "\\Cenchanced\\stderr.log", 'a', 0)
#sys.stdout = os.fdopen(open(os.getenv("APPDATA") + "\\Cenchanced\\stdout.log", 'w'), 0)
#sys.stderr = os.fdopen(open(os.getenv("APPDATA") + "\\Cenchanced\\stderr.log", 'w'), 0)
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

gl.LastPatchTime = 0
gl.logpath = os.getenv("APPDATA") + "\\Cenchanced\\log.log"
gl.path = os.getenv("APPDATA") + "\\Cenchanced\\config.cc"
gl.patchpath = os.getenv("APPDATA") + "\\Cenchanced\\temp_patch.db"
gl.cfg = parseConfig(gl.path)
gl.VERSION = "0.99"


if not gl.VERSION == gl.cfg["Version"]:
    writeBaseConfig()
    gl.cfg = parseConfig(gl.path)
    gl.cfg["Version"] = gl.VERSION

gl.server_conn = http.client.HTTPConnection("translate.lotros.ru")

if __name__ == '__main__':
    gl.app = wx.App()
    gl.progress_wnd = ProgressDialog(None, u"Progress window")
    gl.progress_wnd.Enable()
    gl.progress_wnd.Destroy()
    gl.wnd = Frame(None, "LOTRO Patcher: Enchanced edition ver. " + gl.VERSION)
    gl.app.MainLoop()
    writeConfig(gl.cfg, gl.path)

