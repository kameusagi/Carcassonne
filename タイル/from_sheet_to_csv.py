import pandas as pd
import os

CELL_COLORS = {
    0: "教会",
    1: "道", 
    2: "町", 
    3: "草むら", 
    4: "交差点", 
    5: "境界", 
    None: "予備" 
}

def tile_to_csv(xls, sheet_name ,folder_path):
    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        
    # データフレームを作成するためのリストを初期化
    data = {'id': [], 'x': [], 'y': [], 'category': []}
    
    # 行列データを5x5で読み取る
    cell_ID_count = 0
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            data['id'].append(cell_ID_count)
            data['x'].append(j)
            data['y'].append(df.shape[1] - i - 1)
            data['category'].append(df.iat[i, j])
            cell_ID_count += 1
    
    # データフレームを作成
    result_df = pd.DataFrame(data)

    # マッピングを適用して新しい color カラムを追加
    result_df['category'] = result_df['category'].map(CELL_COLORS)

    # CSVファイル名を決定
    csv_file_path = os.path.join(folder_path,f"{sheet_name}.csv")
    
    # データフレームをCSVファイルとして保存
    result_df.to_csv(f"{csv_file_path}", index=False)

def tile_summay_to_csv(xls, sheet_name, folder_path):
    # df = pd.read_excel(xls, sheet_name=sheet_name, header=["タイル種類","枚数","ダイヤ有枚数"])
    df = pd.read_excel(xls, sheet_name=sheet_name, header=0)

    # 出力用のリスト
    expanded_rows = []

    # 各行について処理
    for _, row in df.iterrows():
        total = row["枚数"]
        diamond = row["ダイヤ有枚数"]
        normal = total - diamond

        # ダイヤありの行を追加
        for _ in range(diamond):
            expanded_rows.append({
                "タイル種類": row["タイル種類"],
                "ダイヤ": True
            })

        # ダイヤなしの行を追加
        for _ in range(normal):
            expanded_rows.append({
                "タイル種類": row["タイル種類"],
                "ダイヤ": False
            })
        # データフレームに変換
        expanded_df = pd.DataFrame(expanded_rows)

        #IDカラム追加
        expanded_df.insert(0, 'id', range(len(expanded_df)))

        # CSVに出力（エンコーディングは日本語向けに utf-8-sig を推奨）
        csv_file_path = os.path.join(folder_path,f"全体.csv")
        expanded_df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")

        print(expanded_df)

def process_excel_sheets_to_csv(excel_file_path):

    folder_path = os.path.dirname(excel_file_path)
    # エクセルファイルを読み込む
    xls = pd.ExcelFile(excel_file_path)
    
    # 各シートをCSVファイルとして保存する
    for sheet_name in xls.sheet_names:
        if sheet_name == "全体":
            tile_summay_to_csv(xls, sheet_name, folder_path)
        else:
            tile_to_csv(xls, sheet_name, folder_path)
        

# 使用例
folder_path = './タイル'  # ここにエクセルファイルのパスを指定してください
excel_file_name = 'タイル検討.xlsx'  # ここにエクセルファイルのパスを指定してください
process_excel_sheets_to_csv(os.path.join(folder_path, excel_file_name))
