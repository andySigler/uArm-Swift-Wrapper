#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFactory, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import os
from distutils.util import convert_path

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

    def find_packages():
        return ['uarm', 'uarm.comm', 'uarm.utils', 'uarm.tools', 'uarm.wrapper', 'uarm.swift', 'uarm.metal']

main_ns = {}
ver_path = convert_path('uarm/version.py')
with open(os.path.join(os.getcwd(), ver_path)) as ver_file:
    exec(ver_file.read(), main_ns)

version = main_ns['__version__']

# long_description = open('README.rst').read()
long_description = 'long description for uarm'

with open(os.path.join(os.getcwd(), 'requirements.txt')) as f:
    requirements = f.read().splitlines()

setup(
    name='uArm-Python-Wrapper',
    version=version,
    author='andySigler',
    description='Wrapper for uFactory\'s uArm-Python-SDK',
    packages=find_packages(),
    author_email='andrewsigler1@gmail.com',
    url="https://github.com/andysigler/uArm-Python-Wrapper",
    keywords="uarm4py uarmForPython uarm ufactory uarmForPython swift swiftpro swiftForPython swift4py",
    install_requires=requirements,
    long_description=long_description,
    license='BSD',
    zip_safe=False
)
