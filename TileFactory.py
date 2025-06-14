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

    def next_tile(self):
        # もう使える CSV がなければエラー
        if not self.available:
            raise RuntimeError("もう配置できるタイルが残っていません")
        # ランダムに一つ選んでリストから削除
        path = random.choice(self.available)
        self.available.remove(path)
        # Tile クラスにファイルパスを渡して生成
        return Tile(csv_path=path)
