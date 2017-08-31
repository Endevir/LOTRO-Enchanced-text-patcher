#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import sqlite3
import os.path
import logging
import threading
import time
import urllib

from patchimari import PATCH_IT
import GlobalVars as gl

from ProgressDialog import ProgressDialog


def updateContent(str):
    str = str.replace('"', '\'')
    str = str.replace('\\\\', '\\')
    return str


def GetStringDataFromServer(file_id, gossip_id):
    gl.server_conn.request("GET", u"/groupware/getitem/" + str(file_id) + "/" + str(gossip_id))
    resp = gl.server_conn.getresponse()
    return str(resp.read()).decode('UTF-8')


def RemovePatchFile():
    if (os.path.exists(gl.patchpath)):
        os.remove(gl.patchpath)


def ResetOneString(file_id, gossip_id, dat_file):
    RemovePatchFile()
    data = GetStringDataFromServer(file_id, gossip_id)
    data = data.split("||")
    AddOneStringToPatch(data[0], data[1], data[2], data[3], data[4])
    PatchFile(dat_file)


def PatchOneString(file_id, gossip_id, content, args_order, dat_file):
    RemovePatchFile()
    data = GetStringDataFromServer(file_id, gossip_id)
    data = data.split("||")
    try:
        args_id = data[4]
    except:
        gl.wnd.ErrorMessage(u"Неверный id файла или id фрагмента.. Не могу продолжить обновление :(")
        return 0
    AddOneStringToPatch(file_id, gossip_id, content, args_order, args_id)
    kol = PatchFile(dat_file)
    gl.wnd.InformationMessage(u"Установлен перевод " + str(kol) + u" строк.")


def PatchFile(dat_file):
    kol = PATCH_IT(gl.patchpath, dat_file)
    RemovePatchFile()
    return kol


def AddOneStringToPatch(file_id, gossip_id, content, args_order, args_id):
    if args_id == "NULL":
        args_order = "Null"
        args_id = "Null"
    elif args_order == "":
        for i in range(len(args_id.split('-')) - 1):
            args_order += str(i + 1) + "-"
        args_order += str(len(args_id.split('-')))

    content = updateContent(content)

    if not os.path.exists(gl.patchpath):
        con = sqlite3.connect(gl.patchpath)
        cur = con.cursor()
        cur.execute(
            'CREATE TABLE text_files (file_id INTEGER, gossip_id INTEGER, content TEXT, args_order TEXT, args_id TEXT)')
        con.commit()
    try:
        con = sqlite3.connect(gl.patchpath)
        cur = con.cursor()
        cur.execute(
            'INSERT INTO text_files (file_id, gossip_id, content, args_order, args_id) VALUES("' + file_id + '", "' + gossip_id + '", "' + content + '", "' + args_order + '", "' + args_id + '")')
        con.commit()
        con.close()
    except:
        print(
        'INSERT INTO text_files (file_id, gossip_id, content, args_order, args_id) VALUES("' + file_id + '", "' + gossip_id + '", "' + content + '", "' + args_order + '", "' + args_id + '")')
        gl.wnd.ErrorMessage(u"Ошибка создания базы данных патча!")
        logging.critical(
            u"Ошибка формирования базы данных патча с файлом: " + str(file_id) + " " + str(gossip_id) + " " + str(
                content) + " " + str(args_order) + " " + str(args_id))
        return -1


class UpdateGUI:
    def __init__(self, parent):
        self.wnd = parent
        pass

    def DoPreparations(self):
        # Проверка непредвиденного поведения и выход
        if gl.cfg["DatPath"] == "NULL":
            self.wnd.WarningMessage(u"Сначала укажите путь к папке и игрой!")
            return -1
        if gl.cfg["UserName"] == "NULL" or gl.cfg["UserGroup"] == "NULL":
            self.wnd.WarningMessage(u"Сначала войдите в систему переводов!")
            return -1

    def SetWelcomeMessage(self):
        if gl.cfg["UserGroup"] == "translator":
            self.text0 = wx.StaticText(self.wnd.gui_panel, -1, u"Вы вошли как переводчик, " + str(gl.cfg[
                                                                                                      "UserNick"]) + u"\n Вы можете скачать и установить все утвержденные переводы,\nа также свои ещё не утвержденные переводы.",
                                       pos=(0, 3), size=(450, -1), style=wx.ALIGN_CENTER)

        elif gl.cfg["UserGroup"] == "moderator" or gl.cfg["UserGroup"] == "developer" or gl.cfg[
            "UserGroup"] == "administrator":
            self.text0 = wx.StaticText(self.wnd.gui_panel, -1, u"Вы - бог всея переводов, " + str(gl.cfg[
                                                                                                      "UserNick"]) + u"\n Вы можете скачать и установить тексты,\n переведенные или утвержденные любым пользователем: ",
                                       pos=(0, 3), size=(450, -1), style=wx.ALIGN_CENTER)

    def AddModeratorButtons(self):
        self.rb4 = wx.RadioButton(self.wnd.gui_panel, -1, u"Мои тексты", (30, 153), style=wx.RB_GROUP)
        self.rb5 = wx.RadioButton(self.wnd.gui_panel, -1, u"Все тексты", (30, 173))
        self.rb6 = wx.RadioButton(self.wnd.gui_panel, -1, u"Тексты пользователя: ", (30, 193))
        self.input3 = wx.TextCtrl(self.wnd.gui_panel, -1, u"", pos=(176, 190), size=(140, 19))

    def SetButtons(self):
        if gl.cfg["UserGroup"] == "moderator" or gl.cfg["UserGroup"] == "developer" or gl.cfg[
            "UserGroup"] == "administrator":
            self.AddModeratorButtons()
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

    def Start(self, event):
        if self.DoPreparations() == -1:
            return
        self.wnd.RemoveGUI()
        self.SetWelcomeMessage()
        self.SetButtons()

    def Update(self, event):
        logging.info(u'Инициализация потока обновления...')
        # Function - starts update process. Creating dialog window, showing process of installation, and starting new thread of updating
        gl.progress_wnd = ProgressDialog(None, u"Progress window")
        gl.progress_wnd.Enable()
        t = threading.Thread(target=self.StartUpdate)
        t.daemon = True
        t.start()

    def GetRequestedTimeValue(self):
        self.starttime = -1
        self.endtime = -1
        self.uname = ""

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

    def GetRequestedUserData(self):
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

    def StartUpdate(self):
        # Function - Updates texts...

        # Doing the preparations
        gl.progress_wnd.UpdateStageText(u"Инициализация обновления...")

        self.GetRequestedTimeValue()
        self.GetRequestedUserData()

        logging.info(u"Получаем тексты переводов пользователя " + self.uname + " :\n")
        # Creating patch with approved texts, translated by person
        kol1, kol2, kol3 = 0, 0, 0
        kol1 = self.CreatePatch("1", "translated")

        if not (self.uname == "All" and gl.cfg["UserGroup"] == "translator"):
            # Creating patch with not-approved texts. Translators can only get all approved texts...
            kol2 = self.CreatePatch("0", "translated")

        if not (self.uname == "All" or gl.cfg["UserGroup"] == "translator"):
            # Creating patch with approved by user texts. This shouldn't do anything if person is translator, or "All"
            logging.info(u"Получаем тексты, утвержденные пользователем " + self.uname + " :\n")
            kol3 = self.CreatePatch("1", "approved")

        # Destroying dialog window, when patch applied.
        gl.progress_wnd.Disable()
        gl.progress_wnd.Destroy()

        InfoText = u'Установка текстов завершена.\nУстановлено: \n'
        if (kol1 > 0):
            if (self.uname == "All"):
                InfoText += str(kol1) + u' утвержденных переводов пользователей.\n'
            else:
                InfoText += str(kol1) + u' утвержденных переводов пользователя ' + str(self.uname) + u'.\n'
        if (kol2 > 0):
            if (self.uname == "All"):
                InfoText += str(kol2) + u' неутвержденных переводов пользователей.\n'
            else:
                InfoText += str(kol2) + u' неутвержденных переводов пользователя ' + str(self.uname) + u'.\n'
        if (kol3 > 0):
            if (self.uname == "All"):
                InfoText += str(kol3) + u' утвержденных пользователями переводов.\n'
            else:
                InfoText += str(kol3) + u' утвержденных пользователем ' + str(self.uname) + u' переводов.\n'
        if (kol1 == 0 and kol2 == 0 and kol3 == 0):
            InfoText += u' 0 переводов.'

        logging.info(InfoText)
        self.wnd.InformationMessage(InfoText)

    def SendTranslatedByUserRequest(self, approved):
        if approved == "1":
            apptext = u"утвержденных текстов"
        else:
            apptext = u"неутвержденных текстов"

        gl.progress_wnd.UpdateStageText(u"Получение данных " + apptext + u"...")
        if self.uname == "All":
            gl.server_conn.request("GET", u"/groupware/get/" + str(self.starttime) + u"?to=" + str(
                self.endtime) + "&success=" + str(approved))
        else:
            gl.server_conn.request("GET", u"/groupware/get/" + str(self.starttime) + u"?to=" + str(
                self.endtime) + u"&translator=" + urllib.quote(self.uname.encode('utf-8')) + "&success=" + str(
                approved))
        self.resp = gl.server_conn.getresponse()
        self.respdata = str(self.resp.read()).decode('UTF-8')

    def SendApprovedByUserRequest(self):
        gl.server_conn.request("GET", u"/groupware/get/" + str(self.starttime) + u"?to=" + str(
            self.endtime) + "&moder=" + urllib.quote(self.uname.encode('utf-8')))
        self.resp = gl.server_conn.getresponse()
        self.respdata = str(self.resp.read()).decode('UTF-8')

    def CreatePatch(self, approved, mtype):
        # mtype = "translated"|"approved". Переведенные или утвержденные пользователем тексты соответственно
        # approved = 0|1 - Получение неутвержденных/утвержденных текстов

        if approved == "1":
            apptext = u"утвержденных текстов"
        else:
            apptext = u"неутвержденных текстов"

        if mtype == "translated":
            self.SendTranslatedByUserRequest(approved)
        elif mtype == "approved":
            self.SendApprovedByUserRequest()

        gl.progress_wnd.UpdateStageText(u"Формирование патча " + apptext + u"...")

        data = self.respdata.split('\r\n')
        for i in range(len(data)):
            data[i] = data[i].split('||')

        kol = 0
        logging.info(u"Формируем данные патча " + apptext + "...")

        if (os.path.exists(gl.patchpath)):
            os.remove(gl.patchpath)
        progress_str = "None"

        for i in data:
            newstr = "Готово " + str(int(kol / float(len(data)) * 100)) + "% данных...\n"
            if not progress_str == newstr:
                gl.progress_wnd.UpdatePercent(int(kol / float(len(data)) * 100))
            if len(i) == 6 and i[5] == approved:
                try:
                    # Текущий формат даты:
                    # i[0] = file_id (int)
                    # i[1] = item_id (int)
                    # i[2] = content (текст)
                    # i[3] = args_order (list/"")
                    # i[4] = args_id (list/NULL)
                    # i[5] = approved(0/1)
                    AddOneStringToPatch(i[0], i[1], i[2], i[3], i[4])
                except:
                    logging.critical(u"Ошибка формирования базы данных патча с файлом: " + str(i[0]) + " " + str(
                        i[1]) + " " + str(i[2]) + " " + str(i[3]) + " " + str(i[4]))
                kol += 1

        gl.progress_wnd.UpdateStageText(u"Установка патча " + apptext + " ...")

        if kol > 0:
            PatchFile(self.wnd.dat_path)
        return kol
