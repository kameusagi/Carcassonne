# tile.py
import os
import random
import csv
from cell import Cell

class Tile:
    SIZE = 5
    def __init__(self):

        folder_path = "./タイル"

        files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]
        if not files:
            raise FileNotFoundError(f"{folder_path} に CSV が見つかりません")
        file_path = os.path.join(folder_path, random.choice(files))
        x_coords = []
        y_coords = []
        types = []
        print(file_path)
        with open(file_path, newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                # x,y は文字列なので int() で
                x = int(row["x"])
                y = int(row["y"])
                cat = int(row["category"])
                x_coords.append(x)
                y_coords.append(y)
                types.append(cat)

        grid = [[None] * Tile.SIZE for _ in range(Tile.SIZE)]
        for i in range(Tile.SIZE*Tile.SIZE):
            x = x_coords[i]
            y = y_coords[i] 
            grid[y][x] = types[i]

        self.cells = [[Cell(grid[y][x]) for x in range(Tile.SIZE)] for y in range(Tile.SIZE)]

    def get_cell(self, x, y):
        return self.cells[y][x]