# -*- coding: utf-8 -*-

from util.connection import *


class CommentDao():
    def __init__(self):
        pass

    def search_all_comments_with_limit(self, limit):
        # 首先获取到数据库的链接类
        connection = Connetion()
        # 获取到链接
        conn = connection.get_connetction()

        # 使用cursor()方法获取操作游标
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * from comment LIMIT {0}".format(limit))
            conn.commit()
        except:
            conn.rollback()
        # 访问结束关闭链接
        conn.close()
        # :接收全部的返回结果行.
        return cursor.fetchall()
