from tile import Tile
from cell import Cell

class DynamicMap:
    def __init__(self):
        self.cells = {}

    def get_cell(self, x, y):
        return self.cells.get((x, y), Cell())

    def is_area_empty(self, x0, y0, tile):
        for dy in range(Tile.SIZE):
            for dx in range(Tile.SIZE):
                x = x0 + dx
                y = y0 + dy
                if (x, y) in self.cells:
                    return False
        return True

    def is_adjacent_compatible(self, x0, y0, tile):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        has_neighbor = False

        for dy in range(Tile.SIZE):
            for dx in range(Tile.SIZE):
                gx, gy = x0 + dx, y0 + dy
                for dx2, dy2 in directions:
                    nx, ny = gx + dx2, gy + dy2
                    if (nx, ny) in self.cells:
                        has_neighbor = True
                        neighbor = self.cells[(nx, ny)]
                        tile_cell = tile.get_cell(dx, dy)
                        # 種類が異なればすぐに配置不可
                        if neighbor.cell_type != tile_cell.cell_type:
                            if not (neighbor.cell_type == 5 or tile_cell.cell_type == 5): 
                                return False
                            else:
                                # 5はどのタイルとも隣接可能
                                pass
                                
                                
        # 隣接セルが1つもなければ配置不可
        return has_neighbor


    def can_place_tile(self, x0, y0, tile):
        return self.is_area_empty(x0, y0, tile) and self.is_adjacent_compatible(x0, y0, tile)

    def place_tile(self, x0, y0, tile, init=False):
        if (not self.can_place_tile(x0, y0, tile) and not init):
            print(f"タイルを配置できません")
            return False
        for dy in range(Tile.SIZE):
            for dx in range(Tile.SIZE):
                self.cells[(x0 + dx, y0 + dy)] = tile.get_cell(dx, dy)
        return True
