Twitchy
=======

An extensible Twitch.tv GUI designed to improve streamer-chat interaction.

## How to Use

Install [wxPython](http://www.wxpython.org/download.php)

Install Twisted
```
pip install twisted
```
Install PyPubSub
```
pip install PyPubSub
```
Open config.json and enter your Twitch ID
```
{
  "twitch_id": "[YOUR_TWITCH_ID]",
  "services": {
    ...
  }
}
```
Run

```
python twitchy.py
```

## Plugins

#### Word Cloud

A live word cloud for Twitch chat.

#### Poll

A live poll for Twitch chat.

Votes are cast with hashtags, i.e. messages starting with the
pound-sign (#) and containing no spaces.

Example:

```
#thisisavote
```