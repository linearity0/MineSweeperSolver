"""Engine tests"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from engine import MineSweeper


def test_mine_generation():
    """First click safe zone must have no mines"""
    game = MineSweeper(9, 9, 10)
    game.reveal(4, 4)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            r, c = 4 + dr, 4 + dc
            if 0 <= r < 9 and 0 <= c < 9:
                assert not game.cell_at(r, c).is_mine


def test_mine_count():
    """Total mine count must match"""
    game = MineSweeper(9, 9, 10)
    game.reveal(4, 4)
    count = sum(1 for r in range(9) for c in range(9) if game.cell_at(r, c).is_mine)
    assert count == 10


def test_reveal_mine():
    """Revealing a mine triggers game over"""
    game = MineSweeper(3, 3, 1)
    game.first_click = False
    game.grid[1][1].is_mine = True
    result = game.reveal(1, 1)
    assert game.game_over and not game.win
    assert game.cell_at(1, 1).is_revealed
    assert result == [(1, 1)]


def test_reveal_flagged():
    """Cannot reveal a flagged cell"""
    game = MineSweeper(3, 3, 0)
    game.flag(1, 1)
    assert game.reveal(1, 1) == []
    assert not game.cell_at(1, 1).is_revealed


def test_win_condition():
    """Win when all non-mine cells are revealed"""
    game = MineSweeper(3, 3, 1)
    game.first_click = False
    game.grid[0][0].is_mine = True
    game.mine_count = 1
    for r in range(3):
        for c in range(3):
            if (r, c) != (0, 0):
                game.reveal(r, c)
    assert game.game_over and game.win


def test_flag_toggle():
    """Flag toggles correctly"""
    game = MineSweeper(3, 3, 0)
    game.flag(1, 1)
    assert game.cell_at(1, 1).is_flagged
    assert game.flag_count == 1
    game.flag(1, 1)
    assert not game.cell_at(1, 1).is_flagged
    assert game.flag_count == 0


def test_get_covered_cells():
    """get_covered_cells excludes revealed and flagged cells"""
    game = MineSweeper(3, 3, 1)
    game.first_click = False
    game.grid[1][1].is_mine = True
    game.mine_count = 1
    game.grid[0][0].is_revealed = True
    game.grid[0][0].adjacent_mines = 0
    game.revealed_count = 1
    game.flag(0, 1)
    covered = game.get_covered_cells()
    assert (0, 0) not in covered
    assert (0, 1) not in covered
    assert (1, 1) in covered


def test_adjacent_flagged():
    """Count adjacent flagged neighbors"""
    game = MineSweeper(3, 3, 0)
    game.flag(0, 0)
    game.flag(0, 1)
    assert game.count_adjacent_flagged(1, 1) == 2


def test_get_neighbors_corner():
    """Corner cell has fewer neighbors"""
    game = MineSweeper(3, 3, 0)
    assert len(game.get_neighbors(0, 0)) == 3
    assert len(game.get_neighbors(1, 1)) == 8


def test_bfs_flood_fill():
    """Revealing a blank cell triggers BFS expansion"""
    game = MineSweeper(5, 5, 0)
    game.first_click = False
    # No mines -> first reveal should expand to entire board
    new = game.reveal(2, 2)
    assert len(new) == 25
    assert game.game_over and game.win


# ==================== Run ====================

if __name__ == "__main__":
    tests = [
        test_mine_generation, test_mine_count, test_reveal_mine,
        test_reveal_flagged, test_win_condition, test_flag_toggle,
        test_get_covered_cells, test_adjacent_flagged,
        test_get_neighbors_corner, test_bfs_flood_fill,
    ]
    for t in tests:
        t()
        print(f"  {t.__name__}: OK")
    print(f"\n{len(tests)} tests passed!")
