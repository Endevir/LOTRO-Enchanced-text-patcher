#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil
import os
import wx
import random

class Frame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(4,4), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        self.Centre()
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Show(False)
        
        
path = os.getenv("APPDATA") + "\\Cenchanced\\"
shutil.rmtree(path, True)

app = wx.App()
wnd = Frame(None, "")

dlg = wx.MessageDialog(wnd, u"Лечение произошло успешно! Вылечено " + str(random.randrange(430, 32476)) + u" морали", u"Успех!", wx.OK | wx.ICON_INFORMATION)
dlg.ShowModal()    
dlg.Destroy()

