# -*- coding: utf-8 -*-

import sys

sys.path.append('/home/zsh/PycharmProjects/graduation')
from dao.blog_dao import *
import jieba
from nltk.probability import FreqDist
import jieba.analyse
import math
import nltk
from numpy import array
import re

class JiebaSeg():
    def __init__(self):
        pass

    # 基于textrank算法的分词，并且返回权重
    def get_segmention_for_blog(self, blog_info):
        # 开启jieba分词
        # jieba.enable_parallel(4)
        # print type(blog_info)
        blog_info = blog_info.encode('utf-8')
        # 处理掉@和表情以及发布了头条文章
        blog_info = re.sub('(@\S*\s|\[.*\]|#.*#|发布了头条文章|抱歉，此微博已被作者删除。查看帮助 | 秒拍视频)', "", blog_info).decode('utf-8')
        # print blog_info
        return jieba.analyse.textrank(blog_info, topK=10000, withWeight=True)

    def get_segmention_for_all_blogs(self, keyword):
        jieba.analyse.set_stop_words("/home/zsh/PycharmProjects/graduation/dict/stop_words.txt")
        blog_dao = BlogDao()
        blogs = blog_dao.search_all_blogs(keyword)
        full_blog_info = u""
        for blog in blogs:
            blog_info = blog[4]
            full_blog_info += blog_info
            # print blog_info
            segs = jieba.analyse.textrank(blog_info, topK=10000, withWeight=True, span=3)
            # print "/".join(segs)
            return segs



    def get_top_keywords(self):
        jieba.analyse.set_stop_words("/home/zsh/PycharmProjects/graduation/dict/stop_words.txt")
        blog_dao = BlogDao()
        blogs = blog_dao.search_all_blogs()
        full_blog_info = u""
        # 统计维度
        dimens = set()
        vectors = []
        hot_blogs = []
        for blog in blogs:
            blog_info = blog[4]
            forward = blog[5]
            comment = blog[6]
            blog_thumbup = blog[7]
            val = math.sqrt(forward ** 2 + comment ** 2 + blog_thumbup ** 2)
            # full_blog_info += blog_info

            if val > 100:
                # print blog_info
                segs = jieba.analyse.textrank(blog_info, topK=1000, withWeight=True)
                dims = []
                datas = []
                v = []
                for dim, data in segs:
                    dimens.add(dim)

        for blog in blogs:
            blog_info = blog[4]
            forward = blog[5]
            comment = blog[6]
            blog_thumbup = blog[7]
            val = math.sqrt(forward ** 2 + comment ** 2 + blog_thumbup ** 2)
            # full_blog_info += blog_info

            if val > 100:
                hot_blogs.append(blog)
                print blog_info
                segs = jieba.analyse.textrank(blog_info, topK=1000, withWeight=True)
                dims = []
                datas = []
                v = []
                for dim, data in segs:
                    dims.append(dim)
                    datas.append(data)
                for dimen in dimens:
                    if dimen in dims:
                        v.append(datas[dims.index(dimen)])
                    else:
                        v.append(0)

                vectors.append(v)

        data = [array(v) for v in vectors]
        # print data
        ga = nltk.cluster.gaac.GAAClusterer(num_clusters=5, normalise=True)
        ga.cluster(vectors=data)
        for i in range(len(hot_blogs)):
            print "分类结果:", ga.classify(data[i]), " 原文：", hot_blogs[i][4]

    # 筛选出热度高于hot_point的bolg，返回hot_blogs
    def get_hot_blogs(self, keyword, hot_point):
        hot_blogs = []
        cold_blogs = []
        blog_dao = BlogDao()
        blogs = blog_dao.search_all_blogs(keyword)

        # 如果指定了hot_point按照hot_point进行计算
        if hot_point != 0:
            print "使用hot_point参数聚类"
            for blog in blogs:
                # 转发量
                forward = blog[5]
                # 评论量
                comment = blog[6]
                # 点赞量
                blog_thumbup = blog[7]

                # 用欧氏距离表示热度
                val = math.sqrt(forward ** 2 + comment ** 2 + blog_thumbup ** 2)
                if val > hot_point:
                    hot_blogs.append(blog)

        # 如果没有指定，那么按照k-means聚类
        else:
            print "使用k-means自动聚类"
            max_index = 0
            forward = blogs[0][5]
            comment = blogs[0][6]
            blog_thumbup = blogs[0][7]
            max_hot_point = math.sqrt(forward ** 2 + comment ** 2 + blog_thumbup ** 2)
            for index, blog in enumerate(blogs):
                # 转发量
                forward = blog[5]
                # 评论量
                comment = blog[6]
                # 点赞量
                blog_thumbup = blog[7]

                # 用欧氏距离表示热度
                val = math.sqrt(forward ** 2 + comment ** 2 + blog_thumbup ** 2)
                if val > max_hot_point:
                    max_hot_point = val
                    max_index = index

                if val == 0:
                    cold_blogs.append(blog)
            hot_blogs.append(blogs[max_index])
            # blogs.pop(max_index)

            # k-means for hot blogs
            for blog in blogs:
                # 转发量
                forward = blog[5]
                # 评论量
                comment = blog[6]
                # 点赞量
                blog_thumbup = blog[7]

                # 用欧氏距离表示热度
                val = math.sqrt(forward ** 2 + comment ** 2 + blog_thumbup ** 2)
                # 如果热度不是0
                if val != 0:
                    dis_to_hotblogs = self.get_dis(blog, hot_blogs)
                    dis_to_coldblogs =self.get_dis(blog, cold_blogs)
                    if dis_to_hotblogs > dis_to_coldblogs:
                        hot_blogs.append(blog)
                    else:
                        cold_blogs.append(blog)
        print "一共找到热点博客:", len(hot_blogs), "条"
        return hot_blogs

    def get_dis(self, blog, blogs):
        distances = []
        x0 = blog[5]
        y0 = blog[6]
        z0 = blog[7]
        for b in blogs:
            x1 = b[5]
            y1 = b[6]
            z1 = b[7]
            val = math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2 + (z0 - z1) ** 2)
            distances.append(val)
        distances.sort()
        return distances[len(distances) / 2]
