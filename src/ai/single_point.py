"""第一层AI：单点推理"""

from engine import MineSweeper


def single_point_solve(game: MineSweeper) -> bool:
    """遍历已翻开数字格，用直接规则做确定性推理。

    规则1：剩余雷数 == 未翻邻居数 → 全部标雷
    规则2：剩余雷数 == 0 → 全部安全
    """
    action_taken = False

    for r in range(game.rows):
        for c in range(game.cols):
            cell = game.cell_at(r, c)
            if not cell.is_revealed or cell.adjacent_mines == 0:
                continue

            covered = game.get_adjacent_covered(r, c)
            if not covered:
                continue

            flagged = game.count_adjacent_flagged(r, c)
            remaining = cell.adjacent_mines - flagged

            if remaining == 0:
                for nr, nc in covered:
                    game.reveal(nr, nc)
                action_taken = True
            elif remaining == len(covered):
                for nr, nc in covered:
                    if not game.cell_at(nr, nc).is_flagged:
                        game.flag(nr, nc)
                action_taken = True

    return action_taken
