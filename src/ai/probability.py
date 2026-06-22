"""第三层AI：蒙特卡洛采样概率评估"""

import random
from engine import MineSweeper
from ai.constraint import build_initial_constraints


def probability_guess(game: MineSweeper, samples: int = 500) -> tuple[int, int] | None:
    """蒙特卡洛采样，返回含雷概率最低的格子"""
    covered = game.get_covered_cells()
    if not covered:
        return None

    constraints = build_initial_constraints(game)
    mine_count = {cell: 0 for cell in covered}

    for _ in range(samples):
        config = _sample_config(game, covered, constraints)
        for cell, is_mine in config.items():
            if is_mine:
                mine_count[cell] += 1

    return min(covered, key=lambda cell: mine_count[cell])


def _sample_config(game, covered, constraints) -> dict[tuple[int, int], bool]:
    """生成一个满足所有约束的随机雷区配置"""
    config = {cell: False for cell in covered}

    remaining_mines = game.mine_count - game.flag_count
    mine_ratio = remaining_mines / len(covered) if covered else 0
    for cell in covered:
        config[cell] = random.random() < mine_ratio

    for _ in range(100):
        violated = False
        random.shuffle(constraints)
        for c in constraints:
            current = sum(config[cell] for cell in c.cells)
            diff = current - c.mines
            if diff == 0:
                continue

            violated = True
            members = [cell for cell in c.cells if cell in config]
            random.shuffle(members)
            if diff > 0:
                for cell in members:
                    if diff == 0:
                        break
                    if config[cell]:
                        config[cell] = False
                        diff -= 1
            else:
                for cell in members:
                    if diff == 0:
                        break
                    if not config[cell]:
                        config[cell] = True
                        diff += 1
        if not violated:
            break

    return config
