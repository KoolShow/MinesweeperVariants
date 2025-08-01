#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/15 16:34
# @Author  : Wu_RH
# @FileName: 1H2H.py
"""
[1H2H]: 在每一行中, 要么都没有横向相邻的雷，要么都至少有一个横向相邻的雷。
"""
from abs.Lrule import AbstractMinesRule
from abs.board import AbstractBoard
from utils.solver import get_model


class Rule1H(AbstractMinesRule):
    name = "1H2H"
    subrules = [
        [True, "[1H2H]"]
    ]

    def create_constraints(self, board: 'AbstractBoard'):
        if not self.subrules[0][0]:
            return
        model = get_model()
        for key in board.get_interactive_keys():
            pos_bound = board.boundary(key)
            for _pos in board.get_col_pos(pos_bound):
                tmp = model.NewBoolVar("tmp")
                for pos in board.get_row_pos(_pos):
                    var = board.get_variable(pos)
                    pos_vars = []
                    if board.in_bounds(pos.right()):
                        pos_vars.append(board.get_variable(pos.right()))
                    if board.in_bounds(pos.left()):
                        pos_vars.append(board.get_variable(pos.left()))
                    model.Add(sum(pos_vars) == 0).OnlyEnforceIf([var, tmp])
                    model.AddBoolOr(pos_vars).OnlyEnforceIf([var, tmp.Not()])

    @classmethod
    def method_choose(cls) -> int:
        return 1
