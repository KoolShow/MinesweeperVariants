#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/15 18:07
# @Author  : Wu_RH
# @FileName: generate_puzzle.py.py
import os
import time
from pathlib import Path
import yaml

from abs.board import AbstractBoard
from impl.impl_obj import get_board, ModelGenerateError
from impl.summon import Summon
from impl.summon.summon import GenerateError
from utils.image_create import draw_board
from utils.tool import get_logger, get_random
from utils.impl_obj import get_seed

base_path = Path("config/base_puzzle_config.yaml")
default_path = Path("config/default.yaml")
CONFIG = {}
if default_path.exists():
    with open(default_path, "r", encoding="utf-8") as f:
        CONFIG.update(yaml.safe_load(f))
if base_path.exists():
    with open(base_path, "r", encoding="utf-8") as f:
        CONFIG.update(yaml.safe_load(f))


def main(
        log_lv: str,  # 日志等级
        seed: int,  # 随机种子
        attempts: int,  # 尝试次数
        size: tuple[int, int],  # 题板尺寸
        total: int,  # 总雷数
        rules: list[str],  # 规则id集合
        dye: str,  # 染色规则
        drop_r: bool,  # 在推理时候是否隐藏R推理
        board_class: str,  # 题板的名称
        vice_board: bool,  # 启用删除副板
):
    logger = get_logger(log_lv=log_lv)
    get_random(seed, new=True)
    attempts = 20 if attempts == -1 else attempts
    s = Summon(size=size, total=total, rules=rules, board=board_class,
               drop_r=drop_r, dye=dye, vice_board=vice_board)
    total = s.total
    logger.info(f"total mines: {total}")
    _board = None
    info_list = []
    for attempt_index in range(attempts):
        print(f"尝试第{attempt_index}次...", end="\r")
        get_random(seed, new=True)
        a_time = time.time()
        try:
            _board = s.create_puzzle()
        except ModelGenerateError:
            continue
        except GenerateError:
            continue
        b_time = time.time()
        if _board is None:
            continue
        n_num = len([None for _ in _board("N")])
        logger.info(f"<{attempt_index}>生成用时:{b_time - a_time}s")
        logger.info(f"总雷数: {total}/{n_num}")
        logger.info("\n" + _board.show_board())
        if len([None for _ in _board("NF")]) == total:
            logger.warn("题板生成失败 线索填充无法覆盖全盘")
            continue
        info_list.append([
            b_time - a_time,
            n_num,
            "\n" + _board.show_board(),
            _board.encode(),
            "\n" + s.answer_board_str,
            s.answer_board_code,
            _board
        ])

        break

    if not info_list:
        raise ValueError("未在有效次数内得出结果")

    info_list.sort(key=lambda x: x[0])
    time_used, n_num, board_str, board_code, answer, answer_code, _board = info_list[0]

    rule_text = ""
    for rule in rules:
        rule_text += "[" + (rule.split(CONFIG['delimiter'])[0] if
                            CONFIG['delimiter'] in rule else rule) + "]"
    if rule_text == "":
        rule_text = "[V]"
    if dye:
        rule_text += f"[@{dye}]"
    size_a = 0
    size_b = 0
    size_c = len(_board.get_interactive_keys())
    for key in _board.get_interactive_keys():
        bound = _board.boundary(key)
        size_a = max(size_a, bound.x + 1)
        size_b = max(size_b, bound.y + 1)
    rule_text += f"{size_a}x{size_b}"
    if size_c > 1:
        rule_text += f"x{size_c}"

    if not os.path.exists(CONFIG["output_path"]):
        os.mkdir(CONFIG["output_path"])

    with open(os.path.join(CONFIG["output_path"], "demo.txt"), "a", encoding="utf-8") as f:
        f.write("\n" + ("=" * 100) + "\n\n生成时间" + logger.get_time() + "\n")
        f.write(f"生成用时:{time_used}s\n")
        f.write(f"总雷数: {total}/{n_num}\n")
        f.write(f"种子: {get_seed()}\n")
        f.write(rule_text)
        f.write(board_str)
        f.write(answer)

        f.write(f"\n答案: img -c {answer_code.hex()} ")
        f.write(f"-r \"{rule_text}-R{total}/")
        f.write(f"{n_num}-{get_seed()}\" ")
        f.write("-o answer\n")

        f.write(f"\n题板: img -c {board_code.hex()} ")
        f.write(f"-r \"{rule_text}-R{'*' if drop_r else total}/")
        f.write(f"{n_num}-{get_seed()}\" ")
        f.write("-o demo\n")

    image_bytes = draw_board(board=get_board(board_class)(code=board_code), cell_size=100, output="demo",
                             bottom_text=rule_text + f"-R{'*' if drop_r else total}/{n_num}-{get_seed()}\n")
    draw_board(board=get_board(board_class)(code=answer_code), output="answer", cell_size=100,
               bottom_text=rule_text + f"-R{total}/{n_num}-{get_seed()}\n")

    filepath = os.path.join(CONFIG["output_path"], "demo.png")
    with open(filepath, "wb") as f:
        f.write(image_bytes)
        
    logger.info("\n\n" + "=" * 20 + "\n")
    logger.info("\n生成时间" + logger.get_time() + "\n")
    logger.info(f"生成用时:{time_used}s\n")
    logger.info(f"总雷数: {total}/{n_num}\n")
    logger.info(board_str + "\n")
    logger.info(answer + "\n")
    logger.info(f"{board_code}")
