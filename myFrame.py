#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os.path
from appfunc import *
import wx
import random
import webbrowser
import shutil
import time 
import http.client
import urllib
import GlobalVars as gl
import threading 

class ProgressDialog(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(768,576), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX | wx.CLOSE_BOX) | wx.CAPTION | wx.STAY_ON_TOP)
        self.Centre()
        self.InitUI()
        self.SetSize((450, 200))
        self.SetTitle(u"Применение обновлений")
        self.MakeModal(True)        
        self.Show(True)
    
    def Enable(self):
        self.UpdatePercent(0)
        self.MakeModal(False)
        self.Show(True)
        
    def Disable(self):
        self.MakeModal(False)
        self.Show(False)
        
    def InitUI(self):
        self.mainPanel = wx.Panel(self)
        self.Text0 = wx.StaticText(self.mainPanel, -1, u"Скачивание и применение обновлений...", pos = (0, 10), size = (450, -1), style = wx.ALIGN_CENTER);
        self.Text0.SetFont(wx.Font(20, family = wx.FONTFAMILY_DECORATIVE, weight = wx.FONTWEIGHT_NORMAL, style = wx.NORMAL))
        self.StageText = u"Подготовка патча..."
        self.Text1 = wx.StaticText(self.mainPanel, -1, self.StageText, pos = (0, 50), size = (450, -1), style = wx.ALIGN_CENTER);
        self.ProcText = wx.StaticText(self.mainPanel, -1, "0%", pos = (0, 70), size = (450, -1), style = wx.ALIGN_CENTER | wx.TRANSPARENT_WINDOW)        
        self.Gauge = wx.Gauge(self.mainPanel, -1, 100, pos = (20, 90), size=(410, 30))
    
    def UpdatePercent(self, percent):
        self.ProcText.SetLabel(str(percent) + u"%")
        self.Gauge.SetValue(int(percent))
        self.ProcText.Update()
        self.Gauge.Update()
        
    def UpdateStageText(self, str):
        self.StageText = u''.join(str)
        self.Text1.SetLabel(self.StageText)
        self.Text1.Update()
        self.mainPanel.Update()

class Frame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(768,576), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        self.Centre()
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        
        self.panel = wx.Panel(self, -1)
        self.panel.SetBackgroundColour((255, 255, 255))
        bg = wx.Image('bg.jpg', wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        self.bmp = wx.StaticBitmap(parent=self.panel, bitmap=bg, pos = (0, 0), size = (768, 576))
        self.mainPanel = wx.Panel(self.bmp, pos = (0, 80), size = (768, 430))
        self.mainPanel.SetBackgroundColour((255, 255, 255))
        self.addGUI()
        self.Show(True)
        
    def WarningMessage(self, msg):
        dlg = wx.MessageDialog(self, msg, u"Внимание!", wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()    
        dlg.Destroy()
        
    def addGUI(self):
        # Logo text
        LogoText = wx.StaticText(self.mainPanel, -1, "LOTRO Patcher: Enchanced edition", (0, 0), (768, -1), wx.ALIGN_CENTER)
        LogoFont = wx.Font(18, wx.FONTFAMILY_SCRIPT, wx.ITALIC, wx.NORMAL)
        LogoText.SetFont(LogoFont)    
        
        # Debug output text
        self.log_text = u"###################\nПривет! Это расширенная версия русификатора, созданная специально для переводчиков. Она позволяет скачивать и устанавливать обновления самых новых, ещё не утвержденных переводов. Кроме того, она позволяет напрямую менять локальные файлы игры.\n###################\nВнимание! Эти функции будут напрямую изменять данные игры! И они нарушают политику компании StandingStoneGames! Используйте их на свой страх и риск!\n###################\n"
        
        self.log_text_field = wx.TextCtrl(self.mainPanel, -1, self.log_text, pos = (500, 50), size=(250, 300), style=wx.TE_MULTILINE | wx.TE_READONLY)        
        self.log_text_field.SetFont(wx.Font(10, family = wx.FONTFAMILY_SWISS, weight = wx.FONTWEIGHT_NORMAL, style = wx.NORMAL, encoding = wx.FONTENCODING_CP1251))
        
        #path to client_local_English.dat file
        self.dat_text = wx.StaticText(self.mainPanel, -1, u"1) Папка с игрой: ", pos = (20, 50), size = (100, -1));
        self.dat_dialogue = wx.FileDialog(self.mainPanel, u"Укажите путь до файла \"client_local_English.dat\" в папке с игрой", "", "", "client_local_English.dat")
        self.dat_filetext = wx.StaticText(self.mainPanel, -1, u"1) Укажите путь до папки с LOTRO", pos = (120, 50), size=(250, -1), style = wx.SIMPLE_BORDER) 
        self.dat_path = ""
        self.dat_filetext.SetWindowStyleFlag(wx.SIMPLE_BORDER)
        if not gl.cfg["DatPath"] == "NULL":
            self.dat_path = gl.cfg["DatPath"]
            if (len(gl.cfg["DatPath"]) <= 40):
                self.dat_filetext.SetLabel(gl.cfg["DatPath"])
            else:
                self.dat_filetext.SetLabel(gl.cfg["DatPath"][:40] + "...")
            self.dat_dialogue.SetDirectory(gl.cfg["DatPath"][:-24])
            
        self.dat_button = wx.Button(self.mainPanel, -1, u"Выбрать файл", pos = (385, 48))
        self.Bind(wx.EVT_BUTTON, self.OnClickDatButton, self.dat_button)

        # Field - choose what to do
        self.what_to_do_text = wx.StaticText(self.mainPanel, -1, u"Что будем делать?", pos = (0, 75), size = (500, -1), style = wx.ALIGN_CENTER)
        self.what_to_do_text.SetFont(wx.Font(19, family = wx.FONTFAMILY_DECORATIVE, weight = wx.FONTWEIGHT_NORMAL, style = wx.NORMAL))
        
        # Buttons - what to do
        self.login = wx.Button(self.mainPanel, -1, u"2) Войти в систему", pos = (20, 130), size = (220, 25))
        self.update = wx.Button(self.mainPanel, -1, u"3) Получить обновления", pos = (265, 130), size = (220, 25))        
        self.translate = wx.Button(self.mainPanel, -1, u"Переводить отдельный фрагмент", pos = (20, 160), size = (220, 25))
        self.bug_report = wx.Button(self.mainPanel, -1, u"Писать сообщение об ошибке", pos = (265, 160), size = (220, 25))
        
        # Binding buttons to actions - show GUI on gui_panel
        self.Bind(wx.EVT_BUTTON, self.LoginGUI, self.login)        
        self.Bind(wx.EVT_BUTTON, self.UpdateGUI, self.update)
        self.Bind(wx.EVT_BUTTON, self.SelfPatchGUI, self.translate)
        self.Bind(wx.EVT_BUTTON, self.Report, self.bug_report)
        
        # Describing gui_panel
        self.gui_panel = wx.Panel(self.mainPanel, -1, pos = (20, 190), size = (465, 240), style = wx.SIMPLE_BORDER)
        self.gui_panel.SetBackgroundColour((255, 255, 255)) # for debug it is useful to change color
        
        # Base item of gui_panel - names of authors
        self.authors = wx.StaticText(self.gui_panel, -1, u'Над всем этим трудились:\nОфициальный клиент: Kubera\nРасширенная версия:  Gi1dor\nОбновление файлов перевода: ArtRakyuo\nСайт и серверная часть: Coder', pos = (30, 10))
        self.authors.SetFont(wx.Font(10, family = wx.FONTFAMILY_SWISS, weight = wx.FONTWEIGHT_NORMAL, style = wx.NORMAL))

        # Button - start the game
        self.startButton = wx.Button(self.mainPanel, -1, u'Запуск игры', pos = (520, 370), size = (200, 35)) 
        self.startButton.SetFont(wx.Font(19, family = wx.FONTFAMILY_DECORATIVE, weight = wx.FONTWEIGHT_NORMAL, style = wx.NORMAL))
        self.Bind(wx.EVT_BUTTON, self.StartGame, self.startButton)
        
    def StartGame(self, event):
        # Function - uses path to folder with client_local_English.dat, and starts TurbineLauncher.exe from the same folder
        if gl.cfg["DatPath"] == "NULL":
            self.WarningMessage(u"Сначала укажите путь к папке с игрой!")
            return
        execstr = str(gl.cfg["DatPath"][:-24]) + "TurbineLauncher.exe -nosplash -disablePatch -skiprawdownload"
        try:
            os.system('"' + str(gl.cfg["DatPath"][:-24]) + 'TurbineLauncher.exe" -nosplash -disablePatch -skiprawdownload')
        except:
            self.WarningMessage(u'Не найден файл TurbineLauncher.exe в папке с .dat файлом... Не можем запустить игру :(')
    
    def Login(self, event):
        # Function - logins user to the application via site controls
        
        self.nUserName = self.UserName_input.GetValue() # New username
        self.npassword = self.password_input.GetValue() # New password
        
        # Sending request to site
        gl.server_conn.request("GET", u"/auth/autologin?logout=1&email=" + self.nUserName + u"&password=" + self.npassword)
        self.resp = gl.server_conn.getresponse()
        self.respdata = self.resp.read()
        
        # self.respdata = "" when user is not in privileged group
        # self.respdata = %GROUPNAME%, when login is successfull
        # self.respdata = "null", when authentification fails
        
        if not self.respdata:
            self.WarningMessage(u"Кажется, вы не принадлежите команде переводчиков lotro... и поэтому вам недоступны многие функции программы. Но вы всегда можете присоединиться и стать переводчиком или модератором-тестировщиком!\nИли это просто ошибка подключения к серверу :)")
        
        if self.respdata and not self.respdata == "null":
            tmp = self.respdata.split("||") 
            gl.cfg["UserName"] = self.nUserName
            gl.cfg["LoginTime"] = str(int(time.time()))
            gl.cfg["UserGroup"] = tmp[0]
            gl.cfg["UserNick"] = tmp[1]
            
            self.UserName = self.nUserName
            self.LoginGUI(None)
            
        elif self.respdata == "null":
            self.WarningMessage(u"Неправильный e-mail или пароль.")
    
    
    def Update(self, event):
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
                self.WarningMessage(u"Неверный формат даты!")
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
        
        
        self.AddToLog(u"Получаем тексты переводов пользователя " + self.uname + " :\n")    
       
        # Creating patch with approved texts, translated by person
        self.CreatePatch("1", "translated")
        
        
        if not (self.uname == "All" and gl.cfg["UserGroup"] == "translator"):
            # Creating patch with not-approved texts. Translators can only get all approved texts... 
            self.CreatePatch("0", "translated")
        
        if not (self.uname == "All" or gl.cfg["UserGroup"] == "translator"):
            # Creating patch with approved by user texts. This shouldn't do anything if person is translator, or "All"
            self.AddToLog(u"Получаем тексты, утвержденные пользователем " + self.uname + " :\n") 
            self.CreatePatch("1", "approved")
        
        # Destroying dialog window, when patch applied.
        gl.progress_wnd.Disable()
        gl.progress_wnd.Destroy()        
        
    def CreatePatch(self, approved, mtype):
        # mtype = "translated"|"approved". Переведенные или утвержденные пользователем тексты соответственно
        if approved == "1":
            apptext = "утвержденных текстов"
        else:
            apptext = "неутвержденных текстов"
            
        if mtype == "translated":    
            gl.progress_wnd.UpdateStageText(u"Получение данных " + apptext + "...")
            if self.uname == "All":
                gl.server_conn.request("GET", u"/groupware/get1/" + str(self.starttime) + u"?to=" + str(self.endtime) + "&success=" + str(approved))
            else:
                gl.server_conn.request("GET", u"/groupware/get1/" + str(self.starttime) + u"?to=" + str(self.endtime) + u"&translator=" + urllib.quote(self.uname.encode('utf-8')) + "&success=" + str(approved))
            self.resp = gl.server_conn.getresponse()
            self.respdata = str(self.resp.read()).decode('UTF-8')
        elif mtype == "approved":
            gl.server_conn.request("GET", u"/groupware/get1/" + str(self.starttime) + u"?to=" + str(self.endtime) + "&moder=" + urllib.quote(self.uname.encode('utf-8')))
            self.resp = gl.server_conn.getresponse()
            self.respdata = str(self.resp.read()).decode('UTF-8')            
            #print(u"/groupware/get1/" + str(self.starttime) + u"?to=" + str(self.endtime) + "&moder=" + urllib.quote(self.uname.encode('utf-8')))
        
        gl.progress_wnd.UpdateStageText(u"Формирование патча " + apptext + "...")
        #print(str(self.respdata))
        tmp = self.respdata.split('\r\n')
        for i in range(len(tmp)):
            tmp[i] = tmp[i].split('||')

        kol = 0
        self.AddToLog(u"Формируем данные патча " + apptext + "...\n")            
        
        if (os.path.exists(gl.patchpath)):
            os.remove(gl.patchpath)     
        progress_str = "None"
        
        for i in tmp:
            #print("Готово " + str(int(kol / float(len(tmp)) * 100)) + "% данных...\n")
            newstr = "Готово " + str(int(kol / float(len(tmp)) * 100)) + "% данных...\n"
            if not progress_str == newstr:
                gl.progress_wnd.UpdatePercent(int(kol / float(len(tmp)) * 100))                          
                #self.RemoveFromLog(progress_str)
                #progress_str = newstr
                #self.AddToLog(progress_str)             
            if len(i) == 5 and i[4] == approved:
                try:
                    AddOneStringToPatch(i[0], i[1], i[2], i[3])
                except:
                    self.AddToLog("ПРОБЛЕМА! ПРОБЛЕМА! НЕ СМОГЛИ ПРОПАТЧИТЬ СТРОКУ!!!\n")
                kol += 1
        #print("VERY_IMPORTANT_NUM = " + str(kol))
        
        self.AddToLog(u"Готово 100% данных...\n")
        gl.progress_wnd.UpdateStageText(u"Установка патча " + apptext + " ...")
        if kol > 0:
            self.AddToLog(u"Получено " + str(kol) + u" " + apptext + u".\n")
            PatchFile(self.dat_path)
        else:
            self.AddToLog(u"Получено 0 " + apptext + ". Ничего не делаем...\n###################\n")
                                  
    def UpdateGUI(self, event):
        if gl.cfg["DatPath"] == "NULL":
            self.WarningMessage(u"Сначала укажите путь к папке и игрой!")
            return
        if gl.cfg["UserName"] == "NULL" or gl.cfg["UserGroup"] == "NULL":
            self.WarningMessage(u"Сначала войдите в систему переводов!")  
            return
        self.RemoveGUI()        
        
        if gl.cfg["UserGroup"] == "translator":
            self.text0 = wx.StaticText(self.gui_panel, -1, u"Вы вошли как переводчик, " + str(gl.cfg["UserNick"]) + u"\n Вы можете скачать и установить все утвержденные переводы,\nили свои ещё переводы.", pos = (0, 3), size = (450, -1), style = wx.ALIGN_CENTER)
        elif gl.cfg["UserGroup"] == "moderator" or gl.cfg["UserGroup"] == "developer" or gl.cfg["UserGroup"] == "administrator":
            self.text0 = wx.StaticText(self.gui_panel, -1, u"Вы - бог всея переводов, " + str(gl.cfg["UserNick"]) + u"\n Вы можете скачать и установить тексты,\n переведенные или утвержденные любым пользователем: ", pos = (0, 3), size = (450, -1), style = wx.ALIGN_CENTER)
            self.rb4 = wx.RadioButton(self.gui_panel, -1, u"Мои тексты", (30, 153), style=wx.RB_GROUP)
            self.rb5 = wx.RadioButton(self.gui_panel, -1, u"Все тексты", (30, 173))
            self.rb6 = wx.RadioButton(self.gui_panel, -1, u"Тексты пользователя: ", (30, 193))
            self.input3 = wx.TextCtrl(self.gui_panel, -1, u"", pos = (176, 190), size=(140, 19))
            
        self.text1 = wx.StaticText(self.gui_panel, -1, u"Скачать и установить тексты переводов за:", pos = (10, 60), style = wx.ALIGN_CENTER)
        self.rb0 = wx.RadioButton(self.gui_panel, -1, u"Последний час", (30, 80), style = wx.RB_GROUP)
        self.rb1 = wx.RadioButton(self.gui_panel, -1, u"Последние сутки", (150, 80))
        self.rb2 = wx.RadioButton(self.gui_panel, -1, u"Последнюю неделю", (30, 100))
        self.rb3 = wx.RadioButton(self.gui_panel, -1, u"В период между датами: ", (30, 120))
        if gl.cfg["UserGroup"] == "translator": 
            self.rb41 = wx.RadioButton(self.gui_panel, -1, u"Все последние утвержденные тексты", (30, 160))
        self.input1 = wx.TextCtrl(self.gui_panel, -1, u"ДД-ММ-ГГГГ", pos = (190, 118), size=(90, 19))
        self.text6 = wx.StaticText(self.gui_panel, -1, u" - ", pos = (285, 120),  style = wx.ALIGN_CENTER)
        self.input2 = wx.TextCtrl(self.gui_panel, -1, u"ДД-ММ-ГГГГ", pos = (300, 118), size=(90, 19))
        self.text7 = wx.StaticText(self.gui_panel, -1, u"-------------------------------------------------------------------------------", pos = (0, 137), size = (450, -1), style = wx.ALIGN_CENTER)
                
        if gl.cfg["UserGroup"] == "moderator" or gl.cfg["UserGroup"] == "developer" or gl.cfg["UserGroup"] == "administrator":
            self.button_apply = wx.Button(self.gui_panel, -1, u'Скачать и установить', pos = (150, 210))
        else:
            self.button_apply = wx.Button(self.gui_panel, -1, u'Скачать и установить', pos = (150, 190))
        self.Bind(wx.EVT_BUTTON, self.Update, self.button_apply)            
    
    def LoginGUI(self, event):
        self.RemoveGUI()
        self.text0 = wx.StaticText(self.gui_panel, -1, u"Вы не залогинились!\n Войдите, используя e-mail и пароль от сайта transtale.lotros.ru", pos = (0, 10), size = (450, -1), style = wx.ALIGN_CENTER)
        self.text0.SetFont(wx.Font(10, family = wx.FONTFAMILY_SWISS, weight = wx.FONTWEIGHT_NORMAL, style = wx.NORMAL))
        self.UserName = ""
        
        if gl.cfg["UserName"] and not gl.cfg["UserName"] == "NULL" and gl.cfg["LoginTime"] and not gl.cfg["LoginTime"] == "NULL":
            if int(time.time()) - int(gl.cfg["LoginTime"]) > 86400:
                gl.cfg["UserName"] = "NULL"
                gl.cfg["LoginTime"] = "NULL"
                gl.cfg["UserGroup"] = "NULL"
                gl.cfg["UserNick"] = "NULL"
            if not gl.cfg["LoginTime"] == "NULL":
                self.UserName = gl.cfg["UserName"]
                
        if self.UserName:
            if gl.cfg["UserGroup"] == "translator":
                self.text0.SetLabel(u"Вы вошли как переводчик " + gl.cfg["UserNick"].encode('utf-8') + u"!\n Вы можете перезайти, используя другой e-mail от сайта transtale.lotros.ru")
            else:
                self.text0.SetLabel(u"Вы вошли как модератор " + gl.cfg["UserNick"].encode('utf-8') + u"!\n Вы можете перезайти, используя другой e-mail от сайта transtale.lotros.ru")
        
        self.text_invitation = wx.StaticText(self.gui_panel, -1, u"Войти в систему: ", pos = (0, 60), size = (450, -1), style = wx.ALIGN_CENTER)
        self.text_invitation.SetFont(wx.Font(11, family = wx.FONTFAMILY_SWISS, weight = wx.FONTWEIGHT_NORMAL, style = wx.NORMAL))
        
        self.UserName_text =  wx.StaticText(self.gui_panel, -1, u"E-mail: ", pos = (20, 90))
        self.UserName_input = wx.TextCtrl(self.gui_panel, -1, "", pos = (100, 90), size=(150, 20))
        
        self.password_text =  wx.StaticText(self.gui_panel, -1, u"Пароль: ", pos = (20, 120))
        self.password_input = wx.TextCtrl(self.gui_panel, -1, "", pos = (100, 120), size=(150, 20), style = wx.TE_PASSWORD)
        
        self.login_button = wx.Button(self.gui_panel, -1, u'Войти', pos = (150, 150))
        self.Bind(wx.EVT_BUTTON, self.Login, self.login_button)
    
    def AddToLog(self, str):
        #pass
        self.log_text += str
        self.log_text_field.SetValue(self.log_text)  
        self.log_text_field.Update()
        self.gui_panel.Update()  
        
    def RemoveFromLog(self, str):
        #pass
        pos = self.log_text.rfind(str)
        if pos >= 0:
            self.log_text = self.log_text[:pos]
            self.log_text_field.SetValue(self.log_text)  
            self.log_text_field.Update()
            self.gui_panel.Update()
            
    def OnClickDatButton(self, event):
        if self.dat_dialogue.ShowModal() == wx.ID_OK:
            self.dat_path = self.dat_dialogue.GetPath()
            gl.cfg['DatPath'] = self.dat_path
            if (len(self.dat_path) <= 40):
                self.dat_filetext.SetLabel(self.dat_path)
            else:
                self.dat_filetext.SetLabel(self.dat_path[:40] + "...")
    
    def ClearSelfPatchContents(self, event):
        self.input_file_id.SetValue('')
        self.input_gossip_id.SetValue('')
        self.input_value_id.SetValue('')
        self.input_args_order.SetValue('')
                
    def OnClickSelfPatchButton(self, event):
        if (self.dat_path):
            if (self.input_file_id.GetValue() and self.input_gossip_id.GetValue() and self.input_value_id.GetValue()):
                PatchOneString(self.input_file_id.GetValue(), self.input_gossip_id.GetValue(), self.input_value_id.GetValue().replace('\\\'', '\''), self.input_args_order.GetValue(), self.dat_path)
            else:
                self.WarningMessage(u"Вы не заполнили одно из полей. Так нельзя!")
        else:
            self.WarningMessage(u"Мы не смогли найти папку с игрой и файл client_local_english.dat в ней. Пожалуйста, выполните шаг 1")
             
    def SelfPatchGUI(self, event):
        self.RemoveGUI()
        self.text_file_id = wx.StaticText(self.gui_panel, -1, u"Id файла: ", pos = (15, 10), size = (55, -1))
        self.input_file_id = wx.TextCtrl(self.gui_panel, -1, "", pos = (70, 8), size=(100, 20))        
        
        self.text_gossip_id = wx.StaticText(self.gui_panel, -1, u"Id фрагмента: ", pos = (220, 10), size = (78, -1))
        self.input_gossip_id = wx.TextCtrl(self.gui_panel, -1, "", pos = (300, 8), size=(100, 20))
        
        self.text_args_order = wx.StaticText(self.gui_panel, -1, u"Порядок аргументов: ", pos = (15, 40), size = (130, -1))
        self.input_args_order = wx.TextCtrl(self.gui_panel, -1, "", pos = (145, 38), size=(180, 20))        
        
        self.text_value_id = wx.StaticText(self.gui_panel, -1, u"Значение: ", pos = (15, 70), size = (60, -1))
        self.input_value_id = wx.TextCtrl(self.gui_panel, -1, "", pos = (80, 68), size=(340, 130), style=wx.TE_MULTILINE)

        self.apply_button = wx.Button(self.gui_panel, -1, u"Применить", pos = (130, 200))
        self.Bind(wx.EVT_BUTTON, self.OnClickSelfPatchButton, self.apply_button)

        self.clear_button = wx.Button(self.gui_panel, -1, u"Очистить", pos = (250, 200))
        self.Bind(wx.EVT_BUTTON, self.ClearSelfPatchContents, self.clear_button)        
        
    def Report(self, event):
        webbrowser.open("http://translate.lotros.ru/bugs/add", new = 2)
    def RemoveGUI(self):
        for child in self.gui_panel.GetChildren(): 
            child.Destroy()     
            
