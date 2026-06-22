"""扫雷游戏引擎"""

from dataclasses import dataclass
from collections import deque
import random

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),           (0, 1),
              (1, -1),  (1, 0),  (1, 1)]


@dataclass
class Cell:
    is_mine: bool = False
    is_revealed: bool = False
    is_flagged: bool = False
    adjacent_mines: int = 0


class MineSweeper:
    def __init__(self, rows: int, cols: int, mine_count: int):
        self.rows = rows
        self.cols = cols
        self.mine_count = mine_count
        self.grid = [[Cell() for _ in range(cols)] for _ in range(rows)]
        self.game_over = False
        self.win = False
        self.first_click = True
        self.revealed_count = 0
        self.flag_count = 0

    def generate_mines(self, safe_row: int, safe_col: int):
        """首次点击后，在安全区外随机布雷并计算邻雷数"""
        if not self.is_valid_position(safe_row, safe_col):
            raise ValueError("Invalid safe position")

        safe_zone = {(safe_row, safe_col)}
        for dr, dc in DIRECTIONS:
            r, c = safe_row + dr, safe_col + dc
            if self.is_valid_position(r, c):
                safe_zone.add((r, c))

        all_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)
                     if (r, c) not in safe_zone]
        mine_positions = random.sample(all_cells, self.mine_count)

        for r, c in mine_positions:
            self.grid[r][c].is_mine = True

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if not cell.is_mine:
                    for nr, nc in self.get_neighbors(r, c):
                        if self.grid[nr][nc].is_mine:
                            cell.adjacent_mines += 1

    def reveal(self, r: int, c: int) -> list[tuple[int, int]]:
        """掀开格子。空白格 BFS 自动扩散。返回本次新掀开格列表"""
        if not self.is_valid_position(r, c):
            raise ValueError("Invalid position")

        cell = self.grid[r][c]
        if cell.is_revealed or cell.is_flagged:
            return []

        if self.first_click:
            self.generate_mines(r, c)
            self.first_click = False

        if cell.is_mine:
            cell.is_revealed = True
            self.game_over = True
            return [(r, c)]

        new_revealed = [(r, c)]
        q = deque([(r, c)])
        cell.is_revealed = True
        self.revealed_count += 1

        while q:
            cr, cc = q.popleft()
            if self.grid[cr][cc].adjacent_mines > 0:
                continue
            for nr, nc in self.get_neighbors(cr, cc):
                nb = self.grid[nr][nc]
                if not nb.is_revealed and not nb.is_flagged and not nb.is_mine:
                    nb.is_revealed = True
                    new_revealed.append((nr, nc))
                    self.revealed_count += 1
                    q.append((nr, nc))

        if self.revealed_count == self.rows * self.cols - self.mine_count:
            self.game_over = True
            self.win = True
        return new_revealed

    def flag(self, r: int, c: int):
        """切换标记状态"""
        if not self.is_valid_position(r, c):
            return
        cell = self.grid[r][c]
        if cell.is_revealed:
            return
        cell.is_flagged = not cell.is_flagged
        self.flag_count += 1 if cell.is_flagged else -1

    def is_valid_position(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def cell_at(self, r: int, c: int) -> Cell:
        if not self.is_valid_position(r, c):
            raise ValueError("Invalid position")
        return self.grid[r][c]

    def get_neighbors(self, r: int, c: int) -> list[tuple[int, int]]:
        """返回周围8格中合法坐标的列表"""
        neighbors = []
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if self.is_valid_position(nr, nc):
                neighbors.append((nr, nc))
        return neighbors

    def get_covered_cells(self) -> list[tuple[int, int]]:
        """返回所有未掀开且未标记的格子"""
        covered = []
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if not cell.is_revealed and not cell.is_flagged:
                    covered.append((r, c))
        return covered

    def get_adjacent_covered(self, r: int, c: int) -> list[tuple[int, int]]:
        """返回 (r,c) 周围未掀开且未标记的格子"""
        covered = []
        for nr, nc in self.get_neighbors(r, c):
            cell = self.grid[nr][nc]
            if not cell.is_revealed and not cell.is_flagged:
                covered.append((nr, nc))
        return covered

    def count_adjacent_flagged(self, r: int, c: int) -> int:
        """返回 (r,c) 周围已标记的格子数"""
        count = 0
        for nr, nc in self.get_neighbors(r, c):
            if self.grid[nr][nc].is_flagged:
                count += 1
        return count

    def to_state(self) -> dict:
        """导出棋盘状态字典，不暴露雷位"""
        state = {}
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell.is_revealed:
                    state[(r, c)] = cell.adjacent_mines
                elif cell.is_flagged:
                    state[(r, c)] = -1
                else:
                    state[(r, c)] = -2
        return state
