#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
SVD：奇异值分解，能够降低数据维度，用在降维，推荐，数据压缩等方向

SVD说明：一般矩阵中的信息通常由一小部分表示，其他的要么是噪声，要么是不相关数据，基于此思想，提出矩阵分解，
    Data(mXn) = U(mXn) X(nXn)V.T(nXn)
    矩阵X，只有只有对角元素，其他元素为0，从大到小排序，这个对角元素成为奇异值（Data*Data.T特征值的平方根）

应用：
1、隐形语义索引(隐形语义分析)：利用SVD的方法进行信息检索
2、推荐系统
"""

import numpy as np


class SVD:
    @staticmethod
    def load_data():
        return [[1, 1, 1, 0, 0],
                [2, 2, 2, 0, 0],
                [5, 5, 5, 0, 0],
                [1, 1, 0, 2, 2],
                [0, 0, 0, 3, 3],
                [0, 0, 0, 1, 1]]

    def svd(self):
        data = self.load_data()
        U, sigma, VT = np.linalg.svd(data)
        print(sigma)

        # 重构原始矩阵
        sig = np.mat([[sigma[0], 0, 0], [0, sigma[1], 0], [0, 0, sigma[2]]])
        re_data = U[:, :3] * sig * VT[:3, :]
        print(re_data)

    def eclu_sim(self, inA, inB):
        # 欧式距离
        return 1.0 / (1.0 + np.linalg.norm(inA, inB))

    def pears_sim(self, inA, inB):
        # 皮尔逊系数
        if len(inA) < 3:  # 少于3个点，两个向量完全相关
            return 1.0
        return 0.5 + 0.5*np.corrcoef(inA, inB, rowvar=0)[0][1]

    def cos_sim(self, inA, inB):
        # 余弦距离
        num = float(inA.T * inB)
        denom = np.linalg.norm(inA, inB)
        return 0.5 + 0.5*(num / denom)


if __name__ == "__main__":
    cls = SVD()
    cls.svd()