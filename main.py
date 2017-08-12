#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os.path
from appfunc import *
import wx
import http.client
from myFrame import *
from ProgressDialog import *
import logging

import GlobalVars as gl

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG, filename=os.getenv("APPDATA") + u"\\Cenchanced\\log.log")

reload(sys)
sys.setdefaultencoding('utf8')

if not os.path.exists(os.getenv("APPDATA") + "\\Cenchanced"):
    os.makedirs(os.getenv("APPDATA") + "\\Cenchanced")

sys.stdout = open(os.getenv("APPDATA") + "\\Cenchanced\\stdout.log", 'w', 0)
sys.stderr = open(os.getenv("APPDATA") + "\\Cenchanced\\stderr.log", 'w', 0)

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

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
    logging.info(u'Инициализация программы...')
    gl.app = wx.App()
    gl.progress_wnd = ProgressDialog(None, u"Progress window")
    gl.progress_wnd.Enable()
    gl.progress_wnd.Destroy()
    gl.wnd = Frame(None, "LOTRO Patcher: Enchanced edition ver. " + gl.VERSION)
    gl.app.MainLoop()
    logging.info(u'Запись конфигурации. Подготовка к выходу из программы')
    writeConfig(gl.cfg, gl.path)
    logging.info(u'Завершение работы программы')
