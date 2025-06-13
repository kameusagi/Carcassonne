import tkinter as tk
from map import DynamicMap
from player import Player
from tile import Tile
from gui_config import CELL_COLORS, CELL_SIZE, CELL_SIZE_MIN, CELL_SIZE_MAX

class GUIBoard:
    def __init__(self, root):
        self.root = root
        self.cell_size = CELL_SIZE

        self.canvas = tk.Canvas(root, bg="white", scrollregion=(0, 0, 3000, 3000))
        self.hbar = tk.Scrollbar(root, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.hbar.config(command=self.canvas.xview)

        self.vbar = tk.Scrollbar(root, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar.config(command=self.canvas.yview)

        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.map = DynamicMap()
        # 初期配置タイル（すでに"grass"が置かれている状態）
        self.turn = 0
        initial_tile = Tile("grass")
        self.map.place_tile(0, 0, initial_tile)
        # 初期状態を描画
        self.draw()

        self.players = [
            Player("Player1", "grass"),
            Player("Player2", "water")
        ]

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<MouseWheel>", self.on_zoom)  # Windows
        self.canvas.bind("<Button-4>", self.on_zoom)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_zoom)    # Linux scroll down
        self.root.bind("<Key-plus>", lambda e: self.adjust_zoom(1))
        self.root.bind("<Key-minus>", lambda e: self.adjust_zoom(-1))

    def draw(self):
        self.canvas.delete("all")
        coords = list(self.map.cells.keys())
        # (1) マップにセルが一つもないときは原点(0,0)を扱う
        if coords:
            xs, ys = zip(*coords)
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        else:
            min_x = min_y = max_x = max_y = 0

        cs = self.cell_size
        pad = 6  # 左右上下にセル2マス分の余白

        # (2) scrollregion を「絶対座標＋マージン」で設定
        x0 = (min_x - pad) * cs
        y0 = (min_y - pad) * cs
        x1 = (max_x + 1 + pad) * cs
        y1 = (max_y + 1 + pad) * cs
        self.canvas.config(scrollregion=(x0, y0, x1, y1))

        # (3) 各セルを「絶対座標 x*cs, y*cs」で描画
        for (x, y), cell in self.map.cells.items():
            color = CELL_COLORS.get(cell.cell_type, "gray")
            sx = x * cs
            sy = y * cs
            # セル罫線
            self.canvas.create_rectangle(
                sx, sy, sx + cs, sy + cs,
                fill=color, outline="black"
            )


    def on_click(self, event):
        cs = self.cell_size
        # Canvas の座標をそのままセルサイズで割る
        x_canv = self.canvas.canvasx(event.x)
        y_canv = self.canvas.canvasy(event.y)
        gx = int(x_canv // self.cell_size)
        gy = int(y_canv // self.cell_size)
        print(gx, gy)

        player = self.players[self.turn % 2]
        tile = Tile(player.tile_type)
        if self.map.place_tile(gx, gy, tile):
            self.turn += 1
            self.draw()
        else:
            print("配置できません")

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
