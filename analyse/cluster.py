# -*- coding: utf-8 -*-

import math
from jieba_segmentation import JiebaSeg
import numpy as np
from entity.blog_entity import *
from dao.blog_dao import *
import sys


def get_dimens(blogs):
    dimens = set()
    jieba_seg = JiebaSeg()
    for blog in blogs:
        blog_info = blog[4]
        segs = jieba_seg.get_segmention_for_blog(blog_info)
        for seg, weight in segs:
            dimens.add(seg)
    return dimens


# 将关键词的权重转换成向量
# dimens表示全局的维度
# segs是一个元组列表[(单词，权重)...]

# 对于稀疏向量做泛化处理
def normalize(segs):
    sum = 0
    for seg, weight in segs:
        sum += weight ** 2
    norm = math.sqrt(sum)
    for i in range(len(segs)):
        segs[i] = list(segs[i])
        segs[i][1] /= norm


def gaac_for_hotblogs(keyword, hot, min_similarity):
    jieba_seg = JiebaSeg()
    # 筛选热度高于100的节点作为热点
    hot_blogs, cold_blogs = jieba_seg.get_hot_blogs(keyword, hot)

    print "一共获取到hotblogs(热点博客)", len(hot_blogs), "条"

    # 首先获取所有的单词维度
    # dimens = get_dimens(hot_blogs)
    # print dimens
    # segmentions返回的是元组列表
    # [(单词1，权重1),(单词2，权重2)...]
    # 将vector作为特征向量
    hot_blog_entities = []
    for hot_blog in hot_blogs:
        # get_vector 方法将所有的segmentions返回的是元组转换成向量，词组如果存在就是weight不存在就是0
        segs = jieba_seg.get_segmention_for_blog(hot_blog[4])
        #     segmentions = ""
        #     for seg, weight in segs:
        #         segmentions += "," + seg
        #     print segmentions

        normalize(segs)
        hot_blog_entities.append(
            [BlogEntity(segs, hot_blog)])

    # 现在已经将所有的数据封装到hot_blog_entities中了
    # 开始聚类
    flag = False
    while flag is not True:
        # 总的实体的个数
        tot_entities = len(hot_blog_entities)
        print "当前一共" + str(tot_entities) + "类"
        # 寻找最近的两类合并
        v = 0
        t = 0
        max_similarity = 0
        for i in range(tot_entities):
            for j in range(i + 1, tot_entities):
                similarity = get_similarity(hot_blog_entities[i], hot_blog_entities[j])
                if similarity > max_similarity:
                    max_similarity = similarity
                    v = i
                    t = j
        if max_similarity < min_similarity:
            flag = True
        # 将hot_blog_entities中 index 为v和t的合并
        else:
            merge(hot_blog_entities, v, t)

    # 聚类结束
    # i = 0
    # for entity in hot_blog_entities:
    #     if len(entity) > 2:
    #         # print i
    #         i += 1
    #         for blog in entity:
    #             print blog.get_blog_info()

    return hot_blog_entities


def get_distance(v1, v2):
    sum = 0
    for seg1, weight1 in v1:
        for seg2, weight2 in v2:
            if seg1 == seg2:
                sum += weight1 * weight2
    return sum


def get_similarity(blog_entity1, blog_entity2):
    # print  blog_entity1
    dot_products = []
    for e1 in blog_entity1:
        for e2 in blog_entity2:
            v1 = e1.get_vector()
            v2 = e2.get_vector()
            dot_products.append(get_distance(v1, v2))
    # 返回的是中位数，也可以尝试平均数
    dot_products.sort()
    length = len(dot_products)
    return dot_products[length / 2]

    # 使用平均值，貌似还是中位数比较靠谱
    # return sum(dot_products)/len(dot_products)


def merge(blog_entities, v, t):
    blog_entities[v].extend(blog_entities[t])
    blog_entities.pop(t)


def k_means_for_allblogs(hot_blog_entities, keyword, min_similarity):
    # pass
    blog_dao = BlogDao()
    blogs = blog_dao.search_all_blogs(keyword)
    jieba_seg = JiebaSeg()
    blog_entities = []
    for blog in blogs:
        segs = jieba_seg.get_segmention_for_blog(blog[4])
        # normalize
        normalize(segs)
        blog_entities.append(
            BlogEntity(segs, blog))
    all_blog_entities = [[hot_blog for hot_blog in hot_blog_entity] for hot_blog_entity in hot_blog_entities]
    tot_blogs = len(blog_entities)
    tot_entities = len(all_blog_entities)
    for i in range(tot_blogs):
        # if i % 10 == 0:
        print "the", i, "blog"
        max_similarity = 0
        t = 0
        for j in range(tot_entities):
            # temp_list = []
            # temp_list.append()
            similarity = get_similarity([blog_entities[i]], all_blog_entities[j])
            if similarity > max_similarity:
                max_similarity = similarity
                t = j
        print "最大相似度为 ： ", max_similarity
        if max_similarity == 0:
            print blogs[i][4]
        if max_similarity > min_similarity:
            all_blog_entities[t].append(blog_entities[i])
    return all_blog_entities


def get_earlist_post_time(blog_entities):
    earliest_post_time = blog_entities[0].get_post_time()
    for blog_entity in blog_entities:
        earliest_post_time = min(earliest_post_time, blog_entity.get_post_time())

    return earliest_post_time


def get_classfied_blogs(keywords, hot, min_similarity, min_quantity):
    blog_dao = BlogDao()
    blogs = blog_dao.search_all_blogs(keywords)
    s = ""
    for keyword in keywords:
        s += keyword
    f_name = s + "_" + str(hot) + "_" + str(min_similarity) + "_" + str(min_quantity) + ".txt"
    f = open(f_name, 'w')
    f.write("一共有" + str(len(blogs)) + "博客\n")
    print "一共有" + str(len(blogs)) + "博客"
    f.write("关键词为：")
    for keyword in keywords:
        f.write(keyword)
    f.write("最低热点为：" + str(hot) + "\n")
    f.write("最低相似度为：" + str(min_similarity) + "\n")
    f.write("最小类大小为：" + str(min_quantity) + "\n")
    # 对高热度blog进行层次聚类
    print "正在对热点博客进行聚类"
    hot_blog_entities = gaac_for_hotblogs(keywords, hot, min_similarity)
    f.write("对于热点博客进行层次聚类结果: 一共 " + str(len(hot_blog_entities)) + "类\n")
    # for index, hot_blog_entity in enumerate(hot_blog_entities):
    #     f.write("第" + str(index) + "类, " + "大小为" + str(len(hot_blog_entity)) + "\n")

    # 对所有博客进行层次聚类
    print "正在对所有博客k-means聚类"
    # print "k-means聚类前第56类大小：",len(hot_blog_entities[69])
    all_blog_entities = k_means_for_allblogs(hot_blog_entities, keywords, min_similarity)
    # print "k-means聚类后第56类大小：",len(hot_blog_entities[69])
    f.write("对于所有博客进行k-means聚类结果: 一共 " + str(len(all_blog_entities)) + "类\n")
    # for index, all_blog_entity in enumerate(all_blog_entities):
    #     f.write("第" + str(index) + "类, " + "大小为" + str(len(all_blog_entity)) + "\n")
    # for index, all_blog_entity in enumerate(all_blog_entities):
    #     f.write("第" + str(index) + "类, " + "大小为" + str(len(all_blog_entity)) + "\n")
    #     if len(all_blog_entity) > min_quantity:
    #         f.write("第" + str(index) + "类, " + "大小为" + str(len(all_blog_entity)) + "被定义为核心类,其热点博客为\n")
    #         for hot_blog in hot_blog_entities[index]:
    #             f.write(hot_blog.get_blog_info() + "\n")

    all_blog_entities.sort(key=lambda obj: len(obj), reverse=True)
    all_blog_entities = all_blog_entities[:min_quantity]
    for index, all_blog_entity in enumerate(all_blog_entities):
        f.write("第" + str(index) + "类, " + "大小为" + str(len(all_blog_entity)) + "\n")
        for blog in all_blog_entities[index]:
            f.write(blog.get_blog_info() + "\n")
    f.close()
    # #
    # all_blog_entities.sort(key=get_earlist_post_time, reverse=False)

    return all_blog_entities
