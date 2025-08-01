#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/01 20:20
# @Author  : Wu_RH
# @FileName: 2E'2I.py
"""
[2E'2I]自指残缺:字母X周围8格中某7格的雷数如果有N个 则标有X=N的格子必定是雷 7格的方位被当前题板所有线索共享
"""
from typing import List, Union

from abs.Rrule import AbstractClueRule, AbstractClueValue
from abs.board import AbstractBoard, AbstractPosition, MASTER_BOARD
from utils.impl_obj import VALUE_QUESS, VALUE_CROSS, VALUE_CIRCLE
from utils.solver import get_model
from utils.tool import get_logger, get_random

ALPHABET = "ABCDEFGH"


class Rule2Ep2I(AbstractClueRule):
    name = "2E'2I"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__()
        board.generate_board(self.name, (3, 3))
        board.set_config(MASTER_BOARD, "pos_label", True)

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        def apply_offsets(_pos: AbstractPosition):
            nonlocal offsets
            result = []
            for dpos in offsets:
                result.append(_pos.deviation(dpos))
            return result

        pos = board.get_pos(1, 1, self.name)
        logger = get_logger()
        random = get_random()
        board[pos] = Value2Ep2I_7(pos)

        pos_list = [pos for pos, _ in board("N", key=self.name)]
        pos_list = random.sample(pos_list, 7)
        offsets = []
        for pos in pos_list:
            board[pos] = VALUE_CIRCLE
            offsets.append(pos.up().left())
        for pos, _ in board("N", key=self.name):
            board[pos] = VALUE_CROSS

        letter_map = {i: [] for i in range(8)}
        for pos, _ in board("F"):
            if pos.y > 7:
                continue
            letter = ALPHABET[pos.y]
            if pos.x not in letter_map:
                letter_map[pos.x] = []
            letter_map[pos.x].append(letter)

        for pos, _ in board("N"):
            positions = apply_offsets(pos)
            value = board.batch(positions, mode="type", drop_none=True).count("F")
            if not letter_map[value]:
                board.set_value(pos, VALUE_QUESS)
                continue
            letter = random.choice(letter_map[value])
            obj = Value2Ep2I(pos, bytes([ALPHABET.index(letter)]))
            board.set_value(pos, obj)
            logger.debug(f"[2E'2I] put {letter}({value}) at {pos}")

        return board

    def init_clear(self, board: 'AbstractBoard'):
        for pos, obj in board(mode="object", key=self.name):
            if isinstance(obj, Value2Ep2I_7):
                continue
            board[pos] = None

    def clue_class(self):
        return Value2Ep2I


class Value2Ep2I(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.value = code[0]  # 实际为第几列的字母
        self.pos = pos

    def __repr__(self) -> str:
        return f"{ALPHABET[self.value]}"

    @classmethod
    def method_choose(cls) -> int:
        return 1

    @classmethod
    def type(cls) -> bytes:
        return Rule2Ep2I.name.encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])

    def create_constraints(self, board: 'AbstractBoard'):
        # 初始化日志
        logger = get_logger()
        # 初始化模型
        model = get_model()
        # 初始化位置对象 位于X列
        pos = board.get_pos(0, self.value)
        # 获取该列的所有位置
        line = board.get_col_pos(pos)
        # 获取该列的所有变量
        line_vars = board.batch(line, mode="variable")

        # 初始化对照表
        neighbors = []
        for pos2, obj in board(key=Rule2Ep2I.name):
            if isinstance(obj, Value2Ep2I_7):
                continue
            # 题板上的位置和共享的偏移位置
            _positions = [self.pos.deviation(pos2).up().left(), pos2]
            # 第一个为题板对应的变量 第二个为偏移的变量
            if not board.in_bounds(_positions[0]):
                continue
            neighbors.append(board.batch(_positions, mode="variable"))

        # 初始化和值
        sum_vers = []
        for var_to_sum, cond in neighbors:
            # 初始化临时变量
            tmp = model.NewBoolVar(f"included_if_{self.pos}_{var_to_sum}")
            # 如果偏移变量为真 那么tmp为题板的值
            model.Add(tmp == var_to_sum).OnlyEnforceIf(cond)
            # 如果偏移变量为假 那么tmp为0
            model.Add(tmp == 0).OnlyEnforceIf(cond.Not())
            sum_vers.append(tmp)
            logger.trace(f"[2E'2I] new tempVar: {tmp} = if {cond} -> {var_to_sum}")

        for index in range(min(8, len(line_vars))):
            # 获取该列的X=index的变量
            var = line_vars[index]
            # 如果变量为真 那么sum应该相对 反之亦然
            model.Add(sum(sum_vers) != index).OnlyEnforceIf(var.Not())
            logger.trace(f"[2E'2I] sum_tmp == {index} only if {var}")


class Value2Ep2I_7(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.neighbors = pos.neighbors(2)

    def __repr__(self) -> str:
        return "7"

    @classmethod
    def method_choose(cls) -> int:
        return 1

    @classmethod
    def type(cls) -> bytes:
        return Rule2Ep2I.name.encode("ascii") + b"_7"

    def create_constraints(self, board: 'AbstractBoard'):
        get_model().Add(sum(board.batch(self.neighbors, mode="variable")) == 7)
