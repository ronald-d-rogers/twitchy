import sys
from cx_Freeze import setup, Executable

from twitchy import (
    __appname__,
    __description__,
    __version__,
    __author__,
    __email__,
    __license__
)

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable(
        'twitchy.py',
        base=base,
        icon='icons/twitchy.ico',
        compress=True
    )
]

opts = dict(
    packages        = ['pubsub.core', 'pubsub.core.kwargs', 'pubsub.core.arg1'],
    excludes        = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl', 'Tkconstants', 'Tkinter'],
    include_files   = ['icons/', 'plugins/', 'config.json', 'state.json'],
)

setup(name          = __appname__,
      description   = __description__,
      version       = __version__,
      author        = __author__,
      author_email  = __email__,
      license       = __license__,
      download_url  = 'http://github.com/ronald.d.rogers/twitchy/',
      # packages      = ['twitchy'],
      requires      = ('wxpython', 'twisted', 'pypubsub'),
      platforms     = ('Windows', 'Mac OS X'),
      classifiers   = ['Framework :: Twisted',
                       'Intended Audience :: End Users/Desktop',
                       'License :: OSI Approved :: BSD License',
                       'Operating System :: OS Independent',
                       'Programming Language :: Python',
                       'Topic :: Games/Entertainment'],

      options       = dict(build_exe = opts),
      executables   = executables
)
