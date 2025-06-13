from cell import Cell

class Tile:
    SIZE = 3

    def __init__(self, cell_type="grass"):
        self.cell_type = cell_type
        self.cells = [
            [Cell(cell_type) for _ in range(Tile.SIZE)]
            for _ in range(Tile.SIZE)
        ]

    def get_cell(self, x, y):
        return self.cells[y][x]
