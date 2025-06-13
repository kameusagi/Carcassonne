from tile import Tile
from cell import Cell

class DynamicMap:
    def __init__(self):
        self.cells = {}
        self.tile_size = Tile.SIZE

    def get_cell(self, x, y):
        return self.cells.get((x, y), Cell())

    def is_area_empty(self, x0, y0, tile):
        for dy in range(self.tile_size):
            for dx in range(self.tile_size):
                x = x0 + dx
                y = y0 + dy
                if (x, y) in self.cells:
                    return False
        return True

    def is_adjacent_compatible(self, x0, y0, tile):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dy in range(self.tile_size):
            for dx in range(self.tile_size):
                x = x0 + dx
                y = y0 + dy
                for dx2, dy2 in directions:
                    nx = x + dx2
                    ny = y + dy2
                    if (nx, ny) in self.cells:
                        neighbor = self.cells[(nx, ny)]
                        if neighbor.cell_type != tile.cell_type:
                            return False
        return True

    def can_place_tile(self, x0, y0, tile):
        return self.is_area_empty(x0, y0, tile) and self.is_adjacent_compatible(x0, y0, tile)

    def place_tile(self, x0, y0, tile):
        if not self.can_place_tile(x0, y0, tile):
            print(f"タイル（{tile.cell_type}）を({x0},{y0})に配置できません")
            return False
        for dy in range(self.tile_size):
            for dx in range(self.tile_size):
                self.cells[(x0 + dx, y0 + dy)] = tile.get_cell(dx, dy)
        return True
