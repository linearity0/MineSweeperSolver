"""AI 求解器入口 —— 编排三层递进策略"""

import random
from engine import MineSweeper
from ai.single_point import single_point_solve
from ai.constraint import constraint_propagation
from ai.probability import probability_guess


def ai_step(game: MineSweeper) -> str:
    """执行一步推理：单点 → 约束 → 概率"""

    if game.game_over:
        return "游戏结束"

    if game.first_click:
        r = random.randint(0, game.rows - 1)
        c = random.randint(0, game.cols - 1)
        game.reveal(r, c)
        return f"首次点击: ({r}, {c})"

    if single_point_solve(game):
        return "单点推理"

    if constraint_propagation(game):
        return "约束传播"

    best = probability_guess(game)
    if best:
        game.reveal(*best)
        return f"概率猜测: ({best[0]}, {best[1]})"

    return "无可用操作"
