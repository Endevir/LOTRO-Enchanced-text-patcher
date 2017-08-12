#!/usr/bin/env python
# -*- coding: utf-8 -*-

from appfunc import *
import time
import GlobalVars as gl

class SelfPatchGUI():
    def __init__(self, parent):
        self.wnd = parent
        pass
    def Start(self, event = None):
        self.wnd.RemoveGUI()
        self.text_file_id = wx.StaticText(self.wnd.gui_panel, -1, u"Id файла: ", pos=(15, 10), size=(55, -1))
        self.input_file_id = wx.TextCtrl(self.wnd.gui_panel, -1, "", pos=(70, 8), size=(100, 20))

        self.text_gossip_id = wx.StaticText(self.wnd.gui_panel, -1, u"Id фрагмента: ", pos=(220, 10), size=(78, -1))
        self.input_gossip_id = wx.TextCtrl(self.wnd.gui_panel, -1, "", pos=(300, 8), size=(100, 20))

        self.text_args_order = wx.StaticText(self.wnd.gui_panel, -1, u"Порядок аргументов: ", pos=(15, 40), size=(130, -1))
        self.input_args_order = wx.TextCtrl(self.wnd.gui_panel, -1, "", pos=(145, 38), size=(180, 20))

        self.text_value_id = wx.StaticText(self.wnd.gui_panel, -1, u"Значение: ", pos=(15, 70), size=(60, -1))
        self.input_value_id = wx.TextCtrl(self.wnd.gui_panel, -1, "", pos=(80, 68), size=(340, 130), style=wx.TE_MULTILINE)

        self.apply_button = wx.Button(self.wnd.gui_panel, -1, u"Применить", pos=(130, 200))
        self.wnd.Bind(wx.EVT_BUTTON, self.OnClickSelfPatchButton, self.apply_button)

        self.clear_button = wx.Button(self.wnd.gui_panel, -1, u"Очистить", pos=(250, 200))
        self.wnd.Bind(wx.EVT_BUTTON, self.ClearSelfPatchContents, self.clear_button)

    def OnClickSelfPatchButton(self, event):
        if (self.wnd.dat_path):
            if (self.input_file_id.GetValue() and self.input_gossip_id.GetValue() and self.input_value_id.GetValue()):
                PatchOneString(self.input_file_id.GetValue(), self.input_gossip_id.GetValue(),
                               self.input_value_id.GetValue().replace('\\\'', '\''), self.input_args_order.GetValue(),
                               self.wnd.dat_path)
            else:
                self.wnd.WarningMessage(u"Вы не заполнили одно из полей. Так нельзя!")
        else:
            self.wnd.WarningMessage(
                u"Мы не смогли найти папку с игрой и файл client_local_english.dat в ней. Пожалуйста, выполните шаг 1")

    def ClearSelfPatchContents(self, event):
        self.input_file_id.SetValue('')
        self.input_gossip_id.SetValue('')
        self.input_value_id.SetValue('')
        self.input_args_order.SetValue('')

