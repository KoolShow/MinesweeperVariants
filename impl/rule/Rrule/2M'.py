#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/10 18:09
# @Author  : Wu_RH
# @FileName: 1M.py
"""
[2M']多雷: 每个下方是雷的雷被视为两个(总雷数不受限制)
"""

from abs.board import AbstractBoard, AbstractPosition
from abs.Rrule import AbstractClueRule, AbstractClueValue
from utils.solver import get_model
from utils.tool import get_logger
from utils.impl_obj import VALUE_QUESS, MINES_TAG


class Rule1M(AbstractClueRule):
    name = "2M'"

    def fill(self, board: 'AbstractBoard'):
        logger = get_logger()
        for pos, _ in board("N"):
            positions = pos.neighbors(2)
            positions_d = pos.down().neighbors(2)
            value = 0
            for t, d in zip(
                    board.batch(positions, "type"),
                    board.batch(positions_d, "type")
            ):
                if t != "F":
                    continue
                if d == "F":
                    value += 2
                else:
                    value += 1
            obj = Value1M(pos, code=bytes([value]))
            board.set_value(pos, obj)
            logger.debug(f"[1M]: put {obj} to {pos}")
        return board

    def clue_class(self):
        return Value1M


class Value1M(AbstractClueValue):
    value: int
    neighbors: list

    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        super().__init__(pos)
        self.value = code[0]
        self.neighbors = pos.neighbors(2)

    def __repr__(self) -> str:
        return f"{self.value}"

    @classmethod
    def type(cls) -> bytes:
        return Rule1M.name.encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])

    def create_constraints(self, board: 'AbstractBoard'):
        model = get_model()
        vals = []
        for pos in self.neighbors:
            if board.get_type(pos) != "N":
                continue
            if not board.is_valid(pos.down()):
                a = board.get_variable(pos)
            else:
                a = model.NewIntVar(0, 2, "")
                model.Add(a == board.get_variable(pos)).OnlyEnforceIf(board.get_variable(pos.down()).Not())
                model.Add(a == board.get_variable(pos) * 2).OnlyEnforceIf(board.get_variable(pos.down()))
            vals.append(a)
        if vals:
            model.Add(sum(vals) == self.value)

    def check(self, board: 'AbstractBoard') -> bool:
        min_value = 0
        max_value = 0
        dyes = board.batch(self.neighbors, "dye")
        for pos, dye in zip(self.neighbors, dyes):
            if board.get_type(pos) == "F":
                min_value += 2 if dye else 1
                max_value += 2 if dye else 1
            elif board.get_type(pos) == "N":
                max_value += 2 if dye else 1
        return min_value < self.value < max_value

    @classmethod
    def method_choose(cls) -> int:
        return 3
