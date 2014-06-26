from pubsub import pub
import wx


ICON_16X16 = 'icons/16x16.png'


#
# Name:        flowsizer.py
# Purpose:     A demonstration custom sizer
# Author:      Ricardo Pedroso
# Created:     11 Jun 2005
# RCS-ID:      $Id: flowsizer.py,v 1.3 2005/11/26 16:57:42 rpedroso Exp $
# Copyright:   (c) Ricardo Pedroso
# Licence:     wxWindows licence
#
# Modified by: Ronald Rogers
# Modified:    17 Jun 2014
# Copyright:   (c) Ronald Rogers
#
# - Modified to display correctly with controls of differing heights
# - Added line spacing
#


class FlowSizer(wx.PySizer):

    def __init__(self):
        wx.PySizer.__init__(self)
        self.linespacing = 0

    def SetLineSpacing(self, linespacing):
        self.linespacing = linespacing

    def CalcMin(self):
        width = 0
        height = 0

        for item in self.GetChildren():

            item_width, item_height = item.GetSize()

            width += item_width
            height = max(height, item_height)

        return wx.Size(width, height)

    def RecalcSizes(self):
        x = 0
        y = 0
        size_x, dummy = self.GetSize()
        max_item_height = 0

        for item in self.GetChildren():
            item_width, item_height = item.GetSize()
            max_item_height = max(max_item_height, item_height)

            if x + item_width > size_x:
                x = 0
                y += max_item_height + self.linespacing
                max_item_height = item_height

            item.SetDimension(wx.Point(x, y),
                              wx.Size(item_width, max_item_height))

            x += item_width


class Panel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.leftdown = False
        self.parent = parent
        self.delta = None

        while self.parent.GetParent() is not None:
            self.parent = self.parent.GetParent()

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)

    def OnLeftDown(self, evt):
        self.CaptureMouse()
        self.leftdown = True
        pos = self.ClientToScreen(evt.GetPosition())
        origin = self.parent.GetPosition()
        dx = pos.x - origin.x
        dy = pos.y - origin.y
        self.delta = wx.Point(dx, dy)

    def OnLeftUp(self, evt):
        self.ReleaseMouse()
        self.leftdown = False

    def OnMouseMove(self, evt):
        if evt.Dragging() and self.leftdown:
            pos = self.ClientToScreen(evt.GetPosition())
            fp = (pos.x - self.delta.x, pos.y - self.delta.y)
            self.parent.Move(fp)


class Frame(wx.Frame):

    def __init__(self, **kwargs):
        self._shown = False

        kwargs['style'] = wx.RESIZE_BORDER | wx.STAY_ON_TOP | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, None, **kwargs)

        self.SetTransparent(180)
        self.BackgroundColour = wx.BLACK
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def Show(self, show=True):
        # Required for wxPython frames in Windows without captions
        if (show and not self._shown and 'wxMSW' in wx.PlatformInfo):
            size = self.GetSize()
            self.SetSize((1, 1))
            self.SetSize(size)
            self._shown = True

        super(Frame, self).Show(show)

    def OnClose(self, evt):
        self.Destroy()


class Icon(wx.TaskBarIcon):

    def __init__(self, plugins):
        super(Icon, self).__init__()
        self.plugins = plugins
        icon = wx.IconFromBitmap(wx.Bitmap(ICON_16X16))
        self.SetIcon(icon, 'Twitchy')
        self.Bind(wx.EVT_TASKBAR_LEFT_UP, self.OnLeftUp)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        for plugin in self.plugins:
            item = menu.Append(-1, text=plugin.name)
            menu.Bind(wx.EVT_MENU, lambda x, key=plugin.key:
                      pub.sendMessage('command.' + key + '.toggle'), item)

        menu.AppendSeparator()

        item = menu.Append(wx.ID_EXIT, text='&Exit')
        menu.Bind(wx.EVT_MENU, self.OnQuit, item)

        return menu

    def OnLeftUp(self, evt):
        self.PopupMenu(self.CreatePopupMenu())

    def OnQuit(self, evt):
        pub.sendMessage('command.quit')


class Menu(wx.Frame):

    def __init__(self, plugins):
        super(Menu, self).__init__(None)
        self.plugins = plugins
        menu_bar = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append(id=wx.ID_EXIT, text="")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)

        plugin_menu = wx.Menu()
        for plugin in plugins:
            item = plugin_menu.Append(id=-1, text=plugin.name)
            self.Bind(wx.EVT_MENU, lambda x, key=plugin.key:
                      pub.sendMessage('command.' + key + '.toggle'), item)

        menu_bar.Append(plugin_menu, "Plugins")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnQuit(self, evt):
        pub.sendMessage('command.quit')

    def OnClose(self, evt):
        self.Destroy()
