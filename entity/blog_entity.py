# -*- coding: utf-8 -*-
from graduation.items import BlogItem
import math

# 微博实体类
class BlogEntity():
    def __init__(self, vector, blog):
        self.vector = vector
        # 博文id应该是唯一的
        self.blog_id = blog[0]
        # 所搜索微博文章的关键字
        self.keyword = blog[1]
        # 博文发布的时间
        self.post_time = blog[2]
        # 博文的作者
        self.author = blog[3]
        # 博文的内容
        self.blog_info = blog[4]
        # 博文的转发量
        self.forward = blog[5]
        # 博文的评论数量
        self.comment = blog[6]
        # 博文的点赞数量
        self.blog_thumbup = blog[7]

    def get_vector(self):
        return self.vector

    def get_blog_id(self):
        return self.blog_id

    def get_blog_info(self):
        return self.blog_info

    def get_post_time(self):
        return self.post_time

    def get_author(self):
        return self.author

    def get_hot_point(self):
        return math.sqrt(self.comment ** 2 + self.blog_thumbup ** 2 + self.forward ** 2)
