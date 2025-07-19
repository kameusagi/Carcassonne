import networkx as nx

from tile import Tile
from cell import Cell

class DynamicMap:
    def __init__(self):
        self.cells = {}
        self.tiles = {}
        self.meaples = {}
        # タイル配置直後のセル座標を保持するリスト
        self.before_tile_place = []
        #　タイルを配置した後に、回収されたミープルを保持するリスト
        self.before_meaples = {}

    def get_cell(self, x, y):
        return self.cells.get((x, y), Cell())

    def get_tile(self, x, y):
        return self.tiles.get((x, y), Tile())

    def is_area_empty(self, x0, y0):
            return (x0, y0) not in self.tiles

    def is_adjacent_compatible(self, x0, y0, tile):
        """
        タイルを (x0, y0) に配置できるか判定。
        - 周囲のセルが空いているか
        - 隣接セルとの互換性があるか
        """
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
                            if not (neighbor.cell_type == "境界" or tile_cell.cell_type == "境界"): 
                                # 境界タイル以外で種類が異なるセルが隣接している場合は配置不可
                                return False
                            else:
                                pass
                                
        # 隣接セルが1つもなければ配置不可
        return has_neighbor

    def can_place_tile(self, x0, y0, tile, init):
        judge = (self.is_area_empty(x0, y0) and #タイルが置かれていない
            self.is_adjacent_compatible(x0, y0, tile) #隣接セルとの互換性
        )
        print(judge,init)
        judge = judge or init
        return judge

    def place_tile(self, x0, y0, tile, init=False):
        if not self.can_place_tile(x0, y0, tile, init):
            print(f"タイルを配置できません")
            return False
        for dy in range(Tile.SIZE):
            for dx in range(Tile.SIZE):
                self.cells[(x0 + dx, y0 + dy)] = tile.get_cell(dx, dy)
        self.tiles[(x0, y0)] = tile
        self.before_tile_place = [(x0 + dx, y0 + dy) for dy in range(Tile.SIZE) for dx in range(Tile.SIZE)]
        return True
    
    def patch_id_at_meaple(self, x, y):
        for (x_me, y_me) in self.meaples.keys():
            cell_me = self.get_cell(x_me, y_me)
            cell_target = self.get_cell(x, y)

            if (cell_me.cell_type == cell_target.cell_type and
                cell_me.patch_ids == cell_target.patch_ids):
                return False
        return True
    
    def can_place_meaple(self, x, y):
        """
        ミープルを (x,y) に置けるか判定。
        """
        # 直前に置いたタイルの座標のみにしかミープルは置けない
        if (x, y) not in self.before_tile_place:
            print("そのタイルは今置いたタイルではありません")
            return False

        #ミープルが置けないセル
        if self.cells[(x, y)].cell_type in ["境界", "交差点", "予備"]:
            return False
        
        # 回収されたてのミープルが置かれたセルの領域には置けない
        for x_beforeme, y_beforeme in self.before_meaples.keys():
            player_cell = self.get_cell(x_beforeme, y_beforeme)
            player_patch_id = player_cell.patch_ids
            player_cell_type = player_cell.cell_type
            if (player_cell_type == self.get_cell(x, y).cell_type and
                player_patch_id == self.get_cell(x, y).patch_ids):
                return False
        
        # 置こうとしたセルが草むら、道、町の時、そのセルタイプに同じミープルが置かれているかチェック
        return (self.patch_id_at_meaple(x,y))

    def place_meaple(self, x, y, player):
        """
        ミープルを (x,y) に配置。
        init=True のときは強制配置（初期設定など）を許可。
        """
        # 判定メソッドで NG かつ通常モードならキャンセル
        if not self.can_place_meaple(x, y):
            print("ミープルを配置できません")
            return False
        if not player.put_meaple():
            print(f"{player.name}さんのストックが足りません")
            return False

        # 成功時は辞書に登録
        self.meaples[(x, y)] = player
        return True
    
    def update_cell_area(self):
        """
        各セルのpatchidを更新する
        - 道、町、草むらのセルをそれぞれ連結成分として識別
        - patch_ids 属性に連結成分のIDを設定
        """
        for t in ["道","町","草むら","教会","境界","交差点","予備"]:
            G = nx.Graph()
            # 1) ノード追加：対象タイプのみ
            for (x,y), cell in self.cells.items():
                if cell.cell_type == t:
                    self.cells[(x, y)].is_closed = True #初期化
                    G.add_node((x, y),cell=cell)

            # 2) 隣接ノード間をエッジで結ぶ（上下左右）
            for x, y in list(G.nodes):
                for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    if (x+dx, y+dy) in G:
                        G.add_edge((x, y), (x+dx, y+dy))

            for pid, component in enumerate(nx.connected_components(G), start=1):
                for (x, y) in component:
                    self.cells[(x, y)].patch_ids = pid
            for x, y in list(G.nodes):
                for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    neighbor = (x + dx, y + dy)
                    if neighbor not in self.cells.keys(): #周辺のセルが存在しない場合
                        self.cells[(x, y)].is_closed = False

            for pid, component in enumerate(nx.connected_components(G), start=1):
                values = [self.cells[(x, y)].is_closed for (x,y) in component]
                if any(v is False for v in values):
                    for (x, y) in component:
                        self.cells[(x, y)].is_closed = False
                elif all(v is not False for v in values):
                    for (x, y) in component:
                        self.cells[(x, y)].is_closed = True
    
    def update_tile_area(self):
        for (x,y) in self.tiles.keys():
            directions = [
                (dx * Tile.SIZE, dy * Tile.SIZE)
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
                if not ((dx == 0 and dy == 0) or (dx == dy)) #中心と対角線上のセルは除外
            ]

            for dx, dy in directions:
                neighbor = (x + dx, y + dy)
                if neighbor not in self.tiles.keys(): #周辺のセルが存在しない場合
                    self.tiles[(x, y)].is_closed = False
                else:
                    self.tiles[(x, y)].is_closed = True

    #ミープルを自動で回収する機能
    def collect_meaples(self):
        """
        ミープルを自動で回収する。
        - 各セルの patch_ids を更新
        - ミープルを回収
        """
        for (x, y), player in list(self.meaples.items()):
            cell = self.get_cell(x, y)
            if cell.cell_type in ["道", "町"]:
                if cell.is_closed:
                    del self.meaples[(x, y)]  # ミープルを回収
                    self.before_meaples[(x, y)] = player
                    player.pull_meaple()
            elif cell.cell_type == "教会":
                #セルが置かれているタイルを取得
                tile_id = self.cells[(x, y)].tile_id
                for tile in self.tiles.values():
                    if tile.tile_id == tile_id:
                        tile_coord = [key for key, value in self.tiles.items() if value is tile][0]
                        break
                if self.cells[tile_coord].is_closed:
                    del self.meaples[(x, y)]
                    player.pull_meaple()
                