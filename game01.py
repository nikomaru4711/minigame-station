# イライラ棒
import pyxel
import random as rnd

class generateMaze:
    PATH=0
    WALL=1
    def generate_maze(width:int, height:int):# 前提として開始位置が0,0の可能性あり
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
                    # 倒す方向を決める（1行目🍻上にも倒せる）
                    if y == 2:
                        direction = rnd.randint(0, 3)
                    else:
                        direction = rnd.randint(0, 2)
                    wall_x = x
                    wall_y = y
                    # 一旦倒す
                    match direction:
                        case 0: #上
                            wall_y -= 1
                        case 1: #右
                            wall_x += 1
                        case 2: #下
                            wall_y += 1
                        case 3: #左
                            wall_x -= 1
                    # 倒せるか判定
                    if maze[wall_y][wall_x] == generateMaze.PATH:
                        maze[wall_y][wall_x] = generateMaze.WALL
                        break
        return maze

class Game01:
    def __init__(self, app):
        self.font12 = app.font12
        self.state = "START"
        pyxel.mouse(True)
        # ユーザー設定 #####
        # 440, 250
        self.maze_area = ((0,0), (pyxel.width, pyxel.height))
        self.block_size = 8
        self.stage_color = 13
        ###################
        (sx, sy), (tx, ty) = self.maze_area
        self.maze_width = tx - sx
        self.maze_height = ty - sx

        if self.maze_width % self.block_size != 0 or self.maze_height % self.block_size != 0:
            raise ValueError("迷路の幅はブロックサイズの倍数である必要があります。")
        # グリットの数（100pxにblocksizeが5なら20グリット）
        self.grid_width = pyxel.width / self.block_size
        self.grid_height = pyxel.height / self.block_size

        # スタート地点の領域を計算 ##############
        gx_pos = tx - self.block_size*2
        gy_pos = ty - self.block_size*2
        self.start_area = (sx + self.block_size, sy + self.block_size, self.block_size, self.block_size)
        self.goal_area = (gx_pos, gy_pos , self.block_size, self.block_size)
        #######################################
        # コースを生成 
        self.create_course()

    def create_course(self):
        # 迷路を生成
        maze = generateMaze.generate_maze(int(self.grid_width), int(self.grid_height))
        # imeges0に迷路情報を追加
        img = pyxel.images[0]
        img.cls(0)

        for x in range(int(self.grid_width)):
            for y in range(int(self.grid_height)):
                if maze[y][x] == generateMaze.WALL:
                    img.rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size, self.stage_color)


    def update(self):
        if(pyxel.btnp(pyxel.KEY_Q)):
            self.app.change_scene("Title")
            return "Title"
        
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        if self.state == "START":
            # スタートエリア内でクリックするとゲーム開始
            sx, sy, sw, sh = self.start_area
            if (
                sx <= mx <= sx + sw
                and sy <= my <= sy + sh
                and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            ):
                self.state = "PLAY"

        elif self.state == "PLAY":
            # 壁との接触判定
            if pyxel.images[0].pget(mx, my) == self.stage_color:
                self.state = "GAMEOVER"

            # ゴールエリア到達判定
            gx, gy, gw, gh = self.goal_area
            if gx <= mx <= gx + gw and gy <= my <= gy + gh:
                self.state = "CLEAR"

        elif self.state in ("GAMEOVER", "CLEAR"):
            # リトライ
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                # self.create_course()
                self.state = "START"
        return None
        

    def draw(self):
        pyxel.cls(0)
        
        # 迷路
        pyxel.blt(0, 0, 0, 0, 0, pyxel.width, pyxel.height)

        # スタート、ゴール
        sx, sy, sw, sh = self.start_area
        gx, gy, gw, gh = self.goal_area
        pyxel.rect(sx, sy, sw, sh, 14)
        pyxel.rect(gx, gy, gw, gh, 14)


        # 状態毎のメッセージ
        if self.state == "START":
            pyxel.text(50, 30, "STARTSをクリックして開始", 7, self.font12)
            pyxel.rect(gx, gy, gw, gh, 7)
        elif self.state == "GAMEOVER":
            pyxel.text(50, 30, "GAME OVER", 7, self.font12)
        elif self.state == "CLEAR":
            pyxel.text(50, 30, "CLEAR!", 7, self.font12)