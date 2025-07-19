# tile.py
import os
import random
import csv
from cell import Cell

class Tile:
    SIZE = 5
    def __init__(self, cell_info_df, mark, tile_id):
        self.is_closed = None
        self.tile_id = tile_id
        self.mark = mark
        self.cells = [[None] * Tile.SIZE for _ in range(Tile.SIZE)]

        for _, row in cell_info_df.iterrows():
            cell_type = str(row["category"])
            x = int(row["x"])
            y = int(row["y"])
            self.cells[y][x] = Cell(cell_type, mark, tile_id)

    #タイルに含まれるセルクラスを取得するメソッド
    def get_cell(self, x, y):
        return self.cells[y][x]
    
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
                # old (x,y) → new (y, SIZE-1-x)
                new_cells[y][x] = self.cells[Tile.SIZE-1-x][y]
        self.cells = new_cells