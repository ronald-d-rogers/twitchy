"""Base classes for plugins.
"""
import sys
import os
import wx
from pubsub import pub
import gui
from config import Config


def has_method(obj, name):
    return callable(getattr(obj, name, None))


class PluginManager(object):

    def __init__(self):
        self._plugins = {}

    def load(self, path):
        # Load plugins
        sys.path.insert(0, path)
        for f in os.listdir(path):
            fname, ext = os.path.splitext(f)
            if not fname == '__init__' and ext == '.py':
                mod = __import__(fname)
                self._plugins[fname] = mod.Plugin(fname)
        sys.path.pop(0)

    def plugins(self):
        return self._plugins.values()


state = Config('state.json')


class Plugin(object):

    def __init__(self, key):
        self.key = key
        self.isopen = False

        pub.subscribe(self.toggle, 'command.' + self.key + '.toggle')
        pub.subscribe(self.open, 'command.' + self.key + '.open')
        pub.subscribe(self.close, 'command.' + self.key + '.close')
        pub.subscribe(self.onquit, 'command.quit')

        if has_method(self, 'oninit'):
            self.oninit()

        self.state = state.setdefault(self.key, {})
        self.state.setdefault('open', False)

        if state[self.key]['open'] == True:
            self.open()

    def toggle(self):
        if not self.isopen:
            self.open()
        else:
            self.close()

    def open(self):
        if self.isopen == True:
            return

        self.view = self.viewtype(self.key)

        if has_method(self, 'onopen'):
            self.onopen()

        state[self.key]['open'] = True
        state.write()

        self.isopen = True

    def close(self):
        if self.isopen == False:
            return

        if has_method(self, 'onclose'):
            self.onclose()

        self.view.close()

        state[self.key]['open'] = False
        state.write()
        
        self.isopen = False

    def onquit(self):
        if self.isopen:
            self.view.close()


class View(object):
    size = (300, 200)

    def __init__(self, key):
        self.key = key

        self.state = state.setdefault(self.key, {})
        self.state.setdefault('size', self.size)
        self.state.setdefault('pos', (20, 80))

        size = self.state['size']
        pos = self.state['pos']

        self.frame = gui.Frame(size=size, pos=pos)
        self.panel = gui.Panel(self.frame)
        self.frame.Bind(wx.EVT_CONTEXT_MENU, self.oncontextmenu)

        menu = wx.Menu()
        menu.Bind(wx.EVT_MENU,
            lambda x: pub.sendMessage('command.' + self.key + '.close'),
            menu.Append(id=-1, text='Close'))

        self.contextmenu = menu

        self.init()

    def init(self):
        if has_method(self, 'oninit'):
            self.oninit()

        self.show()

    def show(self):
        self.frame.Show()

    def hide(self):
        self.frame.Hide()

    def close(self):
        self.state.update({
            'size': self.frame.GetSize().Get(),
            'pos': self.frame.GetPosition().Get()
        })
        self.state.write()
        self.frame.Close()

    def oncontextmenu(self, evt):
        self.frame.PopupMenu(
            self.contextmenu,
            self.frame.ScreenToClient(evt.GetPosition()))
