# -*- coding: utf-8 -*-

from analyse import sentiment
from dao import comment_dao, blog_dao
import re
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt
import numpy as np

from analyse.jieba_segmentation import JiebaSeg
import math

# s = sentiment.Sentiment()
#
# com_dao = comment_dao.CommentDao()
#
# comments = com_dao.search_all_comments_with_limit(1000)
# scores = []
# f = open('res.txt', 'w')
# for comment in comments:
#     raw_comment_info = comment[3].encode('utf-8')
#     comment_info = re.sub('(@\S*|\[.*\]|#.*#|秒拍视频|转发微博)', "", raw_comment_info)
#     val = s.single_review_sentiment_score(comment_info)
#     scores.append(val)
#     f.write("得分:" + str(val) + "\n")
#     f.write("原始:" + raw_comment_info + "\n")
#     f.write("处理后:" + comment_info + "\n")
#     f.write("\n")
# f.close()
# print "max = " + str(max(scores)), "min = " + str(min(scores))
# data = np.array(scores)
# data = (data - data.mean()) / (data.max() - data.min())
# bins = np.linspace(-1, 1, 20)
# plt.hist(data, bins=bins)
# plt.show()

# import re
# s = u"""      1
#
#     as
# """
#
# print re.sub(u'(\s|\n|t)', u'', s)


# b_dao = blog_dao.BlogDao()
# blogs = b_dao.search_all_blogs_without_keyword()
# x = []
# y = []
# z = []
# for blog in blogs:
#     x.append(int(blog[5]))
#     y.append(int(blog[6]))
#     z.append(int(blog[7]))
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# x = np.array(x)
# y = np.array(y)
# z = np.array(z)
# ax.scatter(x, y, z, c='r')  # 绘制数据点
# ax.set_xlim(0, 5000)
# ax.set_ylim(0, 5000)
# ax.set_zlim(0, 5000)
# ax.set_zlabel('thumbup')  # 坐标轴
# ax.set_ylabel('comment')
# ax.set_xlabel('forward')
# plt.show()

jieba_seg = JiebaSeg()


hot_blogs, cold_blogs = jieba_seg.get_hot_blogs(["郑爽"], 2500)

hx, hy, hz = [], [], []
cx, cy, cz = [], [], []



for blog in hot_blogs:
    hx.append(int(blog[5]))
    hy.append(int(blog[6]))
    hz.append(int(blog[7]))
for blog in cold_blogs:
    cx.append(int(blog[5]))
    cy.append(int(blog[6]))
    cz.append(int(blog[7]))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
hx = np.array(hx)
hy = np.array(hy)
hz = np.array(hz)

cx = np.array(cx)
cy = np.array(cy)
cz = np.array(cz)


ax.scatter(cx, cy, cz, c='b')  # 绘制数据点
ax.scatter(hx, hy, hz, c='r')  # 绘制数据点


ax.set_xlim(0, 5000)
ax.set_ylim(0, 5000)
ax.set_zlim(0, 5000)
ax.set_zlabel('thumbup')  # 坐标轴
ax.set_ylabel('comment')
ax.set_xlabel('forward')
plt.show()