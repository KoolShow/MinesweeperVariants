#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 
# @Time    : 2025/06/11 14:25
# @Author  : xxx
# @FileName: 1D.py
"""
[1D]对偶: 雷均有1x2或2x1的矩阵组成
"""

from abs.Lrule import AbstractMinesRule
from abs.board import AbstractBoard
from utils.solver import get_model


class Rule1D(AbstractMinesRule):
    name = "1D"
    subrules = [
        [True, "[1D]"]
    ]

    def create_constraints(self, board: 'AbstractBoard'):
        if not self.subrules[0][0]:
            return

        model = get_model()
        for pos, _ in board():
            positions = pos.neighbors(1)
            # sum(vals) 表示周围雷数
            sum_vals = sum(board.batch(positions, mode="variable", drop_none=True))
            val = board.get_variable(pos)
            # val 为1时，vals中必须有且仅有一个1
            # 约束：val=1 => sum(vals) == 1
            model.Add(sum_vals == 1).OnlyEnforceIf(val)

    def check(self, board: 'AbstractBoard') -> bool:
        for pos, dye in board(mode="dye"):
            positions = pos.neighbors(1)
            types = board.batch(positions, mode="type", drop_none=True)
            if types.count("F") > 1:
                return False
            elif types.count("F") == 1:
                continue
            elif types.count("N") == 0:
                return False
        return True

    @classmethod
    def method_choose(cls) -> int:
        return 3

    def suggest_total(self, info: dict):
        def a(model, total):
            model.AddModuloEquality(0, total, 2)
        info["hard_fns"].append(a)
