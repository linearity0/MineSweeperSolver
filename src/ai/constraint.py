"""第二层AI：约束方程组推理 —— 约束子集减法"""

from engine import MineSweeper


class Constraint:
    """cells 中恰好有 mines 颗雷"""

    def __init__(self, cells: set[tuple[int, int]], mines: int):
        self.cells = frozenset(cells)
        self.mines = mines

    def __eq__(self, other):
        return self.cells == other.cells and self.mines == other.mines

    def __hash__(self):
        return hash((self.cells, self.mines))


def build_initial_constraints(game: MineSweeper) -> list[Constraint]:
    """从已翻开数字格构建初始约束集（去重）"""
    constraints = []
    seen = set()

    for r in range(game.rows):
        for c in range(game.cols):
            cell = game.cell_at(r, c)
            if not cell.is_revealed or cell.adjacent_mines == 0:
                continue

            covered = set(game.get_adjacent_covered(r, c))
            if not covered:
                continue

            flagged = game.count_adjacent_flagged(r, c)
            remaining = max(0, cell.adjacent_mines - flagged)
            c_obj = Constraint(covered, remaining)
            key = (c_obj.cells, c_obj.mines)
            if key not in seen:
                seen.add(key)
                constraints.append(c_obj)

    return constraints


def deduce(constraints: list[Constraint]) -> list[Constraint]:
    """对所有约束对做子集减法推导新约束（去重）"""
    new_constraints = []
    seen = {(c.cells, c.mines) for c in constraints}

    for c1 in constraints:
        for c2 in constraints:
            if c1.cells.issubset(c2.cells) and c1 != c2:
                diff_cells = c2.cells - c1.cells
                diff_mines = c2.mines - c1.mines
                if diff_cells and 0 <= diff_mines <= len(diff_cells):
                    key = (diff_cells, diff_mines)
                    if key not in seen:
                        seen.add(key)
                        new_constraints.append(Constraint(diff_cells, diff_mines))

    return new_constraints


def extract_actions(constraints: list[Constraint]) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """提取确定性动作：mines==0 全安全，mines==len(cells) 全雷"""
    safe_cells = []
    mine_cells = []

    for c in constraints:
        if c.mines == 0:
            safe_cells.extend(c.cells)
        elif c.mines == len(c.cells):
            mine_cells.extend(c.cells)

    return safe_cells, mine_cells


def constraint_propagation(game: MineSweeper) -> bool:
    """约束传播主循环：构建约束 → 多轮推导 → 执行动作 → 重复"""
    action_taken = False

    for _ in range(10):
        constraints = build_initial_constraints(game)
        for _ in range(10):
            new = deduce(constraints)
            if not new:
                break
            constraints.extend(new)

        safe, mines = extract_actions(constraints)
        if not safe and not mines:
            return action_taken
        action_taken = True

        for r, c in safe:
            if not game.cell_at(r, c).is_revealed:
                game.reveal(r, c)
        for r, c in mines:
            if not game.cell_at(r, c).is_flagged:
                game.flag(r, c)

    return action_taken
