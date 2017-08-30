#!/usr/bin/env python
# -*- coding: utf-8 -*-
from UpdateGUI import PatchOneString
import wx
import GlobalVars as gl
import logging

class SelfPatchGUI():
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

    def Start(self, event = None):
        if self.DoPreparations() == -1:
            return
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

        self.cb1 = wx.CheckBox(self.wnd.setting_panel, label=u'Использовать стиль оформления \nпорядка аргументов в тексте\n(как на сайте)', pos=(5, 10))
        self.new_argument_type = "False"
        self.wnd.Bind(wx.EVT_CHECKBOX, self.ChangeArgumentType, self.cb1)

    def ChangeArgumentType(self, event = None):
        self.new_argument_type = str(self.cb1.GetValue())
        logging.info(u"Смена состояния параметра ArgumentType на " + str(self.new_argument_type))
        if self.new_argument_type == "True":
            self.input_args_order.SetValue("")
            self.input_args_order.SetEditable(False)
            self.input_args_order.SetBackgroundColour((128, 128, 128))
        else:
            self.input_args_order.SetEditable(True)
            self.input_args_order.SetBackgroundColour((255, 255, 255))
        self.input_args_order.Update()
        self.wnd.gui_panel.Update()

    def OnClickSelfPatchButton(self, event):
        if self.new_argument_type == "True":
            if not (self.input_file_id.GetValue() and self.input_gossip_id.GetValue() and self.input_value_id.GetValue()):
                self.wnd.WarningMessage(u"Вы не заполнили одно из полей. Так нельзя!")
                return

            current_str = self.input_value_id.GetValue().replace('\\\'', '\'')
            current_args_order = ""
            p = 0;
            max_index = 0
            while not p == -1:
                p = current_str.find("<--DO_NOT_TOUCH!-", p)
                if p == -1:
                    break
                p += 17
                print current_str.decode("utf-8")[p]
                i = int(current_str.decode("utf-8")[p])
                max_index = max(max_index, i)
                current_args_order += str(i) + "-"
            for i in range(1, max_index + 1):
                current_str = current_str.replace("<--DO_NOT_TOUCH!-" + str(i) + "!-->", "<--DO_NOT_TOUCH!-->")
            if (len(current_args_order) > 0):
                current_args_order = current_args_order[0:-1]

            PatchOneString(self.input_file_id.GetValue(), self.input_gossip_id.GetValue(),
                           current_str, current_args_order, self.wnd.dat_path)

            return
        if (self.input_file_id.GetValue() and self.input_gossip_id.GetValue() and self.input_value_id.GetValue()):
            PatchOneString(self.input_file_id.GetValue(), self.input_gossip_id.GetValue(),
                           self.input_value_id.GetValue().replace('\\\'', '\''), self.input_args_order.GetValue(),
                           self.wnd.dat_path)
        else:
            self.wnd.WarningMessage(u"Вы не заполнили одно из полей. Так нельзя!")

    def ClearSelfPatchContents(self, event):
        self.input_file_id.SetValue('')
        self.input_gossip_id.SetValue('')
        self.input_value_id.SetValue('')
        self.input_args_order.SetValue('')

