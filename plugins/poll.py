"""A live poll for Twitch chat.

Votes are cast with hashtags, i.e. messages starting with the
pound-sign (#) and containing no spaces.

Example:
    #thisisavote
    
"""
from __future__ import division
from pubsub import pub
import wx
import plugins


class Poll(object):

    def __init__(self):
        self.votes = {}
        self.totalvotes = 0
        self._choices = {}

    def vote(self, voter, choice):
        if voter in self.votes:
            choice_ = self.votes[voter]
            choice_.votes -= 1
            if choice_.votes == 0 and not choice_.name == choice:
                del self._choices[choice_.name]
        else:
            self.totalvotes += 1

        if not choice in self._choices:
            choice_ = Choice(choice)
            self._choices[choice] = choice_
        else:
            choice_ = self._choices[choice]

        choice_.votes += 1
        self.votes[voter] = choice_

    def choices(self):
        choices = sorted(
            self._choices.values(), key=lambda c: c.votes, reverse=True)

        for choice in choices:
            choice.percent = choice.votes / self.totalvotes * 100

        return choices


class Choice(object):

    def __init__(self, name):
        self.name = name
        self.votes = 0
        self.percent = 0.0


class View(plugins.View):

    def oninit(self):
        self.sizer = wx.BoxSizer()
        gridsizer = wx.GridSizer(rows=10, cols=3, hgap=1, vgap=1)
        self.sizer.Add(gridsizer, 1, wx.EXPAND)

        self.choicetexts = []
        for _ in range(10):
            name = wx.StaticText(self.panel)
            name.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL))
            name.SetForegroundColour((255, 255, 255))

            votes = wx.StaticText(self.panel)
            votes.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL))
            votes.SetForegroundColour((255, 255, 255))

            percent = wx.StaticText(self.panel)
            percent.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL))
            percent.SetForegroundColour((255, 255, 255))

            gridsizer.Add(name, 1, wx.ALIGN_LEFT)
            gridsizer.Add(votes, 1, wx.ALIGN_RIGHT)
            gridsizer.Add(percent, 1, wx.ALIGN_RIGHT)
            self.choicetexts.append((name, votes, percent))

        self.panel.SetSizer(self.sizer)

    def setchoices(self, choices):
        if not choices:
            return

        for i, choice in enumerate(choices):
            if i == 10:
                break

            self.choicetexts[i][0].SetLabel(choice.name)
            self.choicetexts[i][1].SetLabel(str(choice.votes))
            self.choicetexts[i][2].SetLabel(
                '%' + str(round(choice.percent, 1)))

        self.sizer.Layout()


class Plugin(plugins.Plugin):
    name = 'Poll'
    viewtype = View

    def onopen(self):
        self.poll = Poll()
        pub.subscribe(self.onchatmessage, "service.chat.message")

    def onclose(self):
        pub.unsubscribe(self.onchatmessage, "service.chat.message")
        self.poll = None

    def onchatmessage(self, user, message):
        if message and message.startswith("#") and not ' ' in message:
            self.poll.vote(user, message)
            self.view.setchoices(self.poll.choices())
