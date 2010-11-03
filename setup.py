# Copyright (c) 2010 Mitch Garnaat http://garnaat.org/
# Copyright (c) 2010, Eucalyptus Systems, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from distutils.core import setup

setup(name = "roboto",
      version = "1.0a1",
      description = "Boto automation layer",
      long_description="An automation layer built on top of the boto library",
      author = "Mitch Garnaat",
      author_email = "mitch@eucalyptus.com",
      scripts = ["bin/roboto"],
      data_files=[('/usr/share/roboto', ["json/CreateVolume.json",
                                         "json/DescribeAddresses.json",
                                         "json/DescribeInstances.json"]),
      url = "http://open.eucalyptus.com",
      packages = ["roboto"],
      license = 'MIT',
      platforms = 'Posix; MacOS X; Windows',
      classifiers = [ 'Development Status :: 3 - Alpha',
                      'Intended Audience :: Users',
                      'License :: OSI Approved :: MIT License',
                      'Operating System :: OS Independent',
                      'Topic :: Internet',
                      ],
      )
