"""扫雷 AI 求解器 —— 经典扫雷界面"""

import pygame
from engine import MineSweeper
from ai.solver import ai_step
from config import (
    DIFFICULTY_PRESETS, CELL_SIZE,
    WINDOW_BG, GRID_BG,
    COLOR_UNREVEALED, COLOR_REVEALED,
    COLOR_MINE, COLOR_MINE_HIT,
)

pygame.init()

HEADER_HEIGHT = 60
PADDING = 8

NUMBER_COLORS = {
    1: (25, 118, 210), 2: (56, 142, 60),
    3: (211, 47, 47), 4: (123, 31, 162),
    5: (255, 143, 0), 6: (0, 151, 167),
    7: (66, 66, 66), 8: (158, 158, 158),
}


class MinesweeperGUI:
    def __init__(self):
        self.difficulty = "初级"
        self._init_game()
        self._init_ui()

    # ==================== 初始化 ====================

    def _init_game(self):
        preset = DIFFICULTY_PRESETS[self.difficulty]
        self.game = MineSweeper(preset["rows"], preset["cols"], preset["mines"])

    def _init_ui(self):
        cols = self.game.cols
        rows = self.game.rows
        self.grid_w = cols * CELL_SIZE
        self.grid_h = rows * CELL_SIZE
        self.screen_w = max(self.grid_w + PADDING * 2, 500)
        self.screen_h = self.grid_h + HEADER_HEIGHT + PADDING * 2

        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("Minesweeper AI Solver")
        self.clock = pygame.time.Clock()

        font_path = self._find_font()
        self.font_sm = pygame.font.Font(font_path, 14)
        self.font_md = pygame.font.Font(font_path, 18)
        self.font_lg = pygame.font.Font(font_path, 18)
        self.font_counter = pygame.font.Font(font_path, 22)

        # 按钮
        self.btn_rects: dict[str, pygame.Rect] = {}
        self.auto_running = False
        self.auto_delay = 150
        self.auto_timer = 0
        self.ai_message = ""
        self.timer_start = 0
        self.timer_frozen = 0

    @staticmethod
    def _find_font() -> str | None:
        import os, platform
        candidates = []
        if platform.system() == "Windows":
            candidates = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simsun.ttc"]
        elif platform.system() == "Darwin":
            candidates = ["/System/Library/Fonts/PingFang.ttc",
                          "/System/Library/Fonts/STHeiti Light.ttc"]
        else:  # Linux
            candidates = ["/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                          "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                          "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"]
        for p in candidates:
            if os.path.exists(p):
                return p
        return None

    # ==================== 坐标 ====================

    def _grid_rect(self) -> pygame.Rect:
        return pygame.Rect(PADDING, HEADER_HEIGHT, self.grid_w, self.grid_h)

    def _cell_rect(self, r: int, c: int) -> pygame.Rect:
        x = PADDING + c * CELL_SIZE
        y = HEADER_HEIGHT + r * CELL_SIZE
        return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    def _cell_at_pos(self, mx: int, my: int) -> tuple[int, int] | None:
        gr = self._grid_rect()
        if not gr.collidepoint(mx, my):
            return None
        c = (mx - PADDING) // CELL_SIZE
        r = (my - HEADER_HEIGHT) // CELL_SIZE
        if 0 <= r < self.game.rows and 0 <= c < self.game.cols:
            return r, c
        return None

    # ==================== 绘制 ====================

    def _draw_header(self):
        header_rect = pygame.Rect(0, 0, self.screen_w, HEADER_HEIGHT)
        pygame.draw.rect(self.screen, (60, 60, 70), header_rect)

        # 左侧：剩余雷数
        remaining = self.game.mine_count - self.game.flag_count
        txt = self.font_counter.render(f"{remaining:03d}", True, (255, 60, 60))
        self.screen.blit(txt, (PADDING + 2, 16))

        # 中央：控制按钮
        btn_h, gap = 28, 6
        btn_y = 16

        # 游戏状态指示
        if self.game.game_over:
            status_text, status_color = ("胜", (46, 125, 50)) if self.game.win else ("败", (211, 47, 47))
        else:
            status_text, status_color = "", (60, 60, 70)

        auto_label = "停止" if self.auto_running else "自动求解"
        auto_color = (180, 80, 40) if self.auto_running else (50, 150, 50)

        buttons = [
            ("reset",  "重置", (255, 255, 255), (80, 80, 90), 52),
            ("step",   "单步", (255, 255, 255), (70, 130, 70), 52),
            ("auto",   auto_label, (255, 255, 255), auto_color, 70),
            ("begin",  "初级", (255, 255, 255), (80, 100, 140), 48),
            ("inter",  "中级", (255, 255, 255), (80, 100, 140), 48),
            ("expert", "高级", (255, 255, 255), (80, 100, 140), 48),
        ]
        # 高亮当前难度
        diff_map = {"初级": 3, "中级": 4, "高级": 5}
        cur = diff_map.get(self.difficulty, 3)
        buttons[cur] = (buttons[cur][0], buttons[cur][1], (255, 220, 60), (60, 80, 120), buttons[cur][4])

        total_w = sum(b[4] for b in buttons) + gap * 5
        x = (self.screen_w - total_w) // 2
        for name, label, fg, bg, w in buttons:
            rect = pygame.Rect(x, btn_y, w, btn_h)
            pygame.draw.rect(self.screen, bg, rect, border_radius=3)
            t = self.font_sm.render(label, True, fg)
            self.screen.blit(t, t.get_rect(center=rect.center))
            self.btn_rects[name] = rect
            x += w + gap

        # 右侧：耗时（未开始显示000，结束时冻结）
        if self.timer_start == 0:
            elapsed = 0
        elif self.game.game_over:
            if self.timer_frozen == 0:
                self.timer_frozen = (pygame.time.get_ticks() - self.timer_start) // 1000
            elapsed = self.timer_frozen
        else:
            elapsed = (pygame.time.get_ticks() - self.timer_start) // 1000
        elapsed = min(elapsed, 999)
        txt = self.font_counter.render(f"{elapsed:03d}", True, (255, 60, 60))
        self.screen.blit(txt, (self.screen_w - PADDING - txt.get_width() - 2, 16))

        # AI 状态提示（header 底部）
        if self.ai_message:
            t = self.font_sm.render(self.ai_message, True, (200, 200, 200))
            self.screen.blit(t, (PADDING, HEADER_HEIGHT - 18))

    def _draw_grid(self):
        gr = self._grid_rect()
        pygame.draw.rect(self.screen, GRID_BG, gr, 2)

        for r in range(self.game.rows):
            for c in range(self.game.cols):
                cell = self.game.cell_at(r, c)
                rect = self._cell_rect(r, c)

                if cell.is_revealed:
                    color = COLOR_MINE_HIT if cell.is_mine else COLOR_REVEALED
                else:
                    # 3D 凸起效果
                    color = COLOR_UNREVEALED

                pygame.draw.rect(self.screen, color, rect)
                # 格子边框
                if not cell.is_revealed:
                    # 亮边（左上）
                    bright = min(color[0] + 40, 255), min(color[1] + 40, 255), min(color[2] + 40, 255)
                    pygame.draw.line(self.screen, bright, rect.topleft, rect.topright)
                    pygame.draw.line(self.screen, bright, rect.topleft, rect.bottomleft)
                    # 暗边（右下）
                    dark = max(color[0] - 40, 0), max(color[1] - 40, 0), max(color[2] - 40, 0)
                    pygame.draw.line(self.screen, dark, rect.bottomright, rect.bottomleft)
                    pygame.draw.line(self.screen, dark, rect.bottomright, rect.topright)
                else:
                    pygame.draw.rect(self.screen, GRID_BG, rect, 1)

                # 数字
                if cell.is_revealed and not cell.is_mine and cell.adjacent_mines > 0:
                    nc = NUMBER_COLORS.get(cell.adjacent_mines, (0, 0, 0))
                    txt = self.font_lg.render(str(cell.adjacent_mines), True, nc)
                    self.screen.blit(txt, txt.get_rect(center=rect.center))

                # 雷
                if cell.is_revealed and cell.is_mine:
                    cx, cy = rect.center
                    pygame.draw.circle(self.screen, COLOR_MINE, (cx, cy), CELL_SIZE // 4)

                # 旗帜
                if cell.is_flagged:
                    x, y = rect.x, rect.y
                    s = CELL_SIZE
                    px = x + s // 3       # 杆偏左，旗面居中
                    pygame.draw.line(self.screen, (50, 50, 50), (px, y + 5), (px, y + s - 4), 2)
                    pts = [(px, y + 5), (px, y + s // 2 + 2), (px + s // 2, y + s // 3 + 2)]
                    pygame.draw.polygon(self.screen, (220, 40, 40), pts)
                    pygame.draw.polygon(self.screen, (180, 20, 20), pts, 1)


    # ==================== 事件 ====================

    def handle_click(self, mx: int, my: int):
        for name, rect in self.btn_rects.items():
            if rect.collidepoint(mx, my):
                self._on_button(name)
                return

        pos = self._cell_at_pos(mx, my)
        if pos and not self.game.game_over:
            if self.timer_start == 0:
                self.timer_start = pygame.time.get_ticks()
            self.game.reveal(*pos)
            if self.game.game_over:
                self.ai_message = "You Win!" if self.game.win else "Game Over!"

    def handle_right_click(self, mx: int, my: int):
        pos = self._cell_at_pos(mx, my)
        if pos and not self.game.game_over:
            self.game.flag(*pos)

    def _on_button(self, name: str):
        diff_map = {"begin": "初级", "inter": "中级", "expert": "高级"}
        if name in diff_map:
            self.difficulty = diff_map[name]
            self._init_game()
            self._init_ui()
        elif name == "reset":
            self._init_game()
            self.auto_running = False
            self.ai_message = ""
            self.timer_start = 0
            self.timer_frozen = 0
        elif name == "step":
            if not self.game.game_over:
                self.ai_message = ai_step(self.game)
                if not self.game.first_click:
                    self.timer_start = pygame.time.get_ticks()
                    self.timer_frozen = 0
        elif name == "auto":
            self.auto_running = not self.auto_running
            self.ai_message = "自动求解中..." if self.auto_running else ""

    # ==================== 主循环 ====================

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(*event.pos)
                    elif event.button == 3:
                        self.handle_right_click(*event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if not self.game.game_over:
                            self.ai_message = ai_step(self.game)
                    elif event.key == pygame.K_a:
                        self.auto_running = not self.auto_running
                        self.ai_message = "自动求解中..." if self.auto_running else ""
                    elif event.key == pygame.K_r:
                        self._init_game()
                        self.auto_running = False
                        self.ai_message = ""
                        self.timer_start = 0
                        self.timer_frozen = 0
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        diffs = ["初级", "中级", "高级"]
                        self.difficulty = diffs[event.key - pygame.K_1]
                        self._init_game()
                        self._init_ui()

            if self.auto_running and not self.game.game_over:
                self.auto_timer += dt
                if self.auto_timer >= self.auto_delay:
                    self.auto_timer = 0
                    self.ai_message = ai_step(self.game)
                    if self.game.game_over:
                        self.auto_running = False
                        self.ai_message = "You Win!" if self.game.win else "Game Over!"

            self.screen.fill(WINDOW_BG)
            self._draw_grid()
            self.btn_rects.clear()
            self._draw_header()
            pygame.display.flip()

        pygame.quit()

    @classmethod
    def launch(cls):
        gui = cls()
        gui.run()
