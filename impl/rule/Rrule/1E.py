#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/09 10:32
# @Author  : Wu_RH
# @FileName: 1E.py
"""
[1E] 视野 (Eyesight)：线索表示四方向上能看到的非雷格数量（包括自身），雷会阻挡视线
"""
from typing import Callable

from abs.Rrule import AbstractClueRule, AbstractClueValue
from abs.board import AbstractBoard, AbstractPosition
from utils.solver import get_model


class Rule1E(AbstractClueRule):
    name = "1E"

    def clue_class(self):
        return Value1E

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        fn: Callable[[int], AbstractPosition]
        for pos, _ in board("N"):
            value = 1
            for fn in [pos.up, pos.down, pos.left, pos.right]:
                n = 1
                while board.get_type(fn(n)) not in "F":
                    n += 1
                    value += 1
            obj = Value1E(pos, bytes([value]))
            board.set_value(pos, obj)
        return board


class Value1E(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.value = code[0]
        self.pos = pos

    def __repr__(self):
        return str(self.value)

    @classmethod
    def method_choose(cls) -> int:
        return 1

    @classmethod
    def type(cls) -> bytes:
        return Rule1E.name.encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])

    def create_constraints(self, board: 'AbstractBoard'):
        def dfs(value: int, index=0, info: dict = None):
            if info is None:
                info = {"T": [], "F": []}
            if index == 4:
                if value == 1:
                    possible_list.append((set(info["T"]), [var for var in info["F"] if var is not None]))
                return
            fn = [self.pos.up, self.pos.down, self.pos.left, self.pos.right][index]
            fn: Callable[[int], AbstractPosition]
            for i in range(value):
                _var_t = board.get_variable(fn(i))
                if _var_t is None:
                    dfs(value - i, index + 1, info)
                    break
                _var_f = board.get_variable(fn(i + 1))
                info["T"].append(_var_t)
                info["F"].append(_var_f)
                dfs(value - i, index + 1, info)
                info["F"].pop(-1)
            for i in range(value):
                if board.get_variable(fn(i)) is None:
                    continue
                info["T"].pop(-1)

        model = get_model()

        possible_list = []

        dfs(value=self.value)
        tmp_list = []

        for vars_t, vars_f in possible_list:
            tmp = model.NewBoolVar("tmp")
            model.Add(sum(vars_t) == 0).OnlyEnforceIf(tmp)
            model.AddBoolAnd(vars_f).OnlyEnforceIf(tmp)
            tmp_list.append(tmp)
        model.AddBoolOr(tmp_list)
