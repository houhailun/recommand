#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
主要推荐算法：
    1、基于内容的推荐：根据物品本身的属性来推荐相似的物品，不存在冷启动问题
    2、协同过滤：
        （1）基于用户的协同过滤：根据用户对物品的行为（浏览、评分、评论等），计算相似用户，推荐相似用户喜欢的物品
        （2）基于物品的协同过滤：根据用户对物品的行为，计算相似物品，给用户推荐相似物品
    3、基于模型的推荐：LR
    4、基于热度的推荐：推荐热门商品

这里实现了基于用户的协同过滤和基于物品的协同过滤算法
一些讨论：
Q：UserCF和ItemCF分别适用于什么情况？
A：UserCF根据相似用户推荐，更社会化；ItemCF根据用户本身的历史记录推荐，更加个性化。UserCF较适用于新闻，社区等网站，ItemCF较适用于购物等网站。

Q：UserCF和ItemCF的余弦相似度矩阵W有什么异同？
A：UserCF的相似度矩阵表示用户之间的相似度，适用于用户较少物品较多的场合；ItemCF的相似度矩阵表示物品之间的相似度，适用于用户较多物品较少的场合。目前的购物网站中，物品数量远远小于用户数量，所以购物网站大多采用ItemCF。

Q：如何评价一个推荐系统的优劣？
A：评价一个推荐系统有3种方法：离线实验，用户调查和在线实验。评测的指标有：用户满意度，预测准确度，覆盖率，多样性，新颖性，惊喜度，信任度，实时性，健壮性和商业目标。
"""

from math import sqrt


class similay:
    """相似度类：欧式距离、皮尔逊相关系数"""
    def sim_distince(self, prefs, person1, person2):
        si = {}
        # person1和person2共同的电影列表
        for item in prefs[person1]:
            if item in prefs[person2]:
                si[item] = 1

        if len(si) == 0:
            return

        # 计算差值平方和
        sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                              for item in si])

        # 偏好越相似距离越短，这里加1防止除以0，并取倒数
        return 1 / (1 + sqrt(sum_of_squares))

    # 皮尔逊相关系数 相比欧式距离来说,在数据不是很规范的时候更容易给出较好结果
    def sim_pearson(self, prefs, person1, person2):
        # 得到双方都评价过的物品
        si = {}
        for item in prefs[person1]:
            if item in prefs[person2]:
                si[item] = 1

        n = len(si)
        if n == 0:
            return 1

        # 对所有偏好求和
        sum1 = sum([prefs[person1][it] for it in si])
        sum2 = sum([prefs[person2][it] for it in si])

        # 求平方和
        sum1Sq = sum([pow(prefs[person1][it], 2) for it in si])
        sum2Sq = sum([pow(prefs[person2][it], 2) for it in si])

        # 求乘积和
        pSum = sum([prefs[person1][it] * prefs[person2][it] for it in si])

        # 计算皮尔逊评价值
        num = pSum - (sum1*sum2/n)
        den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
        if den == 0:
            return 0
        return num / den


class UserCF:
    """
    基于用户的协同过滤推荐算法类实现
    缺点：基于用户的历史行为数据，存在冷启动问题
    """
    def collectPreferences(self):
        # 搜集偏好，即找不同人对物品的喜好程度
        critics={'Lisa Rose':
                    {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                     'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                     'The Night Listener': 3.0
                    },
                'Gene Seymour':
                    {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                     'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                     'You, Me and Dupree': 3.5
                    },
                'Michael Phillips':
                    {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                     'Superman Returns': 3.5, 'The Night Listener': 4.0
                    },
                'Claudia Puig':
                    {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                     'The Night Listener': 4.5, 'Superman Returns': 4.0,
                     'You, Me and Dupree': 2.5
                    },
                'Mick LaSalle':
                    {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                     'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                     'You, Me and Dupree': 2.0
                    },
                'Jack Matthews':
                    {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                     'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5
                    },
                'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0
                    }
                }

        return critics

    # 为评论者打分，即找最近的K个人
    def topMatches(self, prefs, person, n=5, similarity=similay.sim_pearson):
        scores = [(similarity(self, prefs, person, other), other)
                  for other in prefs if other != person]

        scores.sort()
        scores.reverse()
        return scores[0:n]

    # 推荐物品
    def getRecommendations(self, prefs, person, sililarity=similay.sim_pearson):
        totals = {}
        simSum = {}
        for other in prefs:
            # 不要和自己比较
            if other == person:
                continue

            # 忽略评价值小于等于0的情况
            sim = sililarity(self, prefs, person, other)
            if sim <= 0:
                continue
            for item in prefs[other]:
                # 只对自己还未看过的电影进行评价
                if item not in prefs[person] or prefs[person][item] == 0:
                    # 相似度 * 评价值
                    totals.setdefault(item, 0)
                    totals[item] += prefs[other][item] * sim

                    # 相似度和
                    simSum.setdefault(item, 0)
                    simSum[item] += sim

        # 建立一个归一化的列表
        rankings = [(total / simSum[item], item) for item, total in totals.items()]

        rankings.sort(reverse=True)
        return rankings


class ItemCF:
    """
    基于物品的协同过滤算法，计算对某个物品评论过的所有用户，计算相似物品进行推荐
    """
    def transformPrefs(self, prefs):
        # 商品相似度数据，把人员和物品交换即可
        result = {}
        for person in critics:
            for item in prefs[person]:
                result.setdefault(item, {})
                result[item][person] = prefs[person][item]

        return result

    # 为物品打分，即找最近的k个物品
    def top_matches(self, prefs, item, n=5, similarity=similay.sim_pearson):
        scores = [(similarity(self, prefs, item, other), other) for other in prefs if other != item]

        scores.sort()
        scores.reverse()
        return scores[0:n]

    # 构建物品比较数据集合,即每个item有n个最相关的其它item
    def calculate_similary_items(self, prefs, n=10):
        item_sim = {}
        c = 0
        for item in prefs:
            c += 1.0
            if c % 100 == 0:
                print('%d/%d' % (c, len(prefs)))
            scores = self.top_matches(prefs, item, n=n, similarity=similay.sim_pearson)
            item_sim[item] = scores
        return item_sim

    # 推荐物品
    def get_recommendations(self, prefs, person):
        totalsim = {}
        simSum = {}

        sim_prefs = self.transformPrefs(prefs)
        item_sim = self.calculate_similary_items(sim_prefs, n=10)
        for item, ratio in prefs[person].items():
            for sim, item2 in item_sim[item]:
                totalsim.setdefault(item2, 0)
                totalsim[item2] += sim * ratio  # 相似度* 评分
                simSum.setdefault(item2, 0)
                simSum[item2] += sim

        # 建立一个归一化的列表
        rankings = [(total / simSum[item], item) for item, total in totalsim.items()]
        rankings.sort(reverse=True)
        return rankings


if __name__ == "__main__":
    print('基于用户推荐')
    cls = UserCF()
    critics = cls.collectPreferences()
    scores = cls.topMatches(critics, 'Toby')
    rank = cls.getRecommendations(critics, 'Toby')
    print(rank)

    print('基于物品推荐')
    cls = ItemCF()
    rank = cls.get_recommendations(critics, 'Toby')
    print(rank)


