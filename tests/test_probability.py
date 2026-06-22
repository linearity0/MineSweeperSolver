"""Probability tests"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from engine import MineSweeper
from ai.probability import probability_guess


def test_returns_covered_cell():
    """Returns a valid unrevealed cell"""
    game = MineSweeper(3, 3, 1)
    game.first_click = False
    game.grid[1][1].is_mine = True
    game.mine_count = 1
    game.grid[0][0].is_revealed = True
    game.grid[0][0].adjacent_mines = 0
    game.revealed_count = 1
    result = probability_guess(game)
    assert result is not None
    r, c = result
    assert not game.cell_at(r, c).is_revealed


def test_returns_none_when_all_revealed():
    """Returns None when no covered cells remain"""
    game = MineSweeper(3, 3, 1)
    game.first_click = False
    for r in range(3):
        for c in range(3):
            game.grid[r][c].is_revealed = True
    assert probability_guess(game) is None


def test_picks_safest():
    """With a known safe cell, should pick it"""
    game = MineSweeper(3, 3, 1)
    game.first_click = False
    game.grid[0][0].is_mine = True
    game.mine_count = 1
    game.grid[0][2].is_revealed = True
    game.grid[0][2].adjacent_mines = 0
    game.revealed_count = 1
    result = probability_guess(game, samples=300)
    assert result is not None
    # (0,0) is mine, so it should NOT be picked with high confidence
    # This is probabilistic — small chance of failure
    for _ in range(3):
        if result != (0, 0):
            break
        result = probability_guess(game, samples=300)
    assert result != (0, 0)


if __name__ == "__main__":
    tests = [test_returns_covered_cell, test_returns_none_when_all_revealed,
             test_picks_safest]
    for t in tests:
        t()
        print(f"  {t.__name__}: OK")
    print(f"\n{len(tests)} tests passed!")
