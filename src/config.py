"""游戏配置"""


class Difficulty:
    BEGINNER = "初级"
    INTERMEDIATE = "中级"
    EXPERT = "高级"


DIFFICULTY_PRESETS = {
    "初级": {"rows": 9, "cols": 9, "mines": 10},
    "中级": {"rows": 16, "cols": 16, "mines": 40},
    "高级": {"rows": 16, "cols": 30, "mines": 99},
}

# 界面配置
CELL_SIZE = 30
PANEL_WIDTH = 220
GRID_OFFSET_X = 10
GRID_OFFSET_Y = 60
WINDOW_BG = (240, 240, 245)
GRID_BG = (200, 200, 210)

# 格子颜色
COLOR_UNREVEALED = (180, 180, 190)
COLOR_REVEALED = (230, 230, 235)
COLOR_FLAGGED = (220, 80, 80)
COLOR_MINE = (40, 40, 40)
COLOR_MINE_HIT = (255, 60, 60)

# 数字颜色
NUMBER_COLORS = {
    1: (25, 118, 210),
    2: (56, 142, 60),
    3: (211, 47, 47),
    4: (123, 31, 162),
    5: (255, 143, 0),
    6: (0, 151, 167),
    7: (66, 66, 66),
    8: (158, 158, 158),
}

# AI 高亮
COLOR_AI_REVEAL = (100, 220, 130)
COLOR_AI_FLAG = (255, 160, 80)

# AI 速度（毫秒/步）
AI_SPEED_FAST = 100
AI_SPEED_NORMAL = 300
AI_SPEED_SLOW = 800
