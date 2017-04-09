# -*- coding: utf-8 -*-

import MySQLdb


class Connetion():
    def __init__(self):
        pass

    def get_connetction(self):
        return MySQLdb.connect(host="localhost", user="root", passwd="123", db="graduation",
                               use_unicode=True, charset="utf8")
