# -*- coding: utf-8 -*-

from util.connection import *


class BlogDao():
    def __init__(self):
        pass

    def search_all_blogs(self, keyword):
        # 首先获取到数据库的链接类
        connection = Connetion()
        # 获取到链接
        conn = connection.get_connetction()
        print keyword
        keywords = ["keyword = '{0}'".format(k) for k in keyword]

        condition = " OR ".join(keywords)
        print condition

        # 使用cursor()方法获取操作游标
        cursor = conn.cursor()
        try:
            print "SELECT * from blog WHERE {0} order BY post_time".format(condition)
            cursor.execute("SELECT * from blog WHERE {0} order BY post_time".format(condition))

            conn.commit()
        except:
            conn.rollback()
        # 访问结束关闭链接
        conn.close()

        # :接收全部的返回结果行.
        return cursor.fetchall()

    # 查找一列
    def search_col_blogs(self, col_name, keyword):
        # 首先获取到数据库的链接类
        connection = Connetion()
        # 获取到链接
        conn = connection.get_connetction()

        # 使用cursor()方法获取操作游标
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT {0} from blog WHERE keyword = {1}".format(col_name, keyword)),

            conn.commit()
        except:
            conn.rollback()
        # 访问结束关闭链接
        conn.close()

        # :接收全部的返回结果行.
        forwards = cursor.fetchall()
        res = []
        # forwards返回的是已“列”为结果的tuple，这里我只需要一个列表，所以重新组装成list
        for forward in forwards:
            res.extend(list(forward))
        return res

    # 查找多列
    def search_cols_blogs(self, cols_name, keyword):
        # 首先获取到数据库的链接类
        connection = Connetion()
        # 获取到链接
        conn = connection.get_connetction()

        # 使用cursor()方法获取操作游标
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT {0} from blog where keyword = {1}".format(",".join(cols_name), keyword))

            conn.commit()
        except:
            conn.rollback()
        # 访问结束关闭链接
        conn.close()

        # :接收全部的返回结果行.
        return cursor.fetchall()
        # res = []
        # # forwards返回的是已“列”为结果的tuple，这里我只需要一个列表，所以重新组装成list
        # for forward in forwards:
        #     res.extend(list(forward))
        # return res
