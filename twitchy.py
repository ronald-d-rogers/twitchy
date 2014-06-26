"""A pluggable Twitch chat-interaction UI.
"""
from twisted.internet import _threadedselect
_threadedselect.install()
from twisted.internet import reactor
import wx
from pubsub import pub
import gui
import config
import chat
import plugins


__appname__ = 'twitchy'
__description__ = 'An extensible GUI designed to improve Twitch TV streamer-chat interaction'
__version__ = '0.1.0-alpha'
__author__ = 'Ronald Rogers'
__email__ = 'ronald.d.rogers@gmail.com'
__license__ = 'BSD'
__download__ = 'http://github.com/ronald.d.rogers/twitchy/'


class App(object):

    def __init__(self):
        self.config = config.read('config.json')

        if not 'twitch_id' in self.config:
            raise config.ConfigurationError(
                'Setting twitch_id incorrectly configured in config.json')

        self.wx = wx.App()

        self.plugins = plugins.PluginManager()
        self.plugins.load('plugins/')

        twitch_id = self.config['twitch_id']

        login = self.config['services']['chat']['login']
        bot_id = login['id']
        bot_oauth = login['oauth']

        chat.connect(bot_id, bot_oauth, twitch_id)

        reactor.interleave(wx.CallAfter)
        
        pub.subscribe(self.quit, 'command.quit')

        self.icon = gui.Icon(self.plugins.plugins())
        self.menu = gui.Menu(self.plugins.plugins())

        self.wx.MainLoop()

    def quit(self):
        self._quit_twisted()

    def _quit_wx(self, *args):
        self.icon.RemoveIcon()
        self.menu.Close()
        self.wx.Exit()

    def _quit_twisted(self):
        reactor.addSystemEventTrigger(
            'after', 'shutdown', self._quit_wx, True)

        if reactor.running:
            reactor.stop()


if __name__ == '__main__':
    app = App()
