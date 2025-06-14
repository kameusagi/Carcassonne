import tkinter as tk
from map import DynamicMap
from player import Player
from tile import Tile
from gui_config import CELL_COLORS, CELL_SIZE, CELL_SIZE_MIN, CELL_SIZE_MAX

class GUIBoard:
    def __init__(self, root):
        self.root = root
        self.cell_size = CELL_SIZE

        # Canvas とスクロールバーのセットアップ
        self.canvas = tk.Canvas(root, bg="white")
        self.hbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.vbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # マップとプレイヤー
        self.map = DynamicMap()
        self.players = [
            Player("Player1", "grass"),
            Player("Player2", "water")
        ]
        self.turn = 0

        # 初期タイル（grass）を配置して描画
        initial_tile = Tile()
        self.map.place_tile(0, 0, initial_tile)
        # “次に置くタイル” のプレビュー用にランダム生成 or Player 固定
        self.current_preview_tile = Tile()  # None ならランダム。Player 固定なら Tile(player.tile_type)

        self.draw()

        # プレビュー用アイテムID保持リスト
        self._preview_items = []

        # イベントバインド
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<MouseWheel>", self.on_zoom)  # Windows
        self.canvas.bind("<Button-4>", self.on_zoom)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_zoom)    # Linux scroll down
        self.root.bind("<Key-plus>", lambda e: self.adjust_zoom(1))
        self.root.bind("<Key-minus>", lambda e: self.adjust_zoom(-1))

    def draw(self):
        self.canvas.delete("all")
        coords = list(self.map.cells.keys())

        # マップにセルがない場合は (0,0) のみ
        if coords:
            xs, ys = zip(*coords)
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        else:
            min_x = min_y = max_x = max_y = 0

        cs = self.cell_size
        pad = 2  # 余白マージン（セル数）

        # スクロール領域を絶対座標＋余白で設定
        x0 = (min_x - pad) * cs
        y0 = (min_y - pad) * cs
        x1 = (max_x + 1 + pad) * cs
        y1 = (max_y + 1 + pad) * cs
        self.canvas.config(scrollregion=(x0, y0, x1, y1))

        # 各セルを絶対座標で描画
        for (x, y), cell in self.map.cells.items():
            color = CELL_COLORS.get(cell.cell_type, "gray")
            sx = x * cs
            sy = y * cs
            self.canvas.create_rectangle(
                sx, sy, sx + cs, sy + cs,
                fill=color, outline="black"
            )

    def on_click(self, event):
        # クリック位置 → マップ上のセル座標
        x_canv = self.canvas.canvasx(event.x)
        y_canv = self.canvas.canvasy(event.y)

        center_x = int(x_canv // self.cell_size)
        center_y = int(y_canv // self.cell_size)
        gx = center_x - Tile.SIZE // 2
        gy = center_y - Tile.SIZE // 2
        
        print(gx, gy)

        player = self.players[self.turn % 2]
        # 前のタイル配置が成功したら、次のタイルはランダム構成で生成
        tile = self.current_preview_tile
        if self.map.place_tile(gx, gy, tile):
            self.turn += 1
            # 次にプレビューするタイルを更新
            self.current_preview_tile = Tile()
            self.draw()
        else:
            print("配置できません")

    def on_mouse_move(self, event):
        # 既存プレビューを消去
        for item in self._preview_items:
            self.canvas.delete(item)
        self._preview_items.clear()

        # Canvas 座標 → セル座標 (中心オフセット済み)
        x_canv = self.canvas.canvasx(event.x)
        y_canv = self.canvas.canvasy(event.y)
        cs = self.cell_size
        center_x = int(x_canv // cs)
        center_y = int(y_canv // cs)
        origin_x = center_x - Tile.SIZE // 2
        origin_y = center_y - Tile.SIZE // 2

        # プレビュータイルを参照
        tile = self.current_preview_tile
        stipple_pattern = "gray50"

        # タイルのセル構成に合わせて描画
        for dy in range(Tile.SIZE):
            for dx in range(Tile.SIZE):
                cell = tile.get_cell(dx, dy)
                color = CELL_COLORS.get(cell.cell_type, "gray")
                sx = (origin_x + dx) * cs
                sy = (origin_y + dy) * cs
                item = self.canvas.create_rectangle(
                    sx, sy, sx + cs, sy + cs,
                    fill=color, stipple=stipple_pattern, outline=""
                )
                self._preview_items.append(item)


    def on_zoom(self, event):
        delta = 1 if event.delta > 0 else -1
        self.adjust_zoom(delta)

    def adjust_zoom(self, direction):
        new_size = self.cell_size + direction * 5
        if CELL_SIZE_MIN <= new_size <= CELL_SIZE_MAX:
            self.cell_size = new_size
            self.draw()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("タイル配置ゲーム")
    app = GUIBoard(root)
    root.mainloop()
