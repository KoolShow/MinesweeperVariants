#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 
# @Time    : 2025/06/10 11:07
# @Author  : xxx
# @FileName: 1L.py
"""
[2M^]取模:线索与周围8格的雷数除以2的余数相同
"""


from abs.Rrule import AbstractClueRule, AbstractClueValue
from abs.board import AbstractBoard, AbstractPosition

from utils.tool import get_logger
from utils.solver import get_model


class Rule2M(AbstractClueRule):
    name = "2M^"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        for pos, _ in board("N"):
            value = len([_pos for _pos in pos.neighbors(2)
                         if board.get_type(_pos) == "F"]) % 2
            board.set_value(pos, Value2M(pos, count=value))
            logger.debug(f"Set {pos} to 2M[{value}]")
        return board

    def clue_class(self):
        return Value2M


class Value2M(AbstractClueValue):
    def __init__(self, pos: AbstractPosition, count: int = 0, code: bytes = None):
        super().__init__(pos, code)
        if code is not None:
            # 从字节码解码
            self.count = code[0]
        else:
            # 直接初始化
            self.count = count
        self.neighbor = self.pos.neighbors(2)

    def __repr__(self):
        return f"{self.count}"

    @classmethod
    def type(cls) -> bytes:
        return Rule2M.name.encode("ascii")

    def code(self) -> bytes:
        return bytes([self.count])

    def deduce_cells(self, board: 'AbstractBoard') -> bool:
        return False        # 123123

    def create_constraints(self, board: 'AbstractBoard'):
        """创建CP-SAT约束：周围雷数等于count"""
        model = get_model()

        # 收集周围格子的布尔变量
        neighbor_vars = []
        for neighbor in self.neighbor:  # 8方向相邻格子
            if board.in_bounds(neighbor):
                var = board.get_variable(neighbor)
                neighbor_vars.append(var)

        # 添加约束：周围雷数等于count+-1
        if neighbor_vars:
            neighbor_sum = sum(neighbor_vars)

            b1 = model.NewBoolVar(f"[2M]b1")
            b2 = model.NewBoolVar(f"[2M]b2")
            b3 = model.NewBoolVar(f"[2M]b3")
            b4 = model.NewBoolVar(f"[2M]b3")
            b5 = model.NewBoolVar(f"[2M]b3")

            # 将布尔变量与表达式绑定
            model.Add(neighbor_sum == self.count).OnlyEnforceIf(b1)
            model.Add(neighbor_sum != self.count).OnlyEnforceIf(b1.Not())

            model.Add(neighbor_sum == self.count + 2).OnlyEnforceIf(b2)
            model.Add(neighbor_sum != self.count + 2).OnlyEnforceIf(b2.Not())

            model.Add(neighbor_sum == self.count + 4).OnlyEnforceIf(b3)
            model.Add(neighbor_sum != self.count + 4).OnlyEnforceIf(b3.Not())

            model.Add(neighbor_sum == self.count + 6).OnlyEnforceIf(b4)
            model.Add(neighbor_sum != self.count + 6).OnlyEnforceIf(b4.Not())

            model.Add(neighbor_sum == self.count + 8).OnlyEnforceIf(b5)
            model.Add(neighbor_sum != self.count + 8).OnlyEnforceIf(b5.Not())

            model.AddBoolOr([b1, b2, b3, b4, b5])

    def check(self, board: 'AbstractBoard') -> bool:
        return True

    def method_choose(self) -> int:
        return 1
