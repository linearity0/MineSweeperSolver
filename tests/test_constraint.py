"""Constraint solver tests"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from engine import MineSweeper
from ai.single_point import single_point_solve
from ai.constraint import (
    Constraint, build_initial_constraints, deduce,
    extract_actions, constraint_propagation,
)


def test_dedup():
    """build_initial_constraints deduplicates identical constraints"""
    game = MineSweeper(3, 3, 0)
    game.first_click = False
    game.grid[0][0].is_revealed = True
    game.grid[0][0].adjacent_mines = 1
    game.grid[0][1].is_revealed = True
    game.grid[0][1].adjacent_mines = 1
    clist = build_initial_constraints(game)
    assert len(clist) <= 2


def test_deduce_subset():
    """Subset deduction: {A,B}=1, {A,B,C}=2 -> {C}=1"""
    c1 = Constraint({(0, 0), (1, 0)}, 1)
    c2 = Constraint({(0, 0), (1, 0), (1, 1)}, 2)
    new = deduce([c1, c2])
    assert len(new) == 1
    assert new[0].cells == frozenset({(1, 1)})
    assert new[0].mines == 1


def test_deduce_no_subset():
    """No deduction when no subset relationship"""
    c1 = Constraint({(0, 0)}, 1)
    c2 = Constraint({(1, 1)}, 1)
    assert len(deduce([c1, c2])) == 0


def test_extract_actions():
    """mines==0 safe, mines==len(cells) mine"""
    c1 = Constraint({(0, 0)}, 1)
    c2 = Constraint({(1, 0), (1, 1)}, 0)
    safe, mines = extract_actions([c1, c2])
    assert (1, 0) in safe and (1, 1) in safe
    assert (0, 0) in mines


def test_edge_11():
    """Edge 11 pattern solved by constraint propagation"""
    game = MineSweeper(3, 3, 1)
    game.first_click = False
    game.grid[0][1].is_revealed = True
    game.grid[0][1].adjacent_mines = 1
    game.grid[0][2].is_revealed = True
    game.grid[0][2].adjacent_mines = 1
    game.revealed_count = 2
    game.grid[1][2].is_mine = True
    game.mine_count = 1

    assert not single_point_solve(game)
    assert constraint_propagation(game)
    assert game.cell_at(0, 0).is_revealed
    assert game.cell_at(1, 0).is_revealed
    assert game.cell_at(1, 2).is_flagged


def test_121_pattern():
    """121 pattern: A and C are mines, B is safe"""
    game = MineSweeper(4, 3, 2)
    game.first_click = False
    game.grid[0][0].is_revealed = True
    game.grid[0][0].adjacent_mines = 1
    game.grid[0][1].is_revealed = True
    game.grid[0][1].adjacent_mines = 2
    game.grid[0][2].is_revealed = True
    game.grid[0][2].adjacent_mines = 1
    game.revealed_count = 3
    game.grid[1][0].is_mine = True
    game.grid[1][2].is_mine = True
    game.mine_count = 2

    assert not single_point_solve(game)
    assert constraint_propagation(game)
    assert game.cell_at(1, 1).is_revealed
    assert game.cell_at(1, 0).is_flagged
    assert game.cell_at(1, 2).is_flagged


def test_no_deduction():
    """constraint_propagation returns False when nothing to deduce"""
    game = MineSweeper(3, 3, 0)
    game.first_click = False
    game.grid[1][1].is_revealed = True
    game.grid[1][1].adjacent_mines = 1
    game.revealed_count = 1
    assert not constraint_propagation(game)


if __name__ == "__main__":
    tests = [test_dedup, test_deduce_subset, test_deduce_no_subset,
             test_extract_actions, test_edge_11, test_121_pattern,
             test_no_deduction]
    for t in tests:
        t()
        print(f"  {t.__name__}: OK")
    print(f"\n{len(tests)} tests passed!")
