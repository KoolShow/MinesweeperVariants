#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/19 20:34
# @Author  : Wu_RH
# @FileName: 2D.py
"""
[2D]偏移: 线索表示上方一格为中心的3x3区域内的总雷数
"""
from abs.Rrule import AbstractClueRule, AbstractClueValue
from abs.board import AbstractBoard, AbstractPosition

from utils.tool import get_logger
from utils.solver import get_model


class Rule2D(AbstractClueRule):
    name = "2D"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        for pos, _ in board("N"):
            value = len([_pos for _pos in pos.up(1).neighbors(2) if board.get_type(_pos) == "F"])
            if board.get_type(pos.up(1)) == "F": value += 1
            board.set_value(pos, Value2D(pos, count=value))
            logger.debug(f"Set {pos} to 2D[{value}]")
        return board

    def clue_class(self):
        return Value2D


class Value2D(AbstractClueValue):
    def __init__(self, pos: AbstractPosition, count: int = 0, code: bytes = None):
        super().__init__(pos, code)
        if code is not None:
            # 从字节码解码
            self.count = code[0]
        else:
            # 直接初始化
            self.count = count
        self.neighbor = self.pos.up(1).neighbors(0, 2)

    def __repr__(self):
        return f"{self.count}"

    @classmethod
    def type(cls) -> bytes:
        return b'2D'

    def code(self) -> bytes:
        return bytes([self.count])

    def deduce_cells(self, board: 'AbstractBoard') -> bool:
        return False

    def create_constraints(self, board: 'AbstractBoard'):
        """创建CP-SAT约束: 周围雷数等于count"""
        model = get_model()

        # 收集周围格子的布尔变量
        neighbor_vars = []
        for neighbor in self.neighbor:  # 8方向相邻格子
            if board.in_bounds(neighbor):
                var = board.get_variable(neighbor)
                neighbor_vars.append(var)

        # 添加约束：周围雷数等于count
        if neighbor_vars:
            model.Add(sum(neighbor_vars) == self.count)

    def check(self, board: 'AbstractBoard') -> bool:
        neighbor = [board.get_type(pos.up(1)) for pos in self.neighbor]
        return (f_num := neighbor.count("F")) <= self.count <= f_num + neighbor.count("N")


    def method_choose(self) -> int:
        return 3
