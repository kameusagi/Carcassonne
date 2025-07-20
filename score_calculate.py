import networkx as nx
from collections import defaultdict, Counter
from tile import Tile

def score_calculation(players, map):
    """
    スコア計算のロジックをここに実装
    """
    for player in players:
        player.score_sub = 0  # サブスコアをリセット
    
    work = []

    for (x, y), player in map.meaples.items():
        cell = map.cells[(x, y)]
        cell_type = cell.cell_type
        patch_id = cell.patch_ids
        is_closed = cell.is_closed
        work.append((x, y, player.name, cell_type, patch_id, is_closed))

    # 1. グルーピング：同じ (cell_type, patch_id) ごとに要素を集める
    group_map = defaultdict(list)
    for entry in work:
        key = (entry[3], entry[4])  # (cell_type, patch_id)
        group_map[key].append(entry)

    # 2. 各グループ内で player.name をカウントし、残すべき player を決定
    result = []
    for entries in group_map.values():
        if len(entries) == 1:
            # 重複なしならそのまま残す
            result.append(entries[0])
        else:
            name_counts = Counter(e[2] for e in entries)  # player.name のカウント
            max_count = max(name_counts.values())
            top_players = [name for name, cnt in name_counts.items() if cnt == max_count]

            if len(top_players) == 1:
                # 最多1人なら、その人のエントリだけ残す
                winner = top_players[0]
                result.extend([e for e in entries if e[2] == winner])
            else:
                # 複数人が同率 → 全削除
                pass

    for cell_info in result:
        cell_x, cell_y, player_name, cell_type, patch_id, is_closed = cell_info
        
        if cell_type == "町":
            unique_town = []
            for cell in map.cells.values():
                if (cell.patch_ids == patch_id) and (cell.cell_type == cell_type):
                    unique_town.append([cell.tile_id,cell.mark]) #Todo.　0には、タイルスターの情報を入れる
            unique_town = set(tuple(x) for x in unique_town)
            for player in players:
                if player.name == player_name:
                    if is_closed:
                        player.score += (len(unique_town) + sum(tile[1] for tile in unique_town))*2
                    else:
                        player.score_sub += (len(unique_town) + sum(tile[1] for tile in unique_town))*1

        elif cell_type == "道":
            unique_load = []
            for cell in  map.cells.values():
                if (cell.patch_ids == patch_id) and (cell.cell_type == cell_type):
                    unique_load.append(cell.tile_id) 
            unique_load = set(unique_load)
            for player in  players:
                if player.name == player_name:
                    if is_closed:
                        player.score += len(unique_load)
                    else:
                        player.score_sub += len(unique_load)

        elif cell_type == "草むら":
            unique_grass = []
            for cell in  map.cells.values():
                if (cell.patch_ids == patch_id) and (cell.cell_type == cell_type):
                    unique_grass.append([cell.tile_id,0]) 
            unique_grass = set(tuple(x) for x in unique_grass)
            for player in players:
                if player.name == player_name:
                    # 草むらの得点計算
                    # patch_idが同じ草むらの中で、完成した街が面している個数をカウントする機能
                    player.score_sub += facing_town(patch_id,map)

        elif cell_type == "教会":
            for player in players:
                if player.name == player_name:
                    tile_id = map.cells[(cell_x, cell_y)].tile_id
                    for tile in map.tiles.values():
                        if tile.tile_id == tile_id:
                            tile_coord = [key for key, value in  map.tiles.items() if value is tile][0]
                            tile_coord_x, tile_coord_y = tile_coord
                            break
                    directions = [
                        (dx * Tile.SIZE + tile_coord_x, dy * Tile.SIZE + tile_coord_y)
                        for dx in (-1, 0, 1)
                        for dy in (-1, 0, 1)
                    ]
                    if tile.is_closed:
                        player.score += 9
                    else:
                        player.score_sub += sum(1 for key in directions if key in  map.tiles)

def facing_town(patch_id, map):
    # patch_idが同じ草むらの中で、完成した街が面している個数をカウントする機能
    
    G = nx.Graph()
    for (x,y), cell in map.cells.items():
        if cell.cell_type == "草むら" and cell.patch_ids == patch_id:
            G.add_node((x, y),cell=cell)
    # 草むらの輪郭のセルの座標を取得
    contour_cells = []
    for x, y in list(G.nodes):
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            neighbor = (x + dx, y + dy)
            if (neighbor in map.cells.keys()) and neighbor not in G.nodes:  #隣接セルが草むらでない場合
                # 輪郭セルを追加
                contour_cells.append((x, y))
                break
    # 輪郭セルの周囲にある街のセルを取得
    town_patch_ids = set()
    for x, y in contour_cells:
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            neighbor = (x + dx, y + dy)
            if neighbor in map.cells.keys():
                if (neighbor not in G.nodes) and \
                    (map.cells[neighbor].cell_type == "町") and \
                        (map.cells[neighbor].is_closed == True):
                    town_patch_ids.add(map.cells[neighbor].patch_ids)
                    
    score = len(town_patch_ids) * 3  # 街の数に応じてスコアを加算
    return score