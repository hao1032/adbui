#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


requires = [
    'lxml',
    'requests',
    'Pillow',
    'func_timeout'
]

setup(
    name='adbui',
    version='3.5.2',
    description='adbui 所有的功能都是通过 adb 命令，adbui 的特色是可以通过 xpath，ocr 获取 ui 元素。',
    long_description='adbui 所有的功能都是通过 adb 命令，adbui 的特色是可以通过 xpath，ocr 获取 ui 元素。',
    author='Tango Nian',
    author_email='hao1032@gmail.com',
    url='https://github.com/hao1032/adbui',
    keywords=[
        'testing', 'android', 'uiautomator', 'ocr'
    ],
    install_requires=requires,
    packages=['adbui'],
    license='MIT',
    platforms='any',
    classifiers=(
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing'
    )
)