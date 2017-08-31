#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import GlobalVars as gl
import wx
import logging


class LoginGUI():
    def __init__(self, parent):
        self.wnd = parent

    def DoPreparations(self):
        # Проверка непредвиденного поведения и выход
        if gl.cfg["DatPath"] == "NULL":
            self.wnd.WarningMessage(u"Сначала укажите путь к папке с игрой!")
            return -1

    def Start(self, event=None):
        if self.DoPreparations() == -1:
            return

        self.wnd.RemoveGUI()
        self.text0 = wx.StaticText(self.wnd.gui_panel, -1,
                                   u"Вы не вошли в систему!\n Войдите, используя e-mail и пароль от сайта transtale.lotros.ru",
                                   pos=(0, 10), size=(450, -1), style=wx.ALIGN_CENTER)
        self.text0.SetFont(wx.Font(10, family=wx.FONTFAMILY_SWISS, weight=wx.FONTWEIGHT_NORMAL, style=wx.NORMAL))
        self.UserName = ""

        if gl.cfg["UserName"] and not gl.cfg["UserName"] == "NULL" and gl.cfg["LoginTime"] and not gl.cfg[
            "LoginTime"] == "NULL":
            if int(time.time()) - int(gl.cfg["LoginTime"]) > 86400 and gl.cfg["ForceSaveLogin"] == "false":
                gl.cfg["UserName"] = "NULL"
                gl.cfg["LoginTime"] = "NULL"
                gl.cfg["UserGroup"] = "NULL"
                gl.cfg["UserNick"] = "NULL"
            if not gl.cfg["LoginTime"] == "NULL":
                self.UserName = gl.cfg["UserName"]

        if self.UserName:
            if gl.cfg["UserGroup"] == "translator":
                self.text0.SetLabel(u"Вы вошли как переводчик " + gl.cfg["UserNick"].encode(
                    'utf-8') + u"!\n Вы можете перезайти, используя другие e-mail и пароль от сайта transtale.lotros.ru")
            else:
                self.text0.SetLabel(u"Вы вошли как модератор " + gl.cfg["UserNick"].encode(
                    'utf-8') + u"!\n Вы можете перезайти, используя другие e-mail и пароль от сайта transtale.lotros.ru")

        self.text_invitation = wx.StaticText(self.wnd.gui_panel, -1, u"Войти в систему: ", pos=(0, 60), size=(450, -1),
                                             style=wx.ALIGN_CENTER)
        self.text_invitation.SetFont(
            wx.Font(11, family=wx.FONTFAMILY_SWISS, weight=wx.FONTWEIGHT_NORMAL, style=wx.NORMAL))

        self.UserName_text = wx.StaticText(self.wnd.gui_panel, -1, u"E-mail: ", pos=(20, 90))
        self.UserName_input = wx.TextCtrl(self.wnd.gui_panel, -1, "", pos=(100, 90), size=(150, 20))

        self.password_text = wx.StaticText(self.wnd.gui_panel, -1, u"Пароль: ", pos=(20, 120))
        self.password_input = wx.TextCtrl(self.wnd.gui_panel, -1, "", pos=(100, 120), size=(150, 20),
                                          style=wx.TE_PASSWORD)

        self.login_button = wx.Button(self.wnd.gui_panel, -1, u'Войти', pos=(150, 150))
        self.wnd.Bind(wx.EVT_BUTTON, self.Login, self.login_button)

        self.SetupSettingsPanel()

    def SetupSettingsPanel(self):
        self.cb1 = wx.CheckBox(self.wnd.setting_panel, label=u'Запомнить данные пользователя', pos=(5, 10))
        if gl.cfg["ForceSaveLogin"] == "True":
            self.cb1.SetValue(True)

        self.but1 = wx.Button(self.wnd.setting_panel, label=u'Выйти с этого аккаунта', pos=(5, 40), size=(210, -1))

        self.wnd.Bind(wx.EVT_CHECKBOX, self.ChangeForceSaveLoginOption, self.cb1)
        self.wnd.Bind(wx.EVT_BUTTON, self.ExitAccount, self.but1)

    def ChangeForceSaveLoginOption(self, event=None):
        gl.cfg["ForceSaveLogin"] = str(self.cb1.GetValue())
        logging.info(u"Смена состояния параметра ForceSaveLogin на " + gl.cfg["ForceSaveLogin"])

    def ExitAccount(self, event=None):
        if gl.cfg["UserName"] == "NULL":
            self.wnd.InformationMessage(u"Вход в аккаунт не был выполнен")
            return
        gl.cfg["UserName"] = "NULL"
        gl.cfg["LoginTime"] = "NULL"
        gl.cfg["UserGroup"] = "NULL"
        gl.cfg["UserNick"] = "NULL"
        self.Start()
        self.wnd.InformationMessage(u"Вы успешно вышли из аккаунта")

    def Login(self, event):
        # Function - logins user to the application via server controls
        self.nUserName = self.UserName_input.GetValue()  # New username
        self.npassword = self.password_input.GetValue()  # New password

        # Sending request to server
        gl.server_conn.request("GET",
                               u"/auth/autologin?logout=1&email=" + self.nUserName + u"&password=" + self.npassword)
        self.resp = gl.server_conn.getresponse()
        self.respdata = self.resp.read()

        # self.respdata = "" when user is not in privileged group
        # self.respdata = %GROUPNAME%, when login is successfull
        # self.respdata = "null", when authentification fails

        if not self.respdata:
            self.wnd.WarningMessage(
                u"Кажется, вы не принадлежите команде переводчиков lotro... и поэтому вам недоступны многие функции программы. Но вы всегда можете присоединиться и стать переводчиком или модератором-тестировщиком!\nИли это просто ошибка подключения к серверу :)")

        if self.respdata and not self.respdata == "null":
            tmp = self.respdata.split("||")
            gl.cfg["UserName"] = self.nUserName
            gl.cfg["LoginTime"] = str(int(time.time()))
            gl.cfg["UserGroup"] = tmp[0]
            gl.cfg["UserNick"] = tmp[1]

            self.UserName = self.nUserName
            self.Start(None)

        elif self.respdata == "null":
            self.wnd.WarningMessage(u"Неправильный e-mail или пароль.")
