#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import GlobalVars as gl
import os
import logging
import FaqDialog
import threading
import zipfile

from ProgressDialog import ProgressDialog


class MainGUI():
    def __init__(self, parent):
        self.wnd = parent

    def Start(self, event=None):
        self.wnd.RemoveGUI()
        # Base item of gui_panel - names of authors
        self.authors = wx.StaticText(self.wnd.gui_panel, -1,
                                     u'Над программной частью проекта трудились:\nОфициальный клиент: Kubera\nРасширенная версия:  Gi1dor\nОбновление файлов перевода: ArtRakyuo\nСайт и серверная часть: Coder',
                                     pos=(30, 10))
        self.authors.SetFont(wx.Font(10, family=wx.FONTFAMILY_SWISS, weight=wx.FONTWEIGHT_NORMAL, style=wx.NORMAL))

        self.cb1 = wx.CheckBox(self.wnd.setting_panel, label=u'Показывать FAQ при входе', pos=(5, 10))

        if gl.cfg["OpenFAQ"] == "True":
            self.cb1.SetValue(True)

        self.but1 = wx.Button(self.wnd.setting_panel, label=u'Создать резервную копию', pos=(5, 40), size=(210, -1))
        self.but2 = wx.Button(self.wnd.setting_panel, label=u'Восстановить из резервной копии', pos=(5, 70),
                              size=(210, -1))

        self.but3 = wx.Button(self.wnd.setting_panel, label=u'Сформировать журнал логов', pos=(5, 120), size=(210, -1))
        self.but4 = wx.Button(self.wnd.setting_panel, label=u'Удалить все данные программы\nи выйти', pos=(5, 150),
                              size=(210, -1))

        self.wnd.Bind(wx.EVT_CHECKBOX, self.ChangeFaq, self.cb1)
        self.wnd.Bind(wx.EVT_BUTTON, self.CreateCopy, self.but1)
        self.wnd.Bind(wx.EVT_BUTTON, self.RestoreFromCopy, self.but2)
        self.wnd.Bind(wx.EVT_BUTTON, self.MakeLogs, self.but3)
        self.wnd.Bind(wx.EVT_BUTTON, self.DELETE_ALL, self.but4)

    def CopyFile(self, path_source, path_target):
        try:
            source_size = os.stat(path_source).st_size
            copied = 0
            source = open(path_source, 'rb')
            target = open(path_target, 'wb')

            while True:
                chunk = source.read(32768)
                if not chunk:
                    break
                target.write(chunk)
                copied += len(chunk)
                self.copy_progress.UpdatePercent(copied * 100 / source_size)

            source.close()
            target.close()
            self.copy_progress.Disable()
            self.copy_progress.Destroy()
            self.wnd.InformationMessage(u"Копирование успешно завершено!")
        except:
            self.copy_progress.Disable()
            self.copy_progress.Destroy()
            self.wnd.ErrorMessage(
                u"Возникла ошибка при копировании файлов. Файл может быть занят другой программой. Или, возможно, стоит запустить программу от имени администратора.")

    def CreateCopy(self, event=None):
        # Проверка непредвиденного поведения и выход
        if gl.cfg["DatPath"] == "NULL":
            self.wnd.WarningMessage(u"Сначала укажите путь к папке с игрой!")
            return -1
        if os.path.exists(os.getenv("APPDATA") + "\\Cenchanced\\CLE_backup.dtd"):
            dlg = wx.MessageDialog(self.wnd,
                                   u"Программа обнаружила уже созданную ранее резервную копию. Заменить её на новую?",
                                   u"Замена резервной копии?", wx.YES_NO | wx.ICON_QUESTION)
            if not dlg.ShowModal() == wx.ID_YES:
                self.wnd.InformationMessage(u"Создание резервной копии отменено")
                return
        try:
            self.copy_progress = ProgressDialog(self.wnd, u"Создание резервной копии")
            self.copy_progress.Enable()
            self.copy_progress.UpdateTitleText(u"Создание резервной копии...")
            self.copy_progress.UpdateStageText(u"Копируем файлы. Пожалуйста, подождите...")
            t = threading.Thread(target=self.CopyFile,
                                 args=(gl.cfg["DatPath"], os.getenv("APPDATA") + "\\Cenchanced\\CLE_backup.dtd",))
            t.daemon = True
            t.start()
        except:
            self.wnd.ErrorMessage(
                u"Возникла ошибка при копировании файлов. Возможно, стоит запустить программу от имени администратора.")

    def RestoreFromCopy(self, event=None):
        # Проверка непредвиденного поведения и выход
        if gl.cfg["DatPath"] == "NULL":
            self.wnd.WarningMessage(u"Сначала укажите путь к папке с игрой!")
            return -1
        dlg = wx.MessageDialog(self.wnd,
                               u"Вы уверены что хотите восстановить файл client_local_English.dat из резервной копии? Все изменения будут потеряны!",
                               u"Восстановить файл из резервной копии?", wx.YES_NO | wx.ICON_QUESTION)
        if not dlg.ShowModal() == wx.ID_YES:
            self.wnd.InformationMessage(u"Восстановление из резервной копии отменено")
            return

        try:
            self.copy_progress = ProgressDialog(self.wnd, u"Создание резервной копии")
            self.copy_progress.Enable()
            self.copy_progress.UpdateTitleText(u"Восстановление из резервной копии...")
            self.copy_progress.UpdateStageText(u"Копируем файлы. Пожалуйста, подождите...")
            t = threading.Thread(target=self.CopyFile,
                                 args=(os.getenv("APPDATA") + "\\Cenchanced\\CLE_backup.dtd", gl.cfg["DatPath"],))
            t.daemon = True
            t.start()
        except:
            self.wnd.ErrorMessage(
                u"Возникла ошибка при копировании файлов. Возможно, стоит запустить программу от имени администратора.")

    def MakeLogs(self, event=None):
        z = zipfile.ZipFile(os.getenv('HOMEPATH') + '/Desktop/LotroPatcherLog.lpl', 'w')  # Создание нового архива
        for root, dirs, files in os.walk(
                        os.getenv('APPDATA') + "/Cenchanced"):  # Список всех файлов и папок в директории folder
            for file in files:
                if not file == "CLE_backup.dtd":
                    z.write(os.path.join(root, file))  # Создание относительных путей и запись файлов в архив

        z.close()
        self.wnd.InformationMessage(
            u"Готово! Файл с логами помещен на рабочий стол. Теперь его в случае необходимости можно отправить разработчику:\ne-mail: e1.gildor@gmail.com\nvk.com/gi1dor")

    def DELETE_ALL(self, event=None):
        dlg = wx.MessageDialog(self.wnd,
                               u"Вы уверены что хотите удалить ВСЕ данные этой программы? (В том числе файлы конфигурации и резервную копию, при наличии) \nЭто действие необратимо!",
                               u"Удалить все данные программы?", wx.YES_NO | wx.ICON_QUESTION)
        if not dlg.ShowModal() == wx.ID_YES:
            self.wnd.InformationMessage(u"Полное удаление данных программы было отменено")
            return

        gl.cfg["DELETE_ALL"] = 1
        self.wnd.Destroy()

    def ChangeFaq(self, event=None):
        gl.cfg["OpenFAQ"] = str(self.cb1.GetValue())
        if self.cb1.GetValue() == "False":
            self.wnd.InformationMessage(u"Просмотреть справку по работе вы всё ещё можете, нажав клавишу F1")
        logging.info(u"Смена состояния параметра OpenFAQ на " + gl.cfg["OpenFAQ"])

    def ShowFaq(self, event=None):
        gl.faq_wnd = FaqDialog(None)
