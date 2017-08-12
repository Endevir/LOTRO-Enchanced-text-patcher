#!/usr/bin/env python
# -*- coding: utf-8 -*-

from appfunc import *
import time
import GlobalVars as gl
import logging
from ProgressDialog import *

class UpdateGUI:
    def __init__(self, parent):
        self.wnd = parent
        pass

    def Start(self, event):
        if gl.cfg["DatPath"] == "NULL":
            self.wnd.WarningMessage(u"Сначала укажите путь к папке и игрой!")
            return
        if gl.cfg["UserName"] == "NULL" or gl.cfg["UserGroup"] == "NULL":
            self.wnd.WarningMessage(u"Сначала войдите в систему переводов!")
            return
        self.wnd.RemoveGUI()

        if gl.cfg["UserGroup"] == "translator":
            self.text0 = wx.StaticText(self.wnd.gui_panel, -1, u"Вы вошли как переводчик, " + str(gl.cfg[
                                                                                                  "UserNick"]) + u"\n Вы можете скачать и установить все утвержденные переводы,\nили свои ещё переводы.",
                                       pos=(0, 3), size=(450, -1), style=wx.ALIGN_CENTER)
        elif gl.cfg["UserGroup"] == "moderator" or gl.cfg["UserGroup"] == "developer" or gl.cfg[
            "UserGroup"] == "administrator":
            self.text0 = wx.StaticText(self.wnd.gui_panel, -1, u"Вы - бог всея переводов, " + str(gl.cfg[
                                                                                                  "UserNick"]) + u"\n Вы можете скачать и установить тексты,\n переведенные или утвержденные любым пользователем: ",
                                       pos=(0, 3), size=(450, -1), style=wx.ALIGN_CENTER)
            self.rb4 = wx.RadioButton(self.wnd.gui_panel, -1, u"Мои тексты", (30, 153), style=wx.RB_GROUP)
            self.rb5 = wx.RadioButton(self.wnd.gui_panel, -1, u"Все тексты", (30, 173))
            self.rb6 = wx.RadioButton(self.wnd.gui_panel, -1, u"Тексты пользователя: ", (30, 193))
            self.input3 = wx.TextCtrl(self.wnd.gui_panel, -1, u"", pos=(176, 190), size=(140, 19))

        self.text1 = wx.StaticText(self.wnd.gui_panel, -1, u"Скачать и установить тексты переводов за:", pos=(10, 60),
                                   style=wx.ALIGN_CENTER)
        self.rb0 = wx.RadioButton(self.wnd.gui_panel, -1, u"Последний час", (30, 80), style=wx.RB_GROUP)
        self.rb1 = wx.RadioButton(self.wnd.gui_panel, -1, u"Последние сутки", (150, 80))
        self.rb2 = wx.RadioButton(self.wnd.gui_panel, -1, u"Последнюю неделю", (30, 100))
        self.rb3 = wx.RadioButton(self.wnd.gui_panel, -1, u"В период между датами: ", (30, 120))
        if gl.cfg["UserGroup"] == "translator":
            self.rb41 = wx.RadioButton(self.wnd.gui_panel, -1, u"Все последние утвержденные тексты", (30, 160))
        self.input1 = wx.TextCtrl(self.wnd.gui_panel, -1, u"ДД-ММ-ГГГГ", pos=(190, 118), size=(90, 19))
        self.text6 = wx.StaticText(self.wnd.gui_panel, -1, u" - ", pos=(285, 120), style=wx.ALIGN_CENTER)
        self.input2 = wx.TextCtrl(self.wnd.gui_panel, -1, u"ДД-ММ-ГГГГ", pos=(300, 118), size=(90, 19))
        self.text7 = wx.StaticText(self.wnd.gui_panel, -1,
                                   u"-------------------------------------------------------------------------------",
                                   pos=(0, 137), size=(450, -1), style=wx.ALIGN_CENTER)

        if gl.cfg["UserGroup"] == "moderator" or gl.cfg["UserGroup"] == "developer" or gl.cfg[
            "UserGroup"] == "administrator":
            self.button_apply = wx.Button(self.wnd.gui_panel, -1, u'Скачать и установить', pos=(150, 210))
        else:
            self.button_apply = wx.Button(self.wnd.gui_panel, -1, u'Скачать и установить', pos=(150, 190))
        self.wnd.Bind(wx.EVT_BUTTON, self.Update, self.button_apply)

    def Update(self, event):
        logging.info(u'Инициализация потока обновления...')
        # Function - starts update process. Creating dialog window, showing process of installation, and starting new thread of updating
        gl.progress_wnd = ProgressDialog(None, u"Progress window")
        gl.progress_wnd.Enable()
        t = threading.Thread(target=self.StartUpdate)
        t.daemon = True
        t.start()

    def StartUpdate(self):
        # Function - Updates texts...

        # Doing the preparations
        gl.progress_wnd.UpdateStageText(u"Инициализация обновления...")
        self.starttime = -1
        self.endtime = -1
        self.uname = ""

        # Receiving information from buttons at UpdateGUI

        if str(self.rb0.GetValue()) == "True":
            # Using "last hour"
            self.starttime = int(time.time()) - 60 * 60
            self.endtime = int(time.time())
        elif str(self.rb1.GetValue()) == "True":
            # Using "last day"
            self.starttime = int(time.time()) - 60 * 60 * 24
            self.endtime = int(time.time())
        elif str(self.rb2.GetValue()) == "True":
            # Using "last week"
            self.starttime = int(time.time()) - 60 * 60 * 24 * 7
            self.endtime = int(time.time())
        elif str(self.rb3.GetValue()) == "True":
            # Using user-defined date. Formatting date from field to timestamp
            try:
                self.starttime = int(time.mktime(time.strptime(self.input1.GetValue(), '%d-%m-%Y')))
                self.endtime = int(time.mktime(time.strptime(self.input2.GetValue(), '%d-%m-%Y')))
            except:
                self.wnd.WarningMessage(u"Неверный формат даты!")
                return

        if gl.cfg["UserGroup"] == "translator":
            if str(self.rb41.GetValue()) == "True":
                # Getting last approved updates from all users (only for translators)
                self.starttime = int(gl.cfg["LastUpdateTime"])
                self.endtime = int(time.time())
                self.uname = "All"
                gl.cfg["LastUpdateTime"] = self.endtime
            else:
                self.uname = gl.cfg["UserNick"]
        else:
            # Getting information about person, whose texts will be downloaded (available only for moders|developers|admins)
            if str(self.rb4.GetValue()) == "True":
                # "My texts"
                self.uname = gl.cfg["UserNick"]
            elif str(self.rb5.GetValue()) == "True":
                # "All texts"
                self.uname = "All"
            elif str(self.rb6.GetValue()) == "True":
                # "Texts from current person"
                self.uname = self.input3.GetValue()

        logging.info(u"Получаем тексты переводов пользователя " + self.uname + " :\n")

        # Creating patch with approved texts, translated by person
        self.CreatePatch("1", "translated")

        if not (self.uname == "All" and gl.cfg["UserGroup"] == "translator"):
            # Creating patch with not-approved texts. Translators can only get all approved texts...
            self.CreatePatch("0", "translated")

        if not (self.uname == "All" or gl.cfg["UserGroup"] == "translator"):
            # Creating patch with approved by user texts. This shouldn't do anything if person is translator, or "All"
            logging.info(u"Получаем тексты, утвержденные пользователем " + self.uname + " :\n")
            self.CreatePatch("1", "approved")

        # Destroying dialog window, when patch applied.
        gl.progress_wnd.Disable()
        gl.progress_wnd.Destroy()
        self.wnd.InformationMessage(u'Установка текстов завершена.\nПодробности см. в окне логов')

    def CreatePatch(self, approved, mtype):
        # mtype = "translated"|"approved". Переведенные или утвержденные пользователем тексты соответственно
        # approved = 0|1 - Получение неутвержденных/утвержденных текстов
        if approved == "1":
            apptext = "утвержденных текстов"
        else:
            apptext = "неутвержденных текстов"

        if mtype == "translated":
            gl.progress_wnd.UpdateStageText(u"Получение данных " + apptext + "...")
            if self.uname == "All":
                gl.server_conn.request("GET", u"/groupware/get1/" + str(self.starttime) + u"?to=" + str(
                    self.endtime) + "&success=" + str(approved))
            else:
                gl.server_conn.request("GET", u"/groupware/get1/" + str(self.starttime) + u"?to=" + str(
                    self.endtime) + u"&translator=" + urllib.quote(self.uname.encode('utf-8')) + "&success=" + str(
                    approved))
            self.resp = gl.server_conn.getresponse()
            self.respdata = str(self.resp.read()).decode('UTF-8')
        elif mtype == "approved":
            gl.server_conn.request("GET", u"/groupware/get1/" + str(self.starttime) + u"?to=" + str(
                self.endtime) + "&moder=" + urllib.quote(self.uname.encode('utf-8')))
            self.resp = gl.server_conn.getresponse()
            self.respdata = str(self.resp.read()).decode('UTF-8')

        gl.progress_wnd.UpdateStageText(u"Формирование патча " + apptext + "...")
        tmp = self.respdata.split('\r\n')
        for i in range(len(tmp)):
            tmp[i] = tmp[i].split('||')

        kol = 0
        logging.info(u"Формируем данные патча " + apptext + "...")

        if (os.path.exists(gl.patchpath)):
            os.remove(gl.patchpath)
        progress_str = "None"

        for i in tmp:
            newstr = "Готово " + str(int(kol / float(len(tmp)) * 100)) + "% данных...\n"
            if not progress_str == newstr:
                gl.progress_wnd.UpdatePercent(int(kol / float(len(tmp)) * 100))
            if len(i) == 5 and i[4] == approved:
                try:
                    AddOneStringToPatch(i[0], i[1], i[2], i[3])
                except:
                    logging.critical("НЕ СМОГЛИ ПРОПАТЧИТЬ СТРОКУ!!!:" + i[0] + " " + i[1] + " " + i[2] + " " + i[3])
                kol += 1

        gl.progress_wnd.UpdateStageText(u"Установка патча " + apptext + " ...")
        if kol > 0:
            logging.info(u"Получено " + str(kol) + u" " + apptext + u".\n")
            PatchFile(self.wnd.dat_path)
        else:
            logging.info(u"Получено 0 " + apptext + ". Ничего не делаем...\n###################\n")
