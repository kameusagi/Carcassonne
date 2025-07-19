import tkinter as tk
import tkinter.messagebox
import networkx as nx
from collections import defaultdict, Counter
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Canvas
from PIL import Image, ImageTk

from map import DynamicMap
from player import Player
from tile import Tile
from TileFactory import TileFactory
from gui_config import CELL_COLORS, CELL_SIZE, CELL_SIZE_MIN, CELL_SIZE_MAX

class GUIBoard:
    def __init__(self, root):
        self.root = root
        self.cell_size = CELL_SIZE
        self.tile_size = CELL_SIZE*Tile.SIZE
        self.meaple_size = self.cell_size*0.6 #0.6倍

        # Canvas とスクロールバーのセットアップ
        self.canvas = tk.Canvas(root, bg="white")
        self.hbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.vbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.config(xscrollincrement=1)
        self.canvas.config(yscrollincrement=1)

        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.drag_start_x = None
        self.drag_start_y = None

        self.cell_images_put = []  # クラス内で画像保持用
        self.images_move_tile = []  # クラス内で画像保持用
        self.images_move_meaple = []  # クラス内で画像保持用

        # マップとプレイヤー
        self.map = DynamicMap()
        self.players = [
            Player("RED"),
            Player("BLUE"),
        ]
        self.turn = 0
        self.current_player = self.players[self.turn % len(self.players)]

        # フェーズ: 'tile' または 'meaple'
        self.phase = 'tile'
        
        ctrl_frame = tk.Frame(root)
        ctrl_frame.pack(side=tk.TOP, fill=tk.X)

        self.player_label = tk.Label(
            ctrl_frame,
            text=f"Turn: {self.current_player.name}",
            font=("Arial", 14, "bold")
        )
        self.player_label.pack(side=tk.TOP, padx=5, pady=5)

        self.phase_label = tk.Label(
            ctrl_frame,
            text=f"フェーズ: {self.phase}",
            font=("Arial", 14, "bold")
        )
        self.phase_label.pack(side=tk.TOP, padx=5, pady=5)

        end_turn_btn = tk.Button(
            ctrl_frame,
            text="ターン終了",
            command=self.end_turn
        )
        end_turn_btn.pack(side=tk.TOP, padx=5, pady=5)

        discard_btn = tk.Button(
            ctrl_frame,
            text="タイルを捨てる",
            command=self.discard_tile
        )
        discard_btn.pack(side=tk.TOP, padx=5, pady=5)

        self.score = tk.Label(
            ctrl_frame,
            text=f"{self.players[0].name} のスコア: {self.players[0].get_score()}  |  {self.players[1].name} のスコア: {self.players[1].get_score()}",
            font=("Arial", 14, "bold")
        )
        self.score.pack(side=tk.TOP, padx=5, pady=5)

        self.sub_score = tk.Label(
            ctrl_frame,
            text=f"{self.players[0].name} のサブスコア: {self.players[0].get_subscore()}  |  {self.players[1].name} のサブスコア: {self.players[1].get_subscore()}",
            font=("Arial", 14, "bold")
        )
        self.sub_score.pack(side=tk.TOP, padx=5, pady=5)

        self.meaples = tk.Label(
            ctrl_frame,
            text=f"{self.players[0].name} のミープル: {self.players[0].get_stock_meaple()}  |  {self.players[1].name} のミープル: {self.players[1].get_stock_meaple()}",
            font=("Arial", 14, "bold")
        )
        self.meaples.pack(side=tk.TOP, padx=5, pady=5)

        dubug_btn = tk.Button(
            ctrl_frame,
            text="デバッグ用",
            command=self.debug2
        )
        dubug_btn.pack(side=tk.TOP, padx=5, pady=5)

        # TileFactory を初期化（CSV フォルダを指定）
        self.factory = TileFactory()
        # 初期タイルを配置して描画
        initial_tile = self.factory.next_tile(init=True)
        self.map.place_tile(Tile.SIZE*3, Tile.SIZE*3, initial_tile, init=True)
        
        # “次に置くタイル” のプレビュー用生成
        self.current_preview_tile = self.factory.next_tile()
        
        self.draw()

        # プレビュー用アイテムID保持リスト
        self._preview_items = []

        # イベントバインド
        self.canvas.bind("<Button-1>", self.on_left_click) # 左クリックでタイル配置
        self.canvas.bind("<Button-3>", self.on_right_click) # 右クリックでタイル回転
        self.canvas.bind("<Motion>", self.on_mouse_move) # マウス移動でプレビュー更新
        self.canvas.bind("<MouseWheel>", self.on_zoom)  # Windows
        self.canvas.bind("<Button-4>", self.on_zoom)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_zoom)    # Linux scroll down
        # self.root.bind("<Key-plus>", lambda e: self.adjust_zoom(1))
        # self.root.bind("<Key-minus>", lambda e: self.adjust_zoom(-1))
        #ドラッグ＆ドロップ
        self.canvas.bind("<B1-Motion>", self.map_move) # ドラッグ中のマップ移動


    def draw(self):
        self.canvas.delete("all")
        cs = self.cell_size
        self.meaple_size = self.cell_size*0.6 

        # 各セルを絶対座標で描画
        for (x, y), cell in self.map.cells.items():
            png_path = cell.png_path
            sx = x * cs
            sy = y * cs
            rotate_count = cell.rotate_count
            # 画像を読み込み
            tile_img = Image.open(png_path)
            # 90度 × rotate_count回転
            rotated_img = tile_img.rotate(90 * rotate_count, expand=True)
            # リサイズ（セルサイズに合わせる）
            resized_img = rotated_img.resize((cs, cs), Image.Resampling.LANCZOS)
            tile_photo = ImageTk.PhotoImage(resized_img)
            self.cell_images_put.append(tile_photo)  # 保持しておく
            self.canvas.create_image(sx, sy, image=tile_photo, anchor="nw")  # 左上基準

        # 各ミープルを絶対座標で描画
        for (x, y), player in self.map.meaples.items():
            cx = (x +0.5)*cs 
            cy = (y +0.5)*cs
            r = int(self.meaple_size)
            # 画像を読み込み
            meaple_img = Image.open(player.meaple_path)
            # リサイズ（セルサイズに合わせる）
            resized_img = meaple_img.resize((r, r), Image.Resampling.LANCZOS)
            meaple_photo = ImageTk.PhotoImage(resized_img)
            self.cell_images_put.append(meaple_photo)  # 保持しておく
            self.canvas.create_image(cx, cy, image=meaple_photo, anchor="center")  # 中央基準

    def on_left_click(self, event):
        if self.phase == 'tile':
            self.before_meaples = {}
            plased = self.handle_tile_click(event)
        elif self.phase == 'meaple':
            plased = self.handle_meaple_click(event)
        
        if plased:
            # ターン終了時にスコア計算
            self.score_calculation()
            # ミープルを収集
            self.map.collect_meaples()

            if self.current_player == self.players[0] and self.phase == 'tile':
                print("-----------------------------------------------------")
        
        self.draw()
        self.score.config(text=f"{self.players[0].name} のスコア: {self.players[0].get_score()}  |  {self.players[1].name} のスコア: {self.players[1].get_score()}")
        self.sub_score.config(text=f"{self.players[0].name} のサブスコア: {self.players[0].get_subscore()}  |  {self.players[1].name} のサブスコア: {self.players[1].get_subscore()}")
        self.meaples.config(text=f"{self.players[0].name} のミープル: {self.players[0].get_stock_meaple()}  |  {self.players[1].name} のミープル: {self.players[1].get_stock_meaple()}")

        # 今のマウスの位置を保持
        self.drag_start_x = event.x
        self.drag_start_y = event.y


    def on_right_click(self, event):
        """
        プレビュー中のタイルを右回転させて再描画。
        """
        # 1) 回転
        self.current_preview_tile.rotate()

        # 2) 現在のマウス位置で再プレビュー
        self.on_mouse_move(event)

    def on_mouse_move(self, event):
        # 既存プレビューを消去
        for item in self._preview_items:
            self.canvas.delete(item)
        self._preview_items.clear()

        cs = self.cell_size

        if self.phase == 'tile':
            origin_x, origin_y = self.tile_origin_coords(event.x, event.y)
            tile = self.current_preview_tile

            if len(self.images_move_tile) == Tile.SIZE * Tile.SIZE:
                self.images_move_tile = []  # 画像をクリア

            for dy in range(Tile.SIZE):
                for dx in range(Tile.SIZE):
                    cell = tile.get_cell(dx, dy)
                    png_path = cell.png_path
                    sx = (origin_x + dx) * cs
                    sy = (origin_y + dy) * cs
                    rotate_count = cell.rotate_count
                    tile_img = Image.open(png_path).convert("RGBA")
                    rotated_img = tile_img.rotate(90 * rotate_count, expand=True) # 90度 × rotate_count回転
                    resized_img = rotated_img.resize((cs, cs), Image.Resampling.LANCZOS)

                    # αチャンネルを調整して透明度を変更（例: 128 = 50%）
                    alpha = 128
                    r, g, b, a = resized_img.split()
                    a = a.point(lambda p: alpha)  # 全ピクセルのαを128に
                    transparent_img = Image.merge("RGBA", (r, g, b, a))

                    # Tkinter用に変換（PhotoImage）
                    tile_photo = ImageTk.PhotoImage(transparent_img)
                    self.images_move_tile.append(tile_photo)  # 保持しておく
                    self.canvas.create_image(sx, sy, image=tile_photo, anchor="nw")  # 左上基準
            
        elif self.phase == 'meaple':
            if len(self.images_move_meaple) > 0:
                self.images_move_meaple = []  # 画像をクリア
            x_canv = self.canvas.canvasx(event.x)
            y_canv = self.canvas.canvasy(event.y)
            cell_x = int(x_canv // cs)
            cell_y = int(y_canv // cs)
            cx = (cell_x +0.5)*cs 
            cy = (cell_y +0.5)*cs
            r = int(self.meaple_size)
            meaple_img = Image.open(self.current_player.meaple_path).convert("RGBA")
            resized_img = meaple_img.resize((r, r), Image.Resampling.LANCZOS)

            # αチャンネルを調整して透明度を変更（例: 128 = 50%）
            alpha = 128
            r, g, b, a = resized_img.split()
            a = a.point(lambda p: alpha)  # 全ピクセルのαを128に
            transparent_img = Image.merge("RGBA", (r, g, b, a))

            # Tkinter用に変換（PhotoImage）
            meaple_photo = ImageTk.PhotoImage(transparent_img)
            self.images_move_meaple.append(meaple_photo)  # 保持しておく
            self.canvas.create_image(cx, cy, image=meaple_photo, anchor="center")  # 中央基準
        
        # 今のマウスの位置を保持
        self.drag_start_x = event.x
        self.drag_start_y = event.y
                   
    def on_zoom(self, event):
        delta = 1 if event.delta > 0 else -1
        self.adjust_zoom(delta)

    def adjust_zoom(self, direction):
        new_size = self.cell_size + direction * 5
        if CELL_SIZE_MIN <= new_size <= CELL_SIZE_MAX:
            self.cell_size = new_size
            self.tile_size = self.cell_size*Tile.SIZE
            self.draw()

    def map_move(self, event):
        """
        マップをドラッグで移動する機能。
        マウスの動きに合わせてキャンバスをスクロールします。
        """
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        self.canvas.xview_scroll(-dx, "units")
        self.canvas.yview_scroll(-dy, "units")
        self.draw()

        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def discard_tile(self):
        """
        現在のプレビュータイルを捨てて、新しく factory から取得し直す
        """
        if self.phase != 'tile':
            print("タイルを捨てるのは、タイル配置フェーズのときだけです")
            return
        try:
            if not self.is_tile_anywhere_placeable(): #タイルを置ける選択肢がない場合は、タイルを捨てる　Todo
                self.current_preview_tile = self.factory.next_tile()
                print(f"{self.current_player.name} がタイルを捨て、新しいタイルを取得しました。")
            else:
                pass

        except RuntimeError:
            # もうタイルが残っていない場合は終了
            tk.messagebox.showinfo("終了", "タイルが残っていないのでゲームを終了します。")
            self.root.destroy()
            return

        # プレビュー表示を更新
        self.draw()

    def end_turn(self):
        """
        ミープルを置きたくないときの処理
        """
        if self.phase == 'meaple':
            self.turn += 1 # ターンを進める
            self.current_player = self.players[self.turn % len(self.players)]
            self.player_label.config(text=f"Turn: {self.current_player.name}")
            self.phase = 'tile'
            self.phase_label.config(text=f"フェーズ: {self.phase}")
            # プレビュー表示を更新
            self.draw()
        else:
            print("ミープル配置フェーズでのみ、ターン終了が可能です")
            pass

    def tile_origin_coords(self, x, y):
        """
        タイルの原点座標を計算するヘルパー関数。
        (x, y) はタイルの左上セルの座標。
        """
        x_canv = self.canvas.canvasx(x)
        y_canv = self.canvas.canvasy(y)
        cs = self.cell_size

        block_x = int(x_canv // (cs * Tile.SIZE))
        block_y = int(y_canv // (cs * Tile.SIZE))
        origin_x = block_x * Tile.SIZE
        origin_y = block_y * Tile.SIZE

        return (origin_x, origin_y)

    def handle_tile_click(self, event):
        origin_x, origin_y = self.tile_origin_coords(event.x, event.y)

        tile = self.current_preview_tile
        placed = self.map.place_tile(origin_x, origin_y, tile)
        
        if placed:
            self.current_preview_tile = self.factory.next_tile()
            print(f"{self.current_player.name}がタイルを配置")
            # 次はミープル配置フェーズに移行
            self.phase = 'meaple'
            self.phase_label.config(text=f"フェーズ: {self.phase}")

            print(f"--- {self.current_player.name} のミープル配置フェーズ ---")
        else:
            print("タイル配置できません")
        
        # セルのpatch_idsを更新
        self.map.update_cell_area()
        self.map.update_tile_area()


        return placed

    def handle_meaple_click(self, event):
        # マップ上の origin_x,origin_y はタイル配置時と同様計算
        x_canv = self.canvas.canvasx(event.x)
        y_canv = self.canvas.canvasy(event.y)
        cs = self.cell_size
        cell_x = int(x_canv // cs)
        cell_y = int(y_canv // cs)

        # ここでミープル配置処理を行う（例：self.map.place_meaple(...)）
        placed = self.map.place_meaple(cell_x, cell_y, self.current_player)
        if placed:
            self.turn += 1 # ターンを進める
            self.current_player = self.players[self.turn % len(self.players)]
            self.player_label.config(text=f"Turn: {self.current_player.name}")
            self.phase = 'tile'
            self.phase_label.config(text=f"フェーズ: {self.phase}")

        else:
            print("ミープル配置できません")

        return placed


    def score_calculation(self):
        """
        スコア計算のロジックをここに実装
        """
        for player in self.players:
            player.score_sub = 0  # サブスコアをリセット
        
        work = []

        for (x, y), player in self.map.meaples.items():
            cell = self.map.cells[(x, y)]
            cell_type = cell.cell_type
            patch_id = cell.patch_ids
            is_closed = cell.is_closed
            work.append((x, y, player.name, cell_type, patch_id, is_closed))

        # 1. グルーピング：同じ (cell_type, patch_id) ごとに要素を集める
        group_map = defaultdict(list)
        for entry in work:
            key = (entry[3], entry[4])  # (cell_type, patch_id)
            group_map[key].append(entry)

        # 2. 各グループ内で player.name をカウントし、残すべき player を決定
        result = []
        for entries in group_map.values():
            if len(entries) == 1:
                # 重複なしならそのまま残す
                result.append(entries[0])
            else:
                name_counts = Counter(e[2] for e in entries)  # player.name のカウント
                max_count = max(name_counts.values())
                top_players = [name for name, cnt in name_counts.items() if cnt == max_count]

                if len(top_players) == 1:
                    # 最多1人なら、その人のエントリだけ残す
                    winner = top_players[0]
                    result.extend([e for e in entries if e[2] == winner])
                else:
                    # 複数人が同率 → 全削除
                    pass

        for cell_info in result:
            cell_x, cell_y, player_name, cell_type, patch_id, is_closed = cell_info
            
            if cell_type == "町":
                unique_town = []
                for cell in self.map.cells.values():
                    if (cell.patch_ids == patch_id) and (cell.cell_type == cell_type):
                        unique_town.append([cell.tile_id,cell.mark]) #Todo.　0には、タイルスターの情報を入れる
                unique_town = set(tuple(x) for x in unique_town)
                for player in self.players:
                    if player.name == player_name:
                        if is_closed:
                            player.score += (len(unique_town) + sum(tile[1] for tile in unique_town))*2
                        else:
                            player.score_sub += (len(unique_town) + sum(tile[1] for tile in unique_town))*1

            elif cell_type == "道":
                unique_load = []
                for cell in self.map.cells.values():
                    if (cell.patch_ids == patch_id) and (cell.cell_type == cell_type):
                        unique_load.append(cell.tile_id) 
                unique_load = set(unique_load)
                for player in self.players:
                    if player.name == player_name:
                        if is_closed:
                            player.score += len(unique_load)
                        else:
                            player.score_sub += len(unique_load)

            elif cell_type == "草むら":
                unique_grass = []
                for cell in self.map.cells.values():
                    if (cell.patch_ids == patch_id) and (cell.cell_type == cell_type):
                        unique_grass.append([cell.tile_id,0]) 
                unique_grass = set(tuple(x) for x in unique_grass)
                for player in self.players:
                    if player.name == player_name:
                        # 草むらの得点計算
                        # patch_idが同じ草むらの中で、完成した街が面している個数をカウントする機能
                        player.score_sub += self.facing_town(patch_id)

            elif cell_type == "教会":
                for player in self.players:
                    if player.name == player_name:
                        tile_id = self.map.cells[(cell_x, cell_y)].tile_id
                        for tile in self.map.tiles.values():
                            if tile.tile_id == tile_id:
                                tile_coord = [key for key, value in self.map.tiles.items() if value is tile][0]
                                tile_coord_x, tile_coord_y = tile_coord
                                break
                        directions = [
                            (dx * Tile.SIZE + tile_coord_x, dy * Tile.SIZE + tile_coord_y)
                            for dx in (-1, 0, 1)
                            for dy in (-1, 0, 1)
                        ]
                        if tile.is_closed:
                            player.score += 9
                        else:
                            player.score_sub += sum(1 for key in directions if key in self.map.tiles)
        # スコアを表示
        for player in self.players:
            print(f"{player.name} のスコア: {player.score},\
                  サブスコア: {player.score_sub}, メープルストック: {player.stock_meaple}")

    def facing_town(self, patch_id):
        # patch_idが同じ草むらの中で、完成した街が面している個数をカウントする機能
        
        G = nx.Graph()
        for (x,y), cell in self.map.cells.items():
            if cell.cell_type == "草むら" and cell.patch_ids == patch_id:
                G.add_node((x, y),cell=cell)
        # 草むらの輪郭のセルの座標を取得
        contour_cells = []
        for x, y in list(G.nodes):
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                neighbor = (x + dx, y + dy)
                if (neighbor in self.map.cells.keys()) and neighbor not in G.nodes:  #隣接セルが草むらでない場合
                    # 輪郭セルを追加
                    contour_cells.append((x, y))
                    break
        # 輪郭セルの周囲にある街のセルを取得
        town_patch_ids = set()
        for x, y in contour_cells:
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                neighbor = (x + dx, y + dy)
                if neighbor in self.map.cells.keys():
                    if (neighbor not in G.nodes) and \
                        (self.map.cells[neighbor].cell_type == "町") and \
                         (self.map.cells[neighbor].is_closed == True):
                        town_patch_ids.add(self.map.cells[neighbor].patch_ids)
                        
        score = len(town_patch_ids) * 3  # 街の数に応じてスコアを加算
        return score

    def debug(self):
        """
        デバッグ用（マップのセル情報を取得できるか確認
        """
        debug_cells = {}
        self.map.update_cell_area()
        self.map.update_tile_area()
        
        for (x,y), cell in self.map.cells.items():
            debug_cells[(x,y)] = {cell.cell_type : (cell.patch_ids,cell.is_closed)}

        # 2) グリッドサイズ取得
        xs = [x for x, y in self.map.cells.keys()]
        ys = [y for x, y in self.map.cells.keys()]

        max_x, max_y = max(xs), max(ys)
        min_x, min_y = min(xs), min(ys)

        # 3) 草むらの ID だけを取り出したマトリクスを作成 (非草むらは NaN)
        grid = np.full((max_y - min_y +1, max_x - min_x +1), np.nan)
        tmp = 5
        type_dict = {
            "道"    : 1*tmp,
            "町"    : 2*tmp,
            "草むら": 3*tmp,
            "教会"  : 4*tmp,
            "境界"  : 5*tmp,
            "交差点": 6*tmp,
            "予備"  : 7*tmp,
        }

        for (x, y), cell in self.map.cells.items():
            grid[y-min_y, x-min_x] = cell.is_closed  

        
        print(grid)
        # 4) 可視化
        plt.figure()
        plt.imshow(grid, interpolation='none')
        plt.xlabel('x 座標')
        plt.ylabel('y 座標')
        plt.colorbar(label='パッチID')
        plt.grid()
        plt.show()

    def is_tile_anywhere_placeable(self):
        tile_points = list(self.map.tiles.keys())
        
        neighbors = set()

        # 周辺座標のオフセット（8方向）
        offsets = [
            (dx * Tile.SIZE, dy * Tile.SIZE)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if not ((dx == 0 and dy == 0) or # 自分自身を除外
                    (dx != 0 and dy != 0)  # 対角線方向を除外
                    )  
        ]
        for x, y in tile_points:
            for dx, dy in offsets:
                neighbor = (x + dx, y + dy)
                if neighbor not in self.map.cells.keys():
                    neighbors.add(neighbor)
        
        for neighbor in neighbors:
            if self.map.is_adjacent_compatible(neighbor[0], neighbor[1], self.current_preview_tile):
                print("タイルを置ける場所があります")
                return True
        print("タイルを置ける場所がありません")
        return False
    
    def debug2(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    root.title("タイル配置ゲーム")
    root.state('zoomed')
    app = GUIBoard(root)
    root.mainloop()
