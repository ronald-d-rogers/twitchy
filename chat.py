"""Exposes Twitch chat to the application.
"""
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.words.protocols import irc
from threading import Thread
from pubsub import pub


def connect(username, password, autojoin):
    factory = IRCClientFactory(username, password, autojoin)

    host = 'irc.twitch.tv'
    port = 6667

    reactor.connectTCP(host, port, factory)


class IRCClient(irc.IRCClient):

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        self.join(self.factory.autojoin)

    def privmsg(self, user, channel, msg):
        if user == 'jtv':
            return

        pub.sendMessage("service.chat.message", user=user, message=msg)

    def _get_nickname(self):
        return self.factory.username

    def _get_realname(self):
        return self.factory.username

    def _get_username(self):
        return self.factory.username

    def _get_password(self):
        return self.factory.password

    nickname = property(_get_nickname)
    realname = property(_get_realname)
    username = property(_get_username)
    password = property(_get_password)


class IRCClientFactory(protocol.ClientFactory):
    protocol = IRCClient

    def __init__(self, username, password, autojoin):
        self.username = username.lower()
        self.password = password
        self.autojoin = autojoin

    def clientConnectionLost(self, connector, reason):
        print 'irc: connection lost: ', reason
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print 'irc: connection failed: ', reason
        # reactor.stop()
        connector.disconnect()
        pub.sendMessage('command.quit')
