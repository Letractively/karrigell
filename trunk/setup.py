#!/usr/bin/env python
import os
from distutils.core import setup

import sys

package_dir = { 'Karrigell':'Karrigell','HTMLTags':'HTMLTags'}
package_data = {
    'Karrigell':['*.txt'],'HTMLTags':['*.txt']
    }

setup(name='Karrigell',
      version='4.0',
      description='Web framework for Python 3.2+',
      author='Pierre Quentel',
      author_email='pierre.quentel@gmail.com',
      url='http://www.karrigell.fr/',
      packages=['Karrigell','HTMLTags'],
      package_dir=package_dir,
      package_data=package_data,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
          ]
     )

