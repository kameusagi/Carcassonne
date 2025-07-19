# tile_factory.py
import os
import random
import pandas as pd
from tile import Tile

class TileFactory:
      
    def __init__(self, folder_path):
        self.INIT_TILE = "tile04"  # 初期配置用のタイル名 
        self.INIT_TILE_ID = 44  # 初期配置用のタイル名 
        self.tile_id = 0  # タイルIDの初期値 
        # フォルダ内の CSV をすべて読み込む
        self.folder = folder_path

        #self.available はcsvをデータフレームにしたものである
        self.available = pd.read_csv(os.path.join(folder_path,"全体.csv"), encoding="utf-8-sig")
        
        # print(f"利用可能なタイル: {self.available}")
        # if not self.available:
        if len(self.available) == 0:
            raise FileNotFoundError(f"{folder_path} に CSV が見つかりません")

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
        path = os.path.join(self.folder, f"{tile_info['タイル種類']}.csv")
        cell_info_df = pd.read_csv(path, encoding="utf-8")
        mark = tile_info["ダイヤ"]

        self.tile_id = self.tile_id + 1
        tile = Tile(cell_info_df, mark, self.tile_id)
        
        # ランダムに数回転させる
        for _ in range(random.randint(0, 3)):
            tile.rotate()

        # Tile クラスにファイルパスを渡して生成
        return tile
