# -*- coding: utf-8 -*-
import jieba
import os

class Sentiment():
    def __init__(self):
        print "正在读取字典..."
        # 积极字典

        self.BASE_DIR = os.path.dirname(__file__)  # 获取当前文件夹的绝对路径
        self.posdict = self.read_lines(os.path.join(self.BASE_DIR, 'emotion_dict/pos_all_dict.txt'))
        # 消极字典
        self.negdict = self.read_lines(os.path.join(self.BASE_DIR, 'emotion_dict/neg_all_dict.txt'))
        # 程度副词词典
        self.mostdict = self.read_lines(os.path.join(self.BASE_DIR, 'degree_dict/most.txt'))  # 权值为2
        self.verydict = self.read_lines(os.path.join(self.BASE_DIR, 'degree_dict/very.txt')) # 权值为1.5
        self.moredict = self.read_lines(os.path.join(self.BASE_DIR, 'degree_dict/more.txt')) # 权值为1.25
        self.ishdict = self.read_lines(os.path.join(self.BASE_DIR, 'degree_dict/ish.txt')) # 权值为0.5
        self.insufficientdict = self.read_lines(os.path.join(self.BASE_DIR, 'degree_dict/insufficiently.txt')) # 权值为0.25
        self.inversedict = self.read_lines(os.path.join(self.BASE_DIR, 'degree_dict/inverse.txt'))  # 权值为-1

    def match(self, word, sentiment_value):
        if word in self.mostdict:
            sentiment_value *= 2.0
        elif word in self.verydict:
            sentiment_value *= 1.75
        elif word in self.moredict:
            sentiment_value *= 1.5
        elif word in self.ishdict:
            sentiment_value *= 1.2
        elif word in self.insufficientdict:
            sentiment_value *= 0.5
        elif word in self.inversedict:
            # print "inversedict", word
            sentiment_value *= -1
        return sentiment_value

    def read_lines(self, filename):
        # print filename
        fp = open(filename, 'r')
        lines = []
        for line in fp.readlines():
            line = line.strip()
            line = line.decode("utf-8")
            lines.append(line)
        fp.close()
        return lines

    # 求单条微博语句的情感倾向总得分
    def single_review_sentiment_score(self, weibo_sent):
        single_review_senti_score = []
        cuted_review = self.cut_sentence(weibo_sent)  # 句子切分，单独对每个句子进行分析

        for sent in cuted_review:
            seg_sent = self.segmentation(sent)  # 分词
            seg_sent = self.del_stopwords(seg_sent)[:]
            # for w in seg_sent:
            #	print w,
            i = 0  # 记录扫描到的词的位置
            s = 0  # 记录情感词的位置
            poscount = 0  # 记录该分句中的积极情感得分
            negcount = 0  # 记录该分句中的消极情感得分

            for word in seg_sent:  # 逐词分析
                # print word
                if word in self.posdict:  # 如果是积极情感词
                    # print "posword:", word
                    poscount += 1  # 积极得分+1
                    for w in seg_sent[s:i]:
                        poscount = self.match(w, poscount)
                    # print "poscount:", poscount
                    s = i + 1  # 记录情感词的位置变化

                elif word in self.negdict:  # 如果是消极情感词
                    # print "negword:", word
                    negcount += 1
                    for w in seg_sent[s:i]:
                        negcount = self.match(w, negcount)
                    # print "negcount:", negcount
                    s = i + 1

                # # 如果是感叹号，表示已经到本句句尾
                # elif word == "！".decode("utf-8") or word == "!".decode('utf-8'):
                #     for w2 in seg_sent[::-1]:  # 倒序扫描感叹号前的情感词，发现后权值+2，然后退出循环
                #         if w2 in posdict:
                #             poscount += 2
                #             break
                #         elif w2 in negdict:
                #             negcount += 2
                #             break
                i += 1
            # print "poscount,negcount", poscount, negcount
            single_review_senti_score.append(self.transform_to_positive_num(poscount, negcount))  # 对得分做最后处理
        pos_result, neg_result = 0, 0  # 分别记录积极情感总得分和消极情感总得分
        for res1, res2 in single_review_senti_score:  # 每个分句循环累加
            pos_result += res1
            neg_result += res2
        # print pos_result, neg_result
        result = pos_result - neg_result  # 该条微博情感的最终得分
        result = round(result, 1)
        return result

    def del_stopwords(self, seg_sent):
        stopwords = self.read_lines(os.path.join(self.BASE_DIR, "emotion_dict/stop_words.txt"))  # 读取停用词表
        new_sent = []  # 去除停用词后的句子
        for word in seg_sent:
            if word in stopwords:
                continue
            else:
                new_sent.append(word)
        return new_sent

    # 句子切分
    def cut_sentence(self, words):
        words = words.decode('utf8')
        start = 0
        i = 0
        token = 'meaningless'
        sents = []
        punt_list = ',.!?;~，。！？；～… '.decode('utf8')
        # print "punc_list", punt_list
        for word in words:
            # print "word", word
            if word not in punt_list:  # 如果不是标点符号
                # print "word1", word
                i += 1
                token = list(words[start:i + 2]).pop()
            # print "token:", token
            elif word in punt_list and token in punt_list:  # 处理省略号
                # print "word2", word
                i += 1
                token = list(words[start:i + 2]).pop()
            # print "token:", token
            else:
                # print "word3", word
                sents.append(words[start:i + 1])  # 断句
                start = i + 1
                i += 1
        if start < len(words):  # 处理最后的部分
            sents.append(words[start:])
        return sents

    # 分词，返回List
    def segmentation(self, sentence):
        seg_list = jieba.cut(sentence)
        seg_result = []
        for w in seg_list:
            seg_result.append(w)
        # print seg_result[:]
        return seg_result

    # 3.情感得分的最后处理，防止出现负数
    # Example: [5, -2] →  [7, 0]; [-4, 8] →  [0, 12]
    def transform_to_positive_num(self, poscount, negcount):
        pos_count = 0
        neg_count = 0
        if poscount < 0 and negcount >= 0:
            neg_count += negcount - poscount
            pos_count = 0
        elif negcount < 0 and poscount >= 0:
            pos_count = poscount - negcount
            neg_count = 0
        elif poscount < 0 and negcount < 0:
            neg_count = -poscount
            pos_count = -negcount
        else:
            pos_count = poscount
            neg_count = negcount
        return (pos_count, neg_count)
