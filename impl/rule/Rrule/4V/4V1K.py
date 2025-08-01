#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/04 07:39
# @Author  : Wu_RH
# @FileName: 4V.py
"""
[4V1K]2X'plus: 线索表示数字是两个题板中相同位置的其中一个为中心的马步区域的雷总数
"""

from abs.Rrule import AbstractClueRule, AbstractClueValue
from abs.board import AbstractBoard, AbstractPosition, MASTER_BOARD
from utils.impl_obj import VALUE_QUESS, MINES_TAG
from utils.solver import get_model
from utils.tool import get_random

from . import BOARD_NAME_4V


class Rule4V1K(AbstractClueRule):
    name = "4V1K"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        size = (board.boundary().x + 1, board.boundary().y + 1)
        board.generate_board(BOARD_NAME_4V, size)
        board.set_config(BOARD_NAME_4V, "interactive", True)
        board.set_config(BOARD_NAME_4V, "row_col", True)
        board.set_config(BOARD_NAME_4V, "VALUE", VALUE_QUESS)
        board.set_config(BOARD_NAME_4V, "MINES", MINES_TAG)

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        random = get_random()

        for pos, _ in board():
            neighbors_list = []
            for _key in [MASTER_BOARD, BOARD_NAME_4V]:
                _pos = pos.clone()
                _pos.board_key = _key
                neighbors_list.append(_pos.neighbors(5, 5))
            values = [board.batch(positions, mode="type").count("F") for positions in neighbors_list]
            r_value = 0 if random.random() > 0.7 else 1
            _pos.board_key = MASTER_BOARD
            if board.get_type(_pos) != "F":
                obj = Value4V1K(pos=_pos, code=bytes([values[r_value]]))
                board.set_value(_pos, obj)
            _pos.board_key = BOARD_NAME_4V
            if board.get_type(_pos) != "F":
                obj = Value4V1K(pos=_pos, code=bytes([values[1 - r_value]]))
                board.set_value(_pos, obj)

        return board

    def clue_class(self):
        return Value4V1K

    def create_constraints(self, board: 'AbstractBoard') -> bool:
        return super().create_constraints(board)

    def suggest_total(self, info: dict):
        ub = 0
        for key in info["interactive"]:
            size = info["size"][key]
            ub += size[0] * size[1]
        info["soft_fn"](ub * 0.4)


class Value4V1K(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.neighbors_list = []
        for key in [MASTER_BOARD, BOARD_NAME_4V]:
            _pos = pos.clone()
            _pos.board_key = key
            self.neighbors_list.append(_pos.neighbors(5, 5))
        self.value = code[0]

    @classmethod
    def method_choose(cls) -> int:
        return 1

    @classmethod
    def type(cls) -> bytes:
        return Rule4V1K.name.encode("ascii")

    def __repr__(self) -> str:
        return f"{self.value}"

    def create_constraints(self, board: 'AbstractBoard'):
        model = get_model()

        sum_var = []
        for neighbor in self.neighbors_list:
            var_list = board.batch(neighbor, mode="variable", drop_none=True)
            if var_list:
                b = model.NewBoolVar(f"[{Rule4V1K.name}]tmp")
                model.Add(sum(var_list) == self.value).OnlyEnforceIf(b)
                model.Add(sum(var_list) != self.value).OnlyEnforceIf(b.Not())
                sum_var.append(b)
        model.AddBoolOr(sum_var)

    def code(self) -> bytes:
        return bytes([self.value])
