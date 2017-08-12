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
import logging
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
        self.MakeModal(True)
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