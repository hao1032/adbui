#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/29 3:55 下午
# @Author  : tangonian
# @Site    : 
# @File    : tango.py
# @Software: PyCharm
import os
import logging
import time


class Tango:
    @staticmethod
    def set_log(log_path, level=logging.INFO, remove_exist=False):
        if remove_exist and os.path.isfile(log_path):
            os.remove(log_path)

        handler1 = logging.StreamHandler()
        handler2 = logging.FileHandler(filename=log_path, encoding='utf-8')

        format_str = '{}%(asctime)s-%(levelname)s-%(lineno)d:%(message)s{}'
        handler1.setFormatter(logging.Formatter(format_str.format('', '')))
        handler2.setFormatter(logging.Formatter(format_str.format('', '')))

        logging.root.level = level
        logging.root.handlers = [handler1, handler2]

    @staticmethod
    def get_time_str(fmt='%Y%m%d-%H%M%S'):
        return time.strftime(fmt, time.localtime())

    @staticmethod
    def list_to_chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]