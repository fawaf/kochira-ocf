#!/usr/bin/env python3

import sys

from setuptools import setup, find_packages
from urllib.parse import urlparse

with open('requirements.txt', 'r') as f:
    install_requires = []
    dependency_links = []
    append_version = '-' + str(sys.maxsize)

    requirements = [ line.strip() for line in f ]
    for requirement in requirements:
        name = urlparse(requirement)
        if name.scheme and name.netloc:
            install_requires.append(name.fragment.replace('egg=', ''))
            dependency_links.append(requirement + append_version)
        else:
            install_requires.append(requirement)

setup(name="kochira-ocf",
      version="2014.03.27",
      description="OCF kochira services",
      author="",
      author_email="",
      url="",
      packages=find_packages(),
      install_requires=install_requires,
      dependency_links=dependency_links,
      include_package_data=True,
      zip_safe=False,
      )
