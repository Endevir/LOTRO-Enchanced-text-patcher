#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import GlobalVars as gl
import webbrowser
import logging
import http.client
import sys

from MainGUI import MainGUI
from LoginGUI import LoginGUI
from SelfPatchGUI import SelfPatchGUI
from UpdateGUI import UpdateGUI
from FaqDialog import FaqDialog


class Frame(wx.Frame):
    def MakeConnection(self):
        # Создание и проверка соединения, а также проверка версии программы
        try:
            gl.server_conn = http.client.HTTPConnection("translate.lotros.ru")
            gl.server_conn.request("GET", u"/pages/easypatcher.html")
            self.resp = gl.server_conn.getresponse()
            self.respdata = str(self.resp.read()).decode('UTF-8')
            version_start = self.respdata.find('<version>') + 9
            version_end = self.respdata.find('</version>')
            self.onsite_version = self.respdata[version_start:version_end]
        except:
            self.ErrorMessage(
                u"Ошибка подключения к серверу, работа программы не может быть продолжена без интернет-соединения :(")
            sys.exit(0)

        if not self.onsite_version == gl.VERSION:
            self.WarningMessage(
                u"Внимание! Данная версия программы устарела! В целях безопасности использование устаревшей версии невозможно... После нажатия кнопки \"ОК\" Вы будете автоматически перенаправлены на страницу загрузки новой версии! Мы очень стараемся сделать программу лучше с каждым обновлением!\n Спасибо за понимание :) ")
            webbrowser.open("http://translate.lotros.ru/pages/easypatcher.html", new=2)
            sys.exit(0)

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(768, 576),
                          style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        self.Centre()
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.panel = wx.Panel(self, -1)
        self.panel.SetBackgroundColour((255, 255, 255))
        bg = wx.Image('bg.jpg', wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        self.bmp = wx.StaticBitmap(parent=self.panel, bitmap=bg, pos=(0, 0), size=(768, 576))
        self.mainPanel = wx.Panel(self.bmp, pos=(0, 80), size=(768, 430))
        self.mainPanel.SetBackgroundColour((255, 255, 255))
        logging.info(u'Инициализация GUI...')
        self.AddGUI()
        self.Show(True)
        self.MakeConnection()

    def StartGame(self, event):
        # Function - uses path to folder with client_local_English.dat, and starts TurbineLauncher.exe from the same folder
        if gl.cfg["DatPath"] == "NULL":
            self.WarningMessage(u"Укажите путь к папке с игрой!")
            return
        execstr = '"' + str(gl.cfg["DatPath"][:-24]) + 'TurbineLauncher.exe" -nosplash -disablePatch -skiprawdownload'

        try:
            import win32api
            win32api.WinExec(execstr)
        except:
            self.WarningMessage(
                u'Не найден файл TurbineLauncher.exe в папке с .dat файлом... Не можем запустить игру :(')

    def OnClickDatButton(self, event):
        if self.dat_dialogue.ShowModal() == wx.ID_OK:
            self.dat_path = self.dat_dialogue.GetPath()
            gl.cfg['DatPath'] = self.dat_path
            if (len(self.dat_path) <= 85):
                self.dat_filetext.SetLabel(self.dat_path)
            else:
                self.dat_filetext.SetLabel(self.dat_path[:85] + "...")

    def Report(self, event):
        webbrowser.open("http://translate.lotros.ru/bugs/add", new=2)

    def AddGUI(self):
        self.MainGUI = MainGUI(self)
        self.LoginGUI = LoginGUI(self)
        self.SelfPatchGUI = SelfPatchGUI(self)
        self.UpdateGUI = UpdateGUI(self)

        # Logo text
        LogoText = wx.StaticText(self.mainPanel, -1, "LOTRO Patcher: Enchanced edition", (0, 0), (768, -1),
                                 wx.ALIGN_CENTER)
        LogoFont = wx.Font(18, wx.FONTFAMILY_SCRIPT, wx.ITALIC, wx.NORMAL)
        LogoText.SetFont(LogoFont)

        # path to client_local_English.dat file
        self.dat_text = wx.StaticText(self.mainPanel, -1, u"1) Файл данных: ", pos=(20, 50), size=(100, -1));
        self.dat_dialogue = wx.FileDialog(self.mainPanel,
                                          u"Укажите путь до файла \"client_local_English.dat\" в папке с игрой", "", "",
                                          "client_local_English.dat")
        self.dat_filetext = wx.StaticText(self.mainPanel, -1,
                                          u"1) Укажите путь до файла \"client_local_English.dat\" в папке с игрой",
                                          pos=(120, 50), size=(500, -1), style=wx.SIMPLE_BORDER)
        self.dat_path = ""
        self.dat_filetext.SetWindowStyleFlag(wx.SIMPLE_BORDER)
        if not gl.cfg["DatPath"] == "NULL":
            self.dat_path = gl.cfg["DatPath"]
            if (len(gl.cfg["DatPath"]) <= 85):
                self.dat_filetext.SetLabel(gl.cfg["DatPath"])
            else:
                self.dat_filetext.SetLabel(gl.cfg["DatPath"][:85] + "...")
            self.dat_dialogue.SetDirectory(gl.cfg["DatPath"][:-24])

        self.dat_button = wx.Button(self.mainPanel, -1, u"Выбрать файл", pos=(625, 45))
        self.Bind(wx.EVT_BUTTON, self.OnClickDatButton, self.dat_button)

        # Field - choose what to do
        self.what_to_do_text = wx.StaticText(self.mainPanel, -1, u"Что будем делать?", pos=(0, 70), size=(500, -1),
                                             style=wx.ALIGN_CENTER)
        self.what_to_do_text.SetFont(
            wx.Font(19, family=wx.FONTFAMILY_DECORATIVE, weight=wx.FONTWEIGHT_NORMAL, style=wx.NORMAL))

        # Buttons - what to do
        self.login = wx.Button(self.mainPanel, -1, u"2) Войти в систему", pos=(20, 130), size=(220, 25))
        self.update = wx.Button(self.mainPanel, -1, u"3) Скачать новые переводы", pos=(265, 130), size=(220, 25))
        self.translate = wx.Button(self.mainPanel, -1, u"Переводить отдельный фрагмент", pos=(20, 160), size=(220, 25))
        self.bug_report = wx.Button(self.mainPanel, -1, u"Писать сообщение об ошибке", pos=(265, 160), size=(220, 25))
        self.return_back = wx.Button(self.mainPanel, -1, u"Основные настройки", pos=(505, 85), size=(220, 25))

        # Describing gui_panel - panel with main content
        self.gui_panel = wx.Panel(self.mainPanel, -1, pos=(20, 190), size=(465, 240), style=wx.SIMPLE_BORDER)
        self.gui_panel.SetBackgroundColour((255, 255, 255))  # for debug it is useful to change color

        # Describing settings_panel - panel with additional settings
        self.setting_panel = wx.Panel(self.mainPanel, -1, pos=(505, 125), size=(220, 230), style=wx.SIMPLE_BORDER)
        self.setting_panel.SetBackgroundColour((255, 255, 255))  # for debug it is useful to change color

        # Button - start the game
        self.startButton = wx.Button(self.mainPanel, -1, u'Запуск игры', pos=(520, 370), size=(200, 35))
        self.startButton.SetFont(
            wx.Font(19, family=wx.FONTFAMILY_DECORATIVE, weight=wx.FONTWEIGHT_NORMAL, style=wx.NORMAL))

        # Binding buttons to actions - show GUI on gui_panel
        self.Bind(wx.EVT_BUTTON, self.LoginGUI.Start, self.login)
        self.Bind(wx.EVT_BUTTON, self.UpdateGUI.Start, self.update)
        self.Bind(wx.EVT_BUTTON, self.SelfPatchGUI.Start, self.translate)
        self.Bind(wx.EVT_BUTTON, self.Report, self.bug_report)
        self.Bind(wx.EVT_BUTTON, self.MainGUI.Start, self.return_back)
        self.Bind(wx.EVT_BUTTON, self.StartGame, self.startButton)
        self.Bind(wx.wx.EVT_CHAR_HOOK, self.onKeyPress)

        self.MainGUI.Start()

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        print keycode
        if keycode == wx.WXK_ESCAPE:
            self.Destroy()
        if keycode == wx.WXK_F1:
            print(u'Нажали F1')
            gl.faq_wnd = FaqDialog(None)
        event.Skip()

    def RemoveGUI(self):
        for child in self.gui_panel.GetChildren():
            child.Destroy()
        for child in self.setting_panel.GetChildren():
            child.Destroy()

    def WarningMessage(self, msg):
        logging.warning(msg)
        dlg = wx.MessageDialog(self, msg, u"Внимание!", wx.OK | wx.ICON_WARNING | wx.STAY_ON_TOP)
        dlg.ShowModal()
        dlg.Destroy()

    def ErrorMessage(self, msg):
        logging.error(msg)
        dlg = wx.MessageDialog(self, msg, u"Ошибка!", wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP)
        print sys.exc_info()[0]
        dlg.ShowModal()
        dlg.Destroy()

    def InformationMessage(self, msg):
        logging.info(msg)
        dlg = wx.MessageDialog(self, msg, u"Уведомление", wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
        dlg.ShowModal()
        dlg.Destroy()

    def CriticalMessage(self, msg):
        logging.critical(msg)
        dlg = wx.MessageDialog(self, msg, u"Критическая ошибка!", wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP)
        dlg.ShowModal()
        dlg.Destroy()
        gl.wnd.Destroy()
