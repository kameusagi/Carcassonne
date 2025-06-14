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
        print(file_path)

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