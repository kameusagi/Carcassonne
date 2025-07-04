import tkinter as tk
import tkinter.messagebox

from map import DynamicMap
from player import Player
from tile import Tile
from TileFactory import TileFactory
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
            Player("Player1"),
            Player("Player2")
        ]
        self.turn = 0
        self.current_player = self.players[self.turn % len(self.players)]

        ctrl_frame = tk.Frame(root)
        ctrl_frame.pack(side=tk.TOP, fill=tk.X)

        self.player_label = tk.Label(
            ctrl_frame,
            text=f"Turn: {self.current_player.name}",
            font=("Arial", 14, "bold")
        )
        self.player_label.pack(side=tk.TOP, padx=5, pady=5)

        discard_btn = tk.Button(
            ctrl_frame,
            text="タイルを捨てる",
            command=self.discard_tile
        )
        discard_btn.pack(side=tk.TOP, padx=5, pady=5)

        put_meaple_btn = tk.Button(
            ctrl_frame,
            text="ミープルを置く",
            command=self.discard_tile
        )
        put_meaple_btn.pack(side=tk.TOP, padx=5, pady=5)

        turn_fin_btn = tk.Button(
            ctrl_frame,
            text="ターン終了",
            command=self.put_meaple
        )
        turn_fin_btn.pack(side=tk.TOP, padx=5, pady=5)


        # TileFactory を初期化（CSV フォルダを指定）
        self.factory = TileFactory("./タイル")
        # 初期タイルを配置して描画
        initial_tile = self.factory.next_tile(init=True)
        self.map.place_tile(0, 0, initial_tile, init=True)
        
        # “次に置くタイル” のプレビュー用生成
        self.current_preview_tile = self.factory.next_tile()

        self.draw()

        # プレビュー用アイテムID保持リスト
        self._preview_items = []

        # イベントバインド
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
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
        pad = 10  # 余白マージン（セル数）

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

    def on_left_click(self, event):
        # クリック位置 → マップ上のセル座標
        x_canv = self.canvas.canvasx(event.x)
        y_canv = self.canvas.canvasy(event.y)
        cs = self.cell_size

        block_x = int(x_canv // (cs * Tile.SIZE))
        block_y = int(y_canv // (cs * Tile.SIZE))
        origin_x = block_x * Tile.SIZE
        origin_y = block_y * Tile.SIZE

        tile = self.current_preview_tile
        if self.map.place_tile(origin_x, origin_y, tile):
            print(f"{self.current_player.name}が置いた") 
            self.turn += 1
            # 次は factory から新しいタイルを取り出す（もう重複なし）
            try:
                self.current_preview_tile = self.factory.next_tile()
                self.current_player = self.players[self.turn % len(self.players)]
                self.player_label.config(text=f"Turn: {self.current_player.name}")

            except RuntimeError:
                tk.messagebox.showinfo("終了", "タイルがなくなったのでゲームを終了します。")
                self.root.destroy()  # ウィンドウを閉じてプログラム終了
                return
            
            self.draw()
        else:
            print("配置できません")

    def on_right_click(self, event):
        """
        プレビュー中のタイルを右回転させて再描画。
        マウス移動イベントが発生していない場合でも、プレビューを更新します。
        """
        # 1) 回転
        self.current_preview_tile.rotate()

        # 2) 既存プレビューを消去
        for item in self._preview_items:
            self.canvas.delete(item)
        self._preview_items.clear()

        # 3) 現在のマウス位置で再プレビュー
        #    event.x, event.y を使って on_mouse_move を呼び出し
        self.on_mouse_move(event)

    def on_mouse_move(self, event):
        # 既存プレビューを消去
        for item in self._preview_items:
            self.canvas.delete(item)
        self._preview_items.clear()

        # Canvas 座標 → セル座標 (中心オフセット済み)
        x_canv = self.canvas.canvasx(event.x)
        y_canv = self.canvas.canvasy(event.y)
        cs = self.cell_size
        # マウスのキャンバス座標を「タイル1枚(=SIZEセル)」ごとに切り捨て
        block_x = int(x_canv // (cs * Tile.SIZE))
        block_y = int(y_canv // (cs * Tile.SIZE))

        # そのブロックの左上セルをタイル原点に
        origin_x = block_x * Tile.SIZE
        origin_y = block_y * Tile.SIZE

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

    def discard_tile(self):
        """
        現在のプレビュータイルを捨てて、新しく factory から取得し直す
        """
        try:
            self.current_preview_tile = self.factory.next_tile()
            print(f"{self.current_player.name} がタイルを捨て、新しいタイルを取得しました。")
        except RuntimeError:
            # もうタイルが残っていない場合は終了
            tk.messagebox.showinfo("終了", "タイルが残っていないのでゲームを終了します。")
            self.root.destroy()
            return

        # プレビュー表示を更新
        self.draw()

    def put_meaple(self):
        """
        ミープルを置く
        """
        try:
            self.current_preview_tile = self.factory.next_tile()
            print(f"{self.current_player.name} がタイルを捨て、新しいタイルを取得しました。")
        except RuntimeError:
            # もうタイルが残っていない場合は終了
            tk.messagebox.showinfo("終了", "タイルが残っていないのでゲームを終了します。")
            self.root.destroy()
            return

        # プレビュー表示を更新
        self.draw()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("タイル配置ゲーム")
    root.state('zoomed')
    app = GUIBoard(root)
    root.mainloop()
