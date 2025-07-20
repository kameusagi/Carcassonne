# tile_factory.py
import os
import random
import pandas as pd
from tile import Tile

class TileFactory:
    folder_path = './タイル'
    
    def __init__(self):
        self.INIT_TILE = "tile04"  # 初期配置用のタイル名 
        self.INIT_TILE_ID = 2  # 初期配置用のタイル名 
        self.tile_id = 0  # タイルIDの初期値 
        self.folder = TileFactory.folder_path
        self.available = pd.read_csv(os.path.join(TileFactory.folder_path, "全体.csv"), encoding="utf-8-sig")
        
        if len(self.available) == 0:
            raise FileNotFoundError(f"{TileFactory.folder_path} に CSV が見つかりません")

    def next_tile(self,init=False):
        # もう使える CSV がなければエラー
        if len(self.available) == 0:
            raise RuntimeError("もう配置できるタイルが残っていません")
        if init:
            tile_info = self.available[self.available["id"] == self.INIT_TILE_ID].iloc[0]
        else:
            # ランダムに一つ選択
            tile_info = self.available.sample(n=1).iloc[0]

        self.available = self.available[self.available["id"] != tile_info["id"]]
        self.tile_num = len(self.available)
        folder_path = os.path.join(self.folder, "セル", f"{tile_info['タイル種類']}")
        csv_path = os.path.join(folder_path, "cell_info.csv")
        cell_info_df = pd.read_csv(csv_path, encoding="utf-8")
        mark = tile_info["ダイヤ"]

        self.tile_id = self.tile_id + 1
        tile = Tile(cell_info_df, mark, self.tile_id, folder_path)

        # Tile クラスにファイルパスを渡して生成
        return tile
