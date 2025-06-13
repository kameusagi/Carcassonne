class Cell:
    def __init__(self, cell_type=None):
        self.cell_type = cell_type

    def is_empty(self):
        return self.cell_type is None

    def __str__(self):
        return self.cell_type[0].upper() if self.cell_type else "."
