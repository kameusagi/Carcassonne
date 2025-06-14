# tile.py
import os
import random
import csv
from cell import Cell

class Tile:
    SIZE = 5
    def __init__(self, csv_path=None):
        
        file_path = csv_path
        x_coords,y_coords,types = [],[],[]

        with open(file_path, newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                x_coords.append(int(row["x"]))
                y_coords.append(int(row["y"]))
                types.append(int(row["category"]))

        grid = [[None] * Tile.SIZE for _ in range(Tile.SIZE)]
        for i in range(Tile.SIZE*Tile.SIZE):
            x,y = x_coords[i],y_coords[i] 
            grid[y][x] = types[i]

        self.cells = [[Cell(grid[y][x]) for x in range(Tile.SIZE)] 
                      for y in range(Tile.SIZE)]

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