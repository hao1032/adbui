#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
from setuptools import setup, find_packages

VERSION = '4.5.16'

with io.open('README.md', 'r', encoding='utf-8') as fp:
    long_description = fp.read()

requires = [
    'lxml',
    'requests',
    'func_timeout',
    'tencentcloud-sdk-python>=3.0.0'
]

setup(
    name='adbui',
    version=VERSION,
    description='adbui 所有的功能都是通过 adb 命令，adbui 的特色是可以通过 xpath，ocr 获取 ui 元素。',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Tango Nian',
    author_email='hao1032@gmail.com',
    url='https://github.com/hao1032/adbui',
    keywords='testing android uiautomator ocr minicap',
    install_requires=requires,
    packages=find_packages(),
    include_package_data=True,
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