import pyxel


class Card:

  def __init__(self, start_x, start_y, target_x, target_y, delay, color):
    self.start_x = start_x
    self.start_y = start_y
    self.target_x = target_x
    self.target_y = target_y
    self.x = start_x
    self.y = start_y

    self.delay = delay  # 動き出すまでの待ちフレーム数
    self.duration = 20  # 移動にかかるフレーム数（約0.66秒）
    self.timer = 0
    self.color = color
    self.is_dealt = False

  def update(self):
    if self.is_dealt:
      return

    self.timer += 1
    # ディレイ期間中は何もしない
    if self.timer <= self.delay:
      return

    # 進行度 t を 0.0 〜 1.0 の範囲で計算
    elapsed = self.timer - self.delay
    t = min(elapsed / self.duration, 1.0)

    # Ease-Out Cubic（最初は速く、目標に近づくとゆっくり止まる）
    ease_t = 1 - (1 - t) ** 3

    # 現在座標の計算（線形補間）
    self.x = self.start_x + (self.target_x - self.start_x) * ease_t
    self.y = self.start_y + (self.target_y - self.start_y) * ease_t

    if t >= 1.0:
      self.is_dealt = True

  def draw(self):
    # カード本体と枠線を描画（幅16x高さ22）
    pyxel.rect(self.x, self.y, 16, 22, self.color)
    pyxel.rectb(self.x, self.y, 16, 22, 7)


class App:

  def __init__(self):
    pyxel.init(160, 120, title="Card Deal Animation")
    self.deck_x = 16
    self.deck_y = 16
    self.cards = []
    self.deal_cards()
    pyxel.run(self.update, self.draw)

  def deal_cards(self):
    self.cards.clear()
    num_cards = 5
    colors = [8, 9, 10, 11, 12]  # カードごとの色

    for i in range(num_cards):
      # 手札の目標位置（横並びに配置）
      target_x = 24 + i * 24
      target_y = 85
      # 1枚につき6フレームずつずらして発射
      delay = i * 6
      card = Card(
          self.deck_x, self.deck_y, target_x, target_y, delay, colors[i]
      )
      self.cards.append(card)

  def update(self):
    # スペースキーまたはZキーで配り直し
    if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
      self.deal_cards()

    for card in self.cards:
      card.update()

  def draw(self):
    pyxel.cls(1)

    # 山札の描画（少しずらして重ねることで厚み表現）
    for i in range(3):
      pyxel.rect(self.deck_x - i, self.deck_y - i, 16, 22, 5)
      pyxel.rectb(self.deck_x - i, self.deck_y - i, 16, 22, 7)

    # 手札（アニメーション中のカード）の描画
    # ※リストの後ろ（後から配られるカード）が上に重なるように描画
    for card in self.cards:
      card.draw()

    pyxel.text(45, 10, "PRESS SPACE TO DEAL", 7)


App()