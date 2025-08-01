#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 
# @Time    : 2025/06/10 11:07
# @Author  : xxx
# @FileName: 1L.py
"""
[1L]误差：所有线索均比真实值大1或小1
"""


from abs.Rrule import AbstractClueRule, AbstractClueValue
from abs.board import AbstractBoard, AbstractPosition

from utils.tool import get_logger, get_random
from utils.solver import get_model
from utils.impl_obj import VALUE_QUESS, MINES_TAG


class Rule1L(AbstractClueRule):
    name = "1L"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        random = get_random()
        logger = get_logger()
        for pos, _ in board("N"):
            value = len([_pos for _pos in pos.neighbors(2) if board.get_type(_pos) == "F"])
            if value == 0:
                value = 1
            elif value == 8:
                value = 7
            else:
                value += 1 if random.random() > 0.5 else -1
            board.set_value(pos, Value1L(pos, count=value))
            logger.debug(f"Set {pos} to 1L[{value}]")
        return board

    def clue_class(self):
        return Value1L


class Value1L(AbstractClueValue):
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
        return b'1L'

    def code(self) -> bytes:
        return bytes([self.count])

    def deduce_cells(self, board: 'AbstractBoard') -> bool:
        type_dict = {"N": [], "F": []}
        for pos in self.neighbor:
            t = board.get_type(pos)
            if t in ("", "C"):
                continue
            type_dict[t].append(pos)
        n_num, f_num = len(type_dict["N"]), len(type_dict["F"])
        if n_num == 0:
            return False
        if f_num == self.count + 1:
            for i in type_dict["N"]:
                board.set_value(i, VALUE_QUESS)
            return True
        if n_num + f_num == self.count - 1:
            for i in type_dict["N"]:
                board.set_value(i, MINES_TAG)
            return True
        return False

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
            # 两个布尔变量表示加和为 count + 1 或 count - 1
            b1 = model.NewBoolVar("sum_eq_count_plus_1")
            b2 = model.NewBoolVar("sum_eq_count_minus_1")

            # 将布尔变量与表达式绑定
            model.Add(neighbor_sum == self.count + 1).OnlyEnforceIf(b1)
            model.Add(neighbor_sum != self.count + 1).OnlyEnforceIf(b1.Not())

            model.Add(neighbor_sum == self.count - 1).OnlyEnforceIf(b2)
            model.Add(neighbor_sum != self.count - 1).OnlyEnforceIf(b2.Not())

            model.AddBoolOr([b1, b2])

    def check(self, board: 'AbstractBoard') -> bool:
        neighbor = [board.get_type(pos) for pos in self.neighbor]
        return (f_num := neighbor.count("F")) <= self.count + 1 and self.count - 1 <= f_num + neighbor.count("N")

    def method_choose(self) -> int:
        return 3
