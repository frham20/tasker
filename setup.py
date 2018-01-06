#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='tasker',
    version='0.0.1',
    author='Francois Hamel',
    author_email='francois.hamel@gmail.com',
    url='https://github.com/frham20/tasker',
    description='Simple data driven task runner',
    long_description='',
    license='MIT',
    packages=find_packages(),
    zip_safe=True,
    install_requires=[
        'dirsync',
        'isodate'
    ]
)