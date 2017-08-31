#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import logging
import shutil
import wx

from ProgressDialog import ProgressDialog
from FaqDialog import FaqDialog
from Frame import Frame
import GlobalVars as gl
from datetime import datetime


def parseConfig(name):
    if not os.path.isfile(name):
        writeBaseConfig()
    fin = open(name, 'r')
    line = fin.readline()
    res = dict()
    while (line):
        if ('=' in line):
            line = line.split('=')
            res[line[0]] = line[1][:-1]
        line = fin.readline()
    fin.close()
    return res


def enhash(str):
    import hashlib
    return hashlib.md5(str.encode("utf-8")).hexdigest()


def writeConfig(mdict, name):
    fout = open(name, 'w')
    for pair in mdict.items():
        fout.write(str(pair[0]) + '=' + str(pair[1]) + '\n')
    fout.close()


def writeBaseConfig():
    mdict = dict()
    mdict["Version"] = "NULL"
    mdict["DatPath"] = "NULL"
    mdict["UserName"] = "NULL"
    mdict["UserNick"] = "NULL"
    mdict["LoginTime"] = "NULL"
    mdict["UserGroup"] = "NULL"
    mdict["OpenFAQ"] = "True"
    mdict["LastUpdateTime"] = "1000000"
    mdict["ForceSaveLogin"] = "False"
    writeConfig(mdict, gl.path)


def BaseInitialization():
    # Подготовка к запуску программы, создание папки конфигурации и файлов логов, перенаправление стандартного вывода
    reload(sys)
    sys.setdefaultencoding('utf8')
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)
    if not os.path.exists(os.getenv("APPDATA") + "\\Cenchanced"):
        os.makedirs(os.getenv("APPDATA") + "\\Cenchanced")

    # Открытие файлов логов, перенаправление stdout и stderr в файлы
    gl.fh = logging.FileHandler(filename=os.getenv("APPDATA") + u"\\Cenchanced\\log.log")
    logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG)
    gl.fh.setFormatter(logging.Formatter(u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'))
    logging.getLogger().addHandler(gl.fh)

    sys.stdout = open(os.getenv("APPDATA") + "\\Cenchanced\\stdout.log", 'a', 0)
    sys.stderr = open(os.getenv("APPDATA") + "\\Cenchanced\\stderr.log", 'a', 0)
    current_time = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")

    logging.info(current_time + u"Starting new instance of application")
    sys.stderr.write(current_time.decode("utf8") + "Starting new instance of application\n")
    print(current_time + u"\nStarting new instance of application")


def InitializeVariables():
    # Инициализация базовых путей и константных переменных
    gl.path = os.getenv("APPDATA") + "\\Cenchanced\\config.cc"
    gl.patchpath = os.getenv("APPDATA") + "\\Cenchanced\\temp_patch.db"
    gl.cfg = parseConfig(gl.path)
    gl.VERSION = "1.09"


def CheckVersion():
    # Проверка совместимости текущей версии программы с файлом конфигурации
    if not gl.VERSION == gl.cfg["Version"]:
        writeBaseConfig()
        gl.cfg = parseConfig(gl.path)
        gl.cfg["Version"] = gl.VERSION


def InitializeGUI():
    gl.app = wx.App()
    gl.progress_wnd = ProgressDialog(None, u"Progress window")
    gl.progress_wnd.Enable()
    gl.progress_wnd.Disable()
    gl.progress_wnd.Destroy()

    gl.wnd = Frame(None, "LOTRO Patcher: Enchanced edition ver. " + gl.VERSION)

    if gl.cfg["OpenFAQ"] == "True":
        gl.faq_wnd = FaqDialog(None)
    gl.app.MainLoop()


def StopApplication():
    logging.info(u'Запись конфигурации. Подготовка к выходу из программы')
    writeConfig(gl.cfg, gl.path)
    logging.info(u'Завершение работы программы')

    if gl.cfg.has_key("DELETE_ALL") and gl.cfg["DELETE_ALL"]:
        logging.getLogger().removeHandler(gl.fh)
        logging.shutdown()
        sys.stdout.close()
        sys.stderr.close()

        shutil.rmtree(os.getenv("APPDATA") + "\\Cenchanced")

        dlg = wx.MessageDialog(None, u'Все данные программы успешно удалены', u"Информация",
                               wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
        dlg.ShowModal()
        dlg.Destroy()


if __name__ == '__main__':
    BaseInitialization()
    logging.info(u'Инициализация программы...')
    InitializeVariables()
    logging.info(u'Проверка версии программы...')
    CheckVersion()
    logging.info(u'Инициализация пользовательского интерфейса...')
    InitializeGUI()
    logging.info(u'Подготовка к выходу из программы...')
    StopApplication()
