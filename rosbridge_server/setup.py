#!/usr/bin/env python

import os
import platform
import sys
import warnings

from distutils.core import setup, Extension
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=[
        'rosbridge_server',
        'backports',
        'backports.ssl_match_hostname',
        'tornado',
        'tornado.platform'
    ],
    package_dir={'': 'src'}
)

# The following code is copied from
# https://github.com/mongodb/mongo-python-driver/blob/master/setup.py
# to support installing without the extension on platforms where
# no compiler is available.
from distutils.command.build_ext import build_ext

class custom_build_ext(build_ext):
    """Allow C extension building to fail.

    The C extension speeds up websocket masking, but is not essential.
    """

    warning_message = """
********************************************************************
WARNING: %s could not
be compiled. No C extensions are essential for Tornado to run,
although they do result in significant speed improvements for
websockets.
%s

Here are some hints for popular operating systems:

If you are seeing this message on Linux you probably need to
install GCC and/or the Python development package for your
version of Python.

Debian and Ubuntu users should issue the following command:

    $ sudo apt-get install build-essential python-dev

RedHat, CentOS, and Fedora users should issue the following command:

    $ sudo yum install gcc python-devel
********************************************************************
"""

    def run(self):
        try:
            build_ext.run(self)
        except Exception:
            e = sys.exc_info()[1]
            sys.stdout.write('%s\n' % str(e))
            warnings.warn(self.warning_message % ("Extension modules",
                                                  "There was an issue with "
                                                  "your platform configuration"
                                                  " - see above."))

    def build_extension(self, ext):
        name = ext.name
        try:
            build_ext.build_extension(self, ext)
        except Exception:
            e = sys.exc_info()[1]
            sys.stdout.write('%s\n' % str(e))
            warnings.warn(self.warning_message % ("The %s extension "
                                                  "module" % (name,),
                                                  "The output above "
                                                  "this warning shows how "
                                                  "the compilation "
                                                  "failed."))

if (platform.python_implementation() == 'CPython' and
    os.environ.get('TORNADO_EXTENSION') != '0'):
    # This extension builds and works on pypy as well, although pypy's jit
    # produces equivalent performance.
    d['ext_modules'] = [
        Extension('tornado.speedups', sources=['src/tornado/speedups.c']),
    ]

    if os.environ.get('TORNADO_EXTENSION') != '1':
        # Unless the user has specified that the extension is mandatory,
        # fall back to the pure-python implementation on any build failure.
        d['cmdclass'] = {'build_ext': custom_build_ext}

setup(**d)
