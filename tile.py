# tile.py
import os
import random
import csv
from cell import Cell

class Tile:
    SIZE = 5
    def __init__(self, cell_info_df, mark, tile_id, folder_path):
        self.is_closed = None
        self.tile_id = tile_id
        self.mark = mark
        self.folder_path = folder_path
        self.cells = [[None] * Tile.SIZE for _ in range(Tile.SIZE)]

        for _, row in cell_info_df.iterrows():
            cell_type = str(row["category"])
            x = int(row["x"])
            y = int(row["y"])
            png_path = os.path.join(folder_path, f"x_{x}_y_{y}.png")
            self.cells[x][y] = Cell(cell_type, mark, tile_id, png_path)

    #タイルに含まれるセルクラスを取得するメソッド
    def get_cell(self, x, y):
        return self.cells[x][y]
    
    def rotate(self):
        """
        90°右回転（時計回り）してセル配置を更新。
        self.cells[y][x] を変えていきます。
        """
        new_cells = [
            [None] * Tile.SIZE
            for _ in range(Tile.SIZE)
        ]
        for y in range(Tile.SIZE):
            for x in range(Tile.SIZE):
                new_cells[x][y] = self.cells[Tile.SIZE - 1 - y][x]
                new_cells[x][y].rotate()
        self.cells = new_cells