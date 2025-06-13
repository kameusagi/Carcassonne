from tile import Tile

class Player:
    def __init__(self, name: str, tile_type: str):
        self.name = name
        self.tile_type = tile_type

    def create_tile(self):
        return Tile(self.tile_type)
