#!/usr/bin/env python
# -*- coding: utf-8 -*-

from appfunc import *


class MainGUI():
    def __init__(self, parent):
        self.wnd = parent
        pass
    def Start(self, event = None):
        self.wnd.RemoveGUI()
        # Base item of gui_panel - names of authors
        self.authors = wx.StaticText(self.wnd.gui_panel, -1,
                                     u'Над программной частью проекта трудились:\nОфициальный клиент: Kubera\nРасширенная версия:  Gi1dor\nОбновление файлов перевода: ArtRakyuo\nСайт и серверная часть: Coder',
                                     pos=(30, 10))
        self.authors.SetFont(wx.Font(10, family=wx.FONTFAMILY_SWISS, weight=wx.FONTWEIGHT_NORMAL, style=wx.NORMAL))

        self.cb1 = wx.CheckBox(self.wnd.setting_panel, label=u'Показывать FAQ при входе', pos=(5, 10))
        self.cb2 = wx.CheckBox(self.wnd.setting_panel, label=u'Формировать архив с логами\nпри аварийном закрытии',
                               pos=(5, 30))
        self.cb2 = wx.CheckBox(self.wnd.setting_panel, label=u'Хранить резервную копию\nфайла .dat', pos=(5, 65))

        self.but1 = wx.Button(self.wnd.setting_panel, label=u'Сформировать архив с логами', pos=(5, 120), size=(210, -1))
        self.but2 = wx.Button(self.wnd.setting_panel, label=u'Удалить все данные программы', pos=(5, 150), size=(210, -1))
        pass