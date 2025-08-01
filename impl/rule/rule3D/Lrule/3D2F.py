#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 
# @Time    : 2025/06/11 12:14
# @Author  : xxx
# @FileName: 3D2F.py
"""
[3D2F]花田: 染色格中的雷周围六格内恰好有1个雷
"""

from .. import Abstract3DMinesRule
from abs.board import AbstractBoard
from utils.solver import get_model


class Rule2F(Abstract3DMinesRule):
    name = "3D2F"

    def create_constraints(self, board: 'AbstractBoard'):
        model = get_model()
        for pos, dye in board(mode="dye"):
            if not dye:
                continue
            positions = pos.neighbors(1)
            if (_pos := self.up(board, pos)) is not None:
                positions.append(_pos)
            if (_pos := self.down(board, pos)) is not None:
                positions.append(_pos)
            # sum(vals) 表示周围雷数
            sum_vals = sum(board.batch(positions, mode="variable", drop_none=True))
            val = board.get_variable(pos)
            # val 为1时，vals中必须有且仅有一个1
            # 约束：val=1 => sum(vals) == 1
            model.Add(sum_vals == 1).OnlyEnforceIf(val)

    @classmethod
    def method_choose(cls) -> int:
        return 1
