import math
import os
import random
import pyxel
from module import GameModule

SCREEN_WIDTH = 440
SCREEN_HEIGHT = 250


class Bullet:
    def __init__(self, x: float, y: float, dx: float, dy: float, color: int, w: int = 3, h: int = 7):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.dx = dx
        self.dy = dy
        self.color = color
        self.is_alive = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if (
            self.x < -self.w
            or self.x > SCREEN_WIDTH
            or self.y < -self.h
            or self.y > SCREEN_HEIGHT
        ):
            self.is_alive = False

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, self.color)


class Boss:
    def __init__(self):
        self.w = 64
        self.h = 64
        self.x = SCREEN_WIDTH // 2 - self.w // 2
        self.base_y = 34
        self.y = self.base_y
        self.hit_radius = 26  # 64x64の円形スプライトに合わせた当たり判定半径

        self.max_hp = 100
        self.hp = self.max_hp
        self.dir = 1
        self.speed = 1.4
        self.hit_flash_timer = 0
        self.attack_cooldown = 60

    @property
    def center_x(self) -> float:
        return self.x + self.w / 2

    @property
    def center_y(self) -> float:
        return self.y + self.h / 2

    @property
    def is_enraged(self) -> bool:
        return self.hp <= self.max_hp // 2

    def update(self):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

        # 怒り状態（HP半分以下）で移動速度アップ
        current_speed = self.speed * (1.5 if self.is_enraged else 1.0)
        self.x += self.dir * current_speed

        # 画面端で折り返し
        if self.x <= 24:
            self.x = 24
            self.dir = 1
        elif self.x + self.w >= SCREEN_WIDTH - 24:
            self.x = SCREEN_WIDTH - 24 - self.w
            self.dir = -1

        # サイン波による上下の浮遊アニメーション
        self.y = self.base_y + math.sin(pyxel.frame_count * 0.06) * 6

    def draw(self, has_image: bool):
        # 被弾時は全色を白(7)に置換してフラッシュ演出
        if self.hit_flash_timer > 0:
            for c in range(1, 16):
                pyxel.pal(c, 7)

        if has_image:
            # 透過色0（黒）で 64x64 のボス画像を描画
            pyxel.blt(self.x, self.y, 0, 0, 0, self.w, self.h, 0)
        else:
            # 万が一画像が見つからない場合の仮描画
            pyxel.circ(self.center_x, self.center_y, 28, 8 if self.is_enraged else 2)
            pyxel.circb(self.center_x, self.center_y, 28, 7)

        pyxel.pal()  # パレット置換をリセット


class Game03(GameModule):
    def __init__(self, app):
        super().__init__()
        self.app = app
        pyxel.mouse(True)

        self._load_assets()
        self._init_sounds()
        self.reset_game()

    def _load_assets(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        boss_img_path = os.path.join(base_dir, "assets", "images", "wotu_circle_64px.png")

        if os.path.exists(boss_img_path):
            pyxel.images[0].load(0, 0, boss_img_path)
            self.has_boss_image = True
        else:
            self.has_boss_image = False

    def _init_sounds(self):
        # 0: 自機ショット, 1: ボス被弾, 2: ボス撃破/ゲームオーバー
        # pyxel.sounds[0].set("c3g2c2", "p", "741", "f", 5)
        # pyxel.sounds[1].set("a2e2c2", "n", "642", "f", 4)
        # pyxel.sounds[2].set("g2f#2f2e2", "t", "7654", "s", 18)
        pass

    def reset_game(self):
        self.state = "INTRODUCTION"  # "INTRODUCTION", "PLAY", "GAMEOVER", "CLEAR"

        # STARTボタンの矩形領域 [x, y, w, h]
        self.start_btn_area = [SCREEN_WIDTH // 2 - 55, 182, 110, 28]

        # 自機ステータス
        self.player_w = 18
        self.player_h = 10
        self.player_x = SCREEN_WIDTH // 2 - self.player_w // 2
        self.player_y = SCREEN_HEIGHT - 22
        self.player_speed = 3.5
        self.shoot_cooldown = 0

        # ボスと弾リスト
        self.boss = Boss()
        self.player_bullets: list[Bullet] = []
        self.enemy_bullets: list[Bullet] = []

    def update(self):
        # if pyxel.btnp(pyxel.KEY_T):
        #     return "Title"

        # 1. イントロダクション画面（タイトル・操作説明・STARTボタン）
        if self.state == "INTRODUCTION":
            is_clicked = self.is_mouse_over_area(self.start_btn_area) and pyxel.btnp(
                pyxel.MOUSE_BUTTON_LEFT
            )
            is_key_start = pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN)

            if is_clicked or is_key_start:
                self.state = "PLAY"
                pyxel.play(0, 0)
            return None

        # 2. ゲームオーバー / クリア画面
        if self.state != "PLAY":
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
            return None

        # 3. プレイ中の更新処理
        self._update_player()
        self._update_boss()
        self._update_bullets()
        self._check_collisions()

        return None

    def _update_player(self):
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.player_x = max(12, self.player_x - self.player_speed)
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.player_x = min(
                SCREEN_WIDTH - self.player_w - 12, self.player_x + self.player_speed
            )

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if (pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_Z)) and self.shoot_cooldown == 0:
            bx = self.player_x + self.player_w // 2 - 1
            by = self.player_y - 7
            self.player_bullets.append(Bullet(bx, by, 0.0, -5.5, 7))
            self.shoot_cooldown = 10
            pyxel.play(0, 0)

    def _update_boss(self):
        self.boss.update()

        self.boss.attack_cooldown -= 1
        if self.boss.attack_cooldown <= 0:
            self._boss_shoot()
            self.boss.attack_cooldown = 32 if self.boss.is_enraged else 50

    def _boss_shoot(self):
        cx = self.boss.center_x
        cy = self.boss.y + self.boss.h - 8

        if random.random() < 0.5:
            # パターンA：3方向拡散弾（扇状）
            for angle_deg in (-22, 0, 22):
                rad = math.radians(angle_deg)
                speed = 3.0
                dx = math.sin(rad) * speed
                dy = math.cos(rad) * speed
                self.enemy_bullets.append(Bullet(cx - 2, cy, dx, dy, 10, w=4, h=6))
        else:
            # パターンB：自機狙い弾
            px = self.player_x + self.player_w // 2
            py = self.player_y + self.player_h // 2
            angle = math.atan2(py - cy, px - cx)
            speed = 3.6 if self.boss.is_enraged else 2.8
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            self.enemy_bullets.append(Bullet(cx - 2, cy, dx, dy, 8, w=4, h=6))

    def _update_bullets(self):
        for b in self.player_bullets:
            b.update()
        for b in self.enemy_bullets:
            b.update()

        self.player_bullets = [b for b in self.player_bullets if b.is_alive]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.is_alive]

    def _is_colliding_rect(self, ax, ay, aw, ah, bx, by, bw, bh) -> bool:
        return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by

    def _is_colliding_circle_rect(self, cx, cy, r, rx, ry, rw, rh) -> bool:
        # 矩形上で円の中心に最も近い点をクランプして距離判定
        closest_x = max(rx, min(cx, rx + rw))
        closest_y = max(ry, min(cy, ry + rh))
        dx = cx - closest_x
        dy = cy - closest_y
        return (dx * dx + dy * dy) <= (r * r)

    def _check_collisions(self):
        # 自機の弾（矩形） vs ボス（円形判定）
        for b in self.player_bullets:
            if not b.is_alive:
                continue
            if self._is_colliding_circle_rect(
                self.boss.center_x,
                self.boss.center_y,
                self.boss.hit_radius,
                b.x,
                b.y,
                b.w,
                b.h,
            ):
                b.is_alive = False
                self.boss.hp = max(0, self.boss.hp - 2)
                self.boss.hit_flash_timer = 3
                pyxel.play(1, 1)

                if self.boss.hp == 0:
                    self.state = "CLEAR"
                    pyxel.play(0, 2)
                    break

        # ボスの弾 vs 自機（中心寄りの小さめ判定）
        for b in self.enemy_bullets:
            if b.is_alive and self._is_colliding_rect(
                b.x,
                b.y,
                b.w,
                b.h,
                self.player_x + 4,
                self.player_y + 3,
                self.player_w - 8,
                self.player_h - 4,
            ):
                self.state = "GAMEOVER"
                pyxel.play(0, 2)
                break

    def draw(self):
        pyxel.cls(0)

        # イントロダクション画面の描画
        if self.state == "INTRODUCTION":
            self._draw_introduction()
            return

        # 上部UI：ボスHPバー
        self._draw_boss_hp_bar()

        # ボスの描画（wotu_circle_64px.png）
        self.boss.draw(self.has_boss_image)

        # 自機の描画
        pyxel.rect(self.player_x, self.player_y + 4, self.player_w, 6, 11)
        pyxel.rect(self.player_x + 7, self.player_y, 4, 4, 11)

        # 弾の描画
        for b in self.player_bullets:
            b.draw()
        for b in self.enemy_bullets:
            b.draw()

        # ゲームオーバー / クリア時のオーバーレイ
        if self.state in ("GAMEOVER", "CLEAR"):
            pyxel.dither(0.5)
            pyxel.rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0)
            pyxel.dither(1.0)

            if self.state == "GAMEOVER":
                pyxel.text(165, 95, "GAME OVER", 8, self.font20)
            else:
                pyxel.text(180, 95, "CLEAR!", 10, self.font20)

            pyxel.text(165, 130, "[R] イントロへ戻る", 7, self.font10)

    def _draw_boss_hp_bar(self):
        pyxel.text(14, 8, "ヲツ", 8 if self.boss.is_enraged else 7, self.font10)

        bar_x = 46
        bar_y = 9
        bar_w = 320
        bar_h = 8

        pyxel.rect(bar_x, bar_y, bar_w, bar_h, 1)
        fill_w = int(bar_w * (self.boss.hp / self.boss.max_hp))
        bar_col = 8 if self.boss.is_enraged else 10
        pyxel.rect(bar_x, bar_y, fill_w, bar_h, bar_col)
        pyxel.rectb(bar_x, bar_y, bar_w, bar_h, 7)

        # pyxel.text(376, 8, "[T]戻る", 6, self.font10)

    def _draw_introduction(self):
        # タイトルロゴ
        pyxel.text(160, 30, "ヲツベーダー", 10, self.font20)
        pyxel.line(90, 56, 350, 56, 5)

        # 操作説明ボックス
        box_x, box_y, box_w, box_h = 95, 70, 250, 96
        pyxel.rect(box_x, box_y, box_w, box_h, 1)
        pyxel.rectb(box_x, box_y, box_w, box_h, 6)

        pyxel.text(box_x + 85, box_y + 10, "【 操作説明 】", 11, self.font10)
        pyxel.text(box_x + 28, box_y + 30, "左右移動 : [A] / [D] または [←] / [→]", 7, self.font10)
        pyxel.text(box_x + 28, box_y + 46, "ショット : [SPACE] または [Z]（長押し可）", 7, self.font10)
        pyxel.text(box_x + 60, box_y + 70, "ボスのHPを0にすればクリア！", 10, self.font10)
        # pyxel.text(box_x + 28, box_y + 78, "中断復帰 : [T] キーでタイトル画面へ", 6, self.font10)

        # STARTボタン描画
        bx, by, bw, bh = self.start_btn_area
        is_hover = self.is_mouse_over_area(self.start_btn_area)

        btn_bg = 10 if is_hover else 3
        btn_text_col = 0 if is_hover else 7
        pyxel.rect(bx, by, bw, bh, btn_bg)
        pyxel.rectb(bx, by, bw, bh, 7)
        pyxel.text(bx + 27, by + 4, "START", btn_text_col, self.font20)