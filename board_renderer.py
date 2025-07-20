# view/board_renderer.py
import tkinter as tk
from PIL import Image, ImageTk
from tile import Tile
from map import DynamicMap

class BoardRenderer:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.images_move_tile = []  # プレビュー用のタイル画像
        self.images_move_meaple = []
        self.images_put = []  # 配置済みタイルの画像
        self._preview_items = []

    def clear(self):
        self.canvas.delete("all")
        self.images_put.clear()

    def render(self, dynamic_map):
        """DynamicMap の状態を Canvas に描画"""
        cs = dynamic_map.cell_size
        self.clear()

        # セル描画
        for (x, y), cell in dynamic_map.cells.items():
            img = Image.open(cell.png_path).convert("RGBA")
            img = img.rotate(90 * cell.rotate_count, expand=True)
            img = img.resize((cs, cs), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.images_put.append(photo)
            self.canvas.create_image(x*cs, y*cs, image=photo, anchor="nw")

        # ミープル描画
        for (x, y), player in dynamic_map.meaples.items():
            img = Image.open(player.meaple_path).convert("RGBA")
            size = int(cs * 0.6) # ミープルのサイズをセルの60%に設定
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.images_put.append(photo)
            self.canvas.create_image(
                (x+0.5)*cs, (y+0.5)*cs,
                image=photo, anchor="center"
            )
    def render_preview(self, object, x0, y0, cell_size, phase, player_color):
        """プレビュータイルを Canvas に描画"""
        # 既存プレビューを消去
        for item in self._preview_items:
            self.canvas.delete(item)
        self._preview_items.clear()

        cs = cell_size

        if phase == 'tile':
            tile = object
            if len(self.images_move_tile) == (Tile.SIZE * Tile.SIZE):
                self.images_move_tile = []  # 画像をクリア
            for dy in range(Tile.SIZE):
                for dx in range(Tile.SIZE):
                    cell = tile.get_cell(dx, dy)
                    png_path = cell.png_path
                    sx = (x0 + dx) * cs
                    sy = (y0 + dy) * cs
                    rotate_count = cell.rotate_count
                    tile_img = Image.open(png_path).convert("RGBA")
                    rotated_img = tile_img.rotate(90 * rotate_count, expand=True) # 90度 × rotate_count回転
                    resized_img = rotated_img.resize((cs, cs), Image.Resampling.LANCZOS)

                    # αチャンネルを調整して透明度を変更可能
                    alpha = 256
                    r, g, b, a = resized_img.split()
                    a = a.point(lambda p: alpha)  # 全ピクセルのαを256に
                    transparent_img = Image.merge("RGBA", (r, g, b, a))

                    # Tkinter用に変換（PhotoImage）
                    tile_photo = ImageTk.PhotoImage(transparent_img)
                    self.images_move_tile.append(tile_photo)  # 保持しておく
                    self.canvas.create_image(sx, sy, image=tile_photo, anchor="nw")  # 左上基準

            #　タイルの境界線を描画
            sx = x0 * cs
            sy = y0 * cs
            item = self.canvas.create_rectangle(
                sx, sy, sx + cs * Tile.SIZE, sy + cs * Tile.SIZE,
                outline=player_color, width=2
            )
            self._preview_items.append(item)

        elif phase == 'meaple':
            if len(self.images_move_meaple) > 0:
                self.images_move_meaple = []  # 画像をクリア
            player = object
            cx = (x0 +0.5)*cs
            cy = (y0 +0.5)*cs
            size = int(cs * 0.6)
            # r = int(self.meaple_size)
            meaple_img = Image.open(player.meaple_path).convert("RGBA")
            resized_img = meaple_img.resize((size, size), Image.Resampling.LANCZOS)

            # αチャンネルを調整して透明度を変更（例: 128 = 50%）
            alpha = 128
            r, g, b, a = resized_img.split()
            a = a.point(lambda p: alpha)  # 全ピクセルのαを128に
            transparent_img = Image.merge("RGBA", (r, g, b, a))

            # Tkinter用に変換（PhotoImage）
            meaple_photo = ImageTk.PhotoImage(transparent_img)
            self.images_move_meaple.append(meaple_photo)  # 保持しておく
            self.canvas.create_image(cx, cy, image=meaple_photo, anchor="center")  # 中央基準
    
    
