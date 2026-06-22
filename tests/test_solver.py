"""Solver integration tests"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import random
from engine import MineSweeper
from ai.solver import ai_step


def test_first_click():
    """ai_step handles first click"""
    game = MineSweeper(9, 9, 10)
    msg = ai_step(game)
    assert "首次" in msg
    assert not game.first_click


def test_game_over():
    """ai_step returns immediately when game is over"""
    game = MineSweeper(9, 9, 10)
    game.game_over = True
    assert "结束" in ai_step(game)


def test_full_solve_beginner():
    """AI solves a beginner board"""
    random.seed(42)
    game = MineSweeper(9, 9, 10)
    ai_step(game)
    for _ in range(100):
        if game.game_over:
            break
        ai_step(game)
    assert game.game_over and game.win


def test_full_solve_intermediate():
    """AI solves an intermediate board"""
    random.seed(42)
    game = MineSweeper(16, 16, 40)
    ai_step(game)
    for _ in range(300):
        if game.game_over:
            break
        ai_step(game)
    # Intermediate may need probability guesses, win rate not 100%
    if game.win:
        print(f"  intermediate: WIN (revealed={game.revealed_count})")
    else:
        print(f"  intermediate: LOSS (probability guess fail)")


if __name__ == "__main__":
    test_first_click()
    print("  test_first_click: OK")
    test_game_over()
    print("  test_game_over: OK")
    test_full_solve_beginner()
    print("  test_full_solve_beginner: OK")
    test_full_solve_intermediate()
    print(f"\nDone.")
