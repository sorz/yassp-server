#!/usr/bin/env python3
from setuptools import setup


setup(
    name='yassp-server',
    version='0.1.0',
    author='sorz',
    url='https://github.com/sorz/yassp-server/',
    packages=['yasspserver'],
    entry_points="""
    [console_scripts]
    yassp-server = yasspserver.__main__:main
    """,
    install_requires=['requests', 'ssmanager'],
)

