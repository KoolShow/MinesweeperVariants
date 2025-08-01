#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/28 11:12
# @Author  : Wu_RH
# @FileName: BM.py
"""
[BM]多雷平衡(扫联会2)：每行每列的“多雷雷值”相同。(线索格不一定是多雷规则)
"""
from utils.solver import get_model

from abs.Lrule import AbstractMinesRule
from abs.board import AbstractBoard


class RuleBM(AbstractMinesRule):
    name = "BM"
    subrules = [[True, "[BM]列平衡"], [True, "[BM]行平衡"]]

    def __init__(self, board: AbstractBoard, data=None):
        super().__init__(board, data)
        self.R_1M = None if data is None else int(data)

    def create_constraints(self, board: 'AbstractBoard'):
        model = get_model()
        for key in board.get_interactive_keys():
            boundary_pos = board.boundary(key=key)

            if self.subrules[0][0]:
                row_positions = board.get_row_pos(boundary_pos)
                row_sums = [
                    sum(board.get_variable(_pos) * (2 if board.get_dyed(_pos) else 1)
                        for _pos in board.get_col_pos(pos))
                    for pos in row_positions
                ]
                # 所有 row_sums 相等
                for i in range(1, len(row_sums)):
                    model.Add(row_sums[i] == row_sums[0])
                if self.R_1M:
                    model.Add(row_sums[0] == (self.R_1M // (boundary_pos.y+1)))

            if self.subrules[1][0]:
                col_positions = board.get_col_pos(boundary_pos)
                col_sums = [
                    sum(board.get_variable(_pos) * (2 if board.get_dyed(_pos) else 1)
                        for _pos in board.get_row_pos(pos))
                    for pos in col_positions
                ]
                # 所有 col_sums 相等
                for i in range(1, len(col_sums)):
                    model.Add(col_sums[i] == col_sums[0])
                if self.R_1M:
                    model.Add(col_sums[0] == (self.R_1M // (boundary_pos.x+1)))

    @classmethod
    def method_choose(cls) -> int:
        return 1
