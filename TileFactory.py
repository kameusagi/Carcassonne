# tile_factory.py
import os
import random
from tile import Tile

class TileFactory:
    def __init__(self, folder_path):
        # フォルダ内の CSV をすべて読み込む
        self.folder = folder_path
        self.available = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(".csv")
        ]
        if not self.available:
            raise FileNotFoundError(f"{folder_path} に CSV が見つかりません")

    def next_tile(self,init=False):
        # もう使える CSV がなければエラー
        if not self.available:
            raise RuntimeError("もう配置できるタイルが残っていません")
        if init:
            path = [path for path in self.available if "tile04" in path][0]
        else:
            # ランダムに一つ選んでリストから削除
            path = random.choice(self.available)
        print(path)
        self.available.remove(path)
        tile = Tile(csv_path=path)
        # ランダムに数回転させる
        for _ in range(random.randint(0, 3)):
            tile.rotate()

        # Tile クラスにファイルパスを渡して生成
        return tile
