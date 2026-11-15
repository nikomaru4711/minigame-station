# イライラ棒
import pyxel
from module import GameModule
import random as rnd

class generateMaze:
    PATH=0
    WALL=1
    def generate_maze(width:int, height:int):
        # 引数チェック
        if width < 5 or height < 5:
            raise ValueError("Width and height must be at least 5.")
        if height % 2 == 0:
            height += 1
        if width % 2 == 0:
            width += 1        

        #外周の生成（height行width列）
        maze = [[generateMaze.PATH for _ in range(width)] for _ in range(height)]
        for x in range(width):
            for y in range(height):
                if x == 0 or y == 0 or width - 1 == x or height - 1 == y:
                    maze[y][x] = generateMaze.WALL

        # 内部の生成
        for x in range(2, width - 1, 2):
            for y in range(2, height - 1, 2):
                # 棒を立てる
                maze[y][x] = generateMaze.WALL\
                #倒せるまで繰り返す
                while True:
                    # 倒す方向を決める（1行目は上にも倒せる）
                    if y == 2:
                        direction = rnd.randint(0, 3)
                    else:
                        direction = rnd.randint(0, 2)
                    wall_x = x
                    wall_y = y
                    # 一旦倒す
                    match direction:
                        case 0: #上
                            wall_x -= 1
                        case 1: #右
                            wall_x += 1
                        case 2: #下
                            wall_y += 1
                        case 3: #左
                            wall_y -= 1
                    # 倒せるか判定
                    if maze[wall_y][wall_x] == generateMaze.PATH:
                        maze[wall_y][wall_x] = generateMaze.WALL
                        break
        return maze

class Game01(GameModule):
    def __init__(self, app):
        super().__init__()
        self.app = app  # ← 追加（Qキー用）
        pyxel.mouse(True)
        # ユーザー設定 #####
        self.block_size = 10
        self.stage_color = 13
        # 迷路の開始位置とグリッド数（必ず「奇数」にすると壁とピッタリ合います）
        sx, sy = 50, 50
        self.grid_width = 37
        self.grid_height = 19
        self.s_button_area = (70, 100, 30, 11) #(x,y,w,h)
        ###################
        self.is_hover_start = False
        self.s_button_area
        self.state = "INTRODUCTION"
        self.maze_area = (
            (sx, sy),
            (
                sx + self.grid_width * self.block_size,
                sy + self.grid_height * self.block_size,
            ),
        )

        # スタートとゴールの領域を計算（通路の四隅に配置）
        self.start_area = (
            sx + self.block_size,
            sy + self.block_size,
            self.block_size,
            self.block_size,
        )
        gx_pos = sx + (self.grid_width - 2) * self.block_size
        gy_pos = sy + (self.grid_height - 2) * self.block_size
        self.goal_area = (gx_pos, gy_pos, self.block_size, self.block_size)

        # コースを生成
        self.maze = generateMaze.generate_maze(
            self.grid_width, self.grid_height
        )

    def draw_maze(self):
        # 迷路を直接描画
        (sx, sy), _ = self.maze_area
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.maze[y][x] == generateMaze.WALL:
                    pyxel.rect(
                        sx + x * self.block_size,
                        sy + y * self.block_size,
                        self.block_size,
                        self.block_size,
                        self.stage_color,
                    )

        # スタート、ゴール
        st_x, st_y, sw, sh = self.start_area
        gx, gy, gw, gh = self.goal_area
        pyxel.rect(st_x, st_y, sw, sh, 11)
        pyxel.rect(gx, gy, gw, gh, 14)


    def update(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        # 状態別の処理
        if self.state == "INTRODUCTION":
            self.is_hover_start = self.is_mouse_over_area(self.s_button_area)
            if self.is_hover_start and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                pyxel.mouse(True)
                self.state = "SETUP"
        elif self.state == "SETUP":
            sx, sy, sw, sh = self.start_area
            if (
                sx <= mx <= sx + sw
                and sy <= my <= sy + sh
                and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            ):
                self.state = "PLAY"

        elif self.state == "PLAY":
            # 画面上のピクセル色を見て壁との接触判定
            if pyxel.pget(mx, my) == self.stage_color:
                self.state = "GAMEOVER"

            # ゴールエリア到達判定
            gx, gy, gw, gh = self.goal_area
            if gx <= mx <= gx + gw and gy <= my <= gy + gh:
                self.state = "CLEAR"

            elif self.state in ("GAMEOVER", "CLEAR"):
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    # コースの再生成
                    self.maze = generateMaze.generate_maze(
                        self.grid_width, self.grid_height
                    )
                    self.state = "START"
            return None

    def draw(self):
        pyxel.cls(0)
        (sx, sy), _ = self.maze_area

        if self.state == "INTRODUCTION":
            button_bg_color = 6 if self.is_hover_start else 12
            button_text_color = 13 if self.is_hover_start else 7
            pyxel.text(2, 2, "イライラ棒", 7, self.font10)
            pyxel.text(5, 17, "壁に当たらずにゴールまでマウスを動かそう！", 7, self.font10)
            
            sx, sy, sw, sh = self.s_button_area
            pyxel.rect(sx, sy, sw, sh, button_bg_color)
            pyxel.rectb(sx, sy, sw, sh, 5)
            pyxel.text(sx+2, sy, "START", button_text_color, self.font10)
        elif self.state == "SETUP":
            self.draw_maze()
            pyxel.text(50, 30, "STARTをクリックして開始", 7, self.font10)
        elif self.state == "PLAY":
            self.draw_maze()

        elif self.state == "GAMEOVER":
            pyxel.text(50, 30, "GAME OVER", 8, self.font10)
            self.draw_maze()
        elif self.state == "CLEAR":
            pyxel.text(50, 30, "CLEAR!", 10, self.font10)
            self.draw_maze()