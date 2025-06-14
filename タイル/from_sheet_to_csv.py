# import pandas as pd

# def save_sheets_as_csv(excel_file_path):
#     # エクセルファイルを読み込む
#     xls = pd.ExcelFile(excel_file_path)
    
#     # 各シートをCSVファイルとして保存する
#     for sheet_name in xls.sheet_names:
#         df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
#         csv_file_name = f"{sheet_name}.csv"
#         df.to_csv(csv_file_name, index=False, header=False)
#         print(f"Saved {csv_file_name}")

# # 使用例
# excel_file_path = 'タイル検討.xlsx'  # ここにエクセルファイルのパスを指定してください
# save_sheets_as_csv(excel_file_path)

import pandas as pd

def process_excel_sheets_to_csv(excel_file_path):
    # エクセルファイルを読み込む
    xls = pd.ExcelFile(excel_file_path)
    
    cell_ID_count = 0
    # 各シートをCSVファイルとして保存する
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        
        # データフレームを作成するためのリストを初期化
        data = {'id': [], 'x': [], 'y': [], 'category': []}
        
        # 行列データを5x5で読み取る
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                data['id'].append(cell_ID_count)
                data['x'].append(j)
                data['y'].append(df.shape[1] - i - 1)
                data['category'].append(df.iat[i, j])
                cell_ID_count += 1
        
        # データフレームを作成
        result_df = pd.DataFrame(data)
        
        # CSVファイル名を決定
        csv_file_name = f"{sheet_name}.csv"
        
        # データフレームをCSVファイルとして保存
        result_df.to_csv(f"{csv_file_name}", index=False)
        print(f"Saved {csv_file_name}")

# 使用例
excel_file_path = 'タイル検討.xlsx'  # ここにエクセルファイルのパスを指定してください
process_excel_sheets_to_csv(excel_file_path)
