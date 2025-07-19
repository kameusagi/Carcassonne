class Cell:
    def __init__(self, cell_type=None, mark=None, tile_id=None):
        self.cell_type = cell_type
        self.patch_ids = None
        self.tile_id = tile_id
        self.mark = mark
        self.is_closed = None
        self.is_closed = None
    
    def is_empty(self):
        return self.cell_type is None

    # def __str__(self):
    #     # return self.cell_type[0].upper() if self.cell_type else "."
    #     return self.cell_type
