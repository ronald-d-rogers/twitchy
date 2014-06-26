"""A live word cloud for Twitch chat.
"""
from __future__ import division
from collections import deque
from pubsub import pub
import wx
import gui
import plugins


class Tail(object):

    def __init__(self, length=100):
        self._words = {}
        self._tail = deque(maxlen=length)
        self._length = length

    def add(self, line):
        if not line:
            return

        for word in self._words.values():
            word.frecency -= word.occurences

        newline = []
        for key in line:
            if key in self._words:
                word = self._words[key]
            else:
                word = Word(key)
                self._words[key] = word
            word.occurences += 1
            word.frecency += self._length
            newline.append(word)

        if len(self._tail) == self._length:
            for word in self._tail[0]:
                word.occurences -= 1
                if word.occurences == 0:
                    del self._words[word.word]

        self._tail.append(newline)

    def words(self):
        return sorted(self._words.values(), key=lambda w: w.frecency, reverse=True)


class Word(object):

    def __init__(self, word):
        self.word = word
        self.occurences = 0
        self.frecency = 0


class View(plugins.View):

    def oninit(self):
        self.limit = 30
        self.sizer = gui.FlowSizer()
        self.sizer.SetLineSpacing(4)
        self.iswindows = 'wxMSW' in wx.PlatformInfo

        self.wordtexts = []
        for _ in range(self.limit):
            ctrl = wx.StaticText(self.panel, -1, '', style=wx.ALIGN_RIGHT)
            ctrl.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL))
            ctrl.SetForegroundColour((255, 255, 255))
            self.sizer.Add(ctrl, 0, flag=wx.LEFT | wx.RIGHT, border=3)
            self.wordtexts.append(ctrl)

        self.panel.SetSizer(self.sizer)

    def setwords(self, words):
        if not words:
            return

        words = words[:self.limit]

        min_fontsize = 10
        max_fontsize = 30
        fontsize_range = min_fontsize - max_fontsize
        default_fontsize = min_fontsize + fontsize_range / 2

        min_frecency = words[-1].frecency
        max_frecency = words[0].frecency
        frecency_range = min_frecency - max_frecency

        for i, word in enumerate(words):
            if frecency_range:
                fontsize = min_fontsize + \
                    (((word.frecency - min_frecency) / frecency_range) * fontsize_range)
            else:
                fontsize = default_fontsize

            # Windows wxPython hack
            if self.iswindows:
                self.wordtexts[i].SetFont(
                    wx.Font(fontsize, wx.ROMAN, wx.NORMAL, wx.NORMAL))

            self.wordtexts[i].SetFont(
                wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.NORMAL))

            self.wordtexts[i].SetLabel(word.word)

        self.sizer.Layout()


IGNORE_DEFAULT = [
    "a", "about", "all", "am", "an", "and", "any", "anything", "are", "as",
    "at", "be", "because", "been", "but", "can", "can't", "cant", "come",
    "could", "couldn't", "couldnt", "did", "didn't", "didnt", "do", "don't",
    "dont", "for", "from", "get", "go", "going", "good", "got", "had", "has",
    "have", "he", "her", "here", "he's", "hes", "hey", "him", "his", "how",
    "i", "i'd", "if", "i'll", "ill", "i'm", "im", "in", "is", "it", "it's",
    "its", "ive", "i've", "just", "like", "look", "me", "my", "no", "not",
    "now", "of", "oh", "ok", "okay", "on", "one", "or", "out", "see", "she",
    "she's", "shes", "so", "some", "than", "that", "that's", "thats", "the",
    "them", "then", "there", "theres", "there's", "they", "they're", "theyre",
    "think", "this", "time", "to", "u", "up", "want", "was", "we", "well",
    "were", "what", "when", "where", "who", "why", "will", "with", "would",
    "yeah", "yes", "you", "your", "you're", "youre"]


class Plugin(plugins.Plugin):
    name = 'Word Cloud'
    viewtype = View

    def oninit(self):
        self.filters = [lambda x: not "http://" in x and not "https://" in x]
        self.ignore = IGNORE_DEFAULT + ["kappa", "keepo", "kreygasm"]
        self.strip = " .;\"',:?!(){}/*-+=<>"

    def onopen(self):
        self.tail = Tail()
        pub.subscribe(self.onchatmessage, "service.chat.message")

    def onclose(self):
        pub.unsubscribe(self.onchatmessage, "service.chat.message")
        self.tail = None

    def onchatmessage(self, user, message):
        if not message:
            return

        for filter_ in self.filters:
            if not filter_(message):
                return

        line = []
        message = message.strip().split()
        for word in message:
            try:
                word.decode('ascii')
            except UnicodeDecodeError:
                pass
            else:
                word = word.strip(self.strip).lower()
                if word and not word in line and not word in self.ignore:
                    line.append(word)

        if len(line):
            self.tail.add(line)

        self.view.setwords(self.tail.words())
