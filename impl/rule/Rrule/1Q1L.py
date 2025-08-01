#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/28 09:43
# @Author  : Wu_RH
# @FileName: 1Q1L.py
"""
[QL]误差无方(扫联会):误差线索比真实值大1或小1，如果线索处在2*2非雷框内，则它是误差线索，反之则是真实值。
"""

from typing import List

from abs.Rrule import AbstractClueValue, AbstractClueRule
from abs.board import AbstractBoard, AbstractPosition
from utils.solver import get_model
from utils.tool import get_logger, get_random


def block(a_pos: AbstractPosition, board: AbstractBoard) -> List[AbstractPosition]:
    b_pos = a_pos.up()
    c_pos = a_pos.left()
    d_pos = b_pos.left()
    return [
        a_pos if board.is_valid(a_pos) else None,
        b_pos if board.is_valid(b_pos) else None,
        c_pos if board.is_valid(c_pos) else None,
        d_pos if board.is_valid(d_pos) else None
    ]


class Rule1Q1L(AbstractClueRule):
    name = "QL"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        random = get_random()
        for pos, _ in board("N"):
            value = len([_pos for _pos in pos.neighbors(2) if board.get_type(_pos) == "F"])
            if value == 0:
                random_value = 1
            elif value == 8:
                random_value = 7
            else:
                if random.random() > 0.5:
                    random_value = (value + 1)
                else:
                    random_value = (value - 1)
            flag = False
            for _pos in block(pos.down().right(), board):
                if _pos is None:
                    continue
                _block = block(_pos, board)
                if None in _block:
                    continue
                if board.batch(_block, "type").count("F") == 0:
                    flag = True
            if flag:
                board.set_value(pos, Value1Q1L(pos, count=random_value))
            else:
                board.set_value(pos, Value1Q1L(pos, count=value))
        return board

    def clue_class(self):
        return Value1Q1L

    def create_constraints(self, board: 'AbstractBoard') -> bool:
        block_map = {}
        model = get_model()
        for pos, _ in board():
            t = model.NewBoolVar("t")
            block_vars = block(pos.down().right(), board)
            if None in block_vars:
                continue
            block_vars = board.batch(block_vars, "variable")
            model.Add(sum(block_vars) == 0).OnlyEnforceIf(t)
            model.Add(sum(block_vars) > 0).OnlyEnforceIf(t.Not())
            block_map[pos] = t
        for pos, obj in board("C"):
            if type(obj) is not Value1Q1L:
                continue
            var_list = []
            for _pos in block(pos, board):
                if _pos is None:
                    continue
                if _pos not in block_map:
                    continue
                var_list.append(block_map[_pos])
            obj.create_constraints_(board, var_list)
        return True


class Value1Q1L(AbstractClueValue):
    def __init__(self, pos: AbstractPosition, count: int = 0, code: bytes = None):
        super().__init__(pos, code)
        if code is not None:
            # 从字节码解码
            self.value = code[0]
        else:
            # 直接初始化
            self.value = count
        self.neighbor = self.pos.neighbors(2)

    def __repr__(self):
        return f"{self.value}"

    @classmethod
    def type(cls) -> bytes:
        return Rule1Q1L.name.encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])

    def create_constraints_(self, board: 'AbstractBoard', var_list: list):
        """创建CP-SAT约束：周围雷数等于count"""
        model = get_model()

        # 收集周围格子的布尔变量
        neighbor_vars = []
        for neighbor in self.neighbor:  # 8方向相邻格子
            if board.in_bounds(neighbor):
                var = board.get_variable(neighbor)
                neighbor_vars.append(var)

        # 添加约束：周围雷数等于count+-1
        if not neighbor_vars:
            return

        neighbor_sum = sum(neighbor_vars)
        # 两个布尔变量表示加和为 count + 1 或 count - 1
        b1 = model.NewBoolVar("[1Q1L]")
        b2 = model.NewBoolVar("[1Q1L]")
        b3 = model.NewBoolVar("[1Q1L]")

        model.Add(sum(var_list) == 0).OnlyEnforceIf(b3.Not())
        model.Add(sum(var_list) > 0).OnlyEnforceIf(b3)

        # 将布尔变量与表达式绑定
        model.Add(neighbor_sum == self.value + 1).OnlyEnforceIf(b1)
        model.Add(neighbor_sum != self.value + 1).OnlyEnforceIf(b1.Not())

        model.Add(neighbor_sum == self.value - 1).OnlyEnforceIf(b2)
        model.Add(neighbor_sum != self.value - 1).OnlyEnforceIf(b2.Not())

        model.Add(neighbor_sum == self.value).OnlyEnforceIf(b3.Not())
        model.Add(neighbor_sum != self.value).OnlyEnforceIf(b3)

        model.Add(sum([b1, b2, b3.Not()]) == 1)

    def method_choose(self) -> int:
        return 1
