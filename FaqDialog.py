#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import wx.lib.wxpTag
import wx.html2

class FaqDialog(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, size=(600, 500), style=wx.DEFAULT_FRAME_STYLE & ~(
        wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX) | wx.CAPTION | wx.STAY_ON_TOP)
        self.Centre()
        self.InitUI()
        self.SetTitle(u"Руководство")
        self.Show(True)


    def InitUI(self):
        f = open("faq.html", "r")# The html page as a python string literal
        page = f.read().replace('\n', '<br>').replace('\t', '    ').replace(' ', ' &nbsp;').decode('utf8')
        #self.htmlwin = wx.html.HtmlWindow(self)
        #self.htmlwin.SetPage(page)
        self.browser = wx.html2.WebView.New(self)
        self.browser.SetPage(page, "/")
