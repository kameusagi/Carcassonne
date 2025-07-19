class Cell:
    def __init__(self, cell_type=None, mark=None, tile_id=None, png_path=None):
        self.cell_type = cell_type
        self.patch_ids = None
        self.tile_id = tile_id
        self.mark = mark
        self.is_closed = None
        self.png_path = png_path
        self.rotate_count = 0  # 回転回数の初期値
    
    def is_empty(self):
        return self.cell_type is None
    
    def rotate(self):
        self.rotate_count += 1
        self.rotate_count %= 4

