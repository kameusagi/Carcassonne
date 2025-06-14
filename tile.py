# tile.py
import random
from cell import Cell

class Tile:
    SIZE = 3

    def __init__(self, cell_type=None):
        # self.cell_type = cell_type  # 追加！
        if isinstance(cell_type, str):
            types = [[cell_type] * Tile.SIZE for _ in range(Tile.SIZE)]
        else:
            # None のときはランダムに生成
            choices = ["grass", "water", "stone"]
            types = [
                [random.choice(choices) for _ in range(Tile.SIZE)]
                for _ in range(Tile.SIZE)
            ]

        # 最終的に 2D リストを元に Cell を作成
        self.cells = [
            [Cell(types[y][x]) for x in range(Tile.SIZE)]
            for y in range(Tile.SIZE)
        ]

    def get_cell(self, x, y):
        return self.cells[y][x]
