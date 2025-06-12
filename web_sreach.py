import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# G1レースのIDリスト（例: 2023年のG1レース）
g1_race_ids = [
    "202305010812",  # 例: 2023年の天皇賞（春）
]

# カラム名の定義（実際のデータ構造に合わせて更新）
columns = [
    "race_id", "着順", "枠番", "馬番", "馬名", "性齢", "斤量", "騎手", "タイム", 
    "着差", "通過", "上り", "単勝", "人気", "馬体重", "調教師", "馬主", "賞金",
    "備考1", "備考2", "備考3", "備考4"
]

def get_race_result(race_id):
    url = f"https://db.netkeiba.com/race/{race_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    res.encoding = 'EUC-JP'  # netkeibaはEUC-JPエンコーディングを使用
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", class_="race_table_01")
    if table is None:
        print(f"レースID {race_id} のデータが見つかりません")
        return None

    rows = table.find_all("tr")[1:]  # 1行目はヘッダー
    results = []
    for row in rows:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if cols:
            results.append(cols)
    return results

all_results = []
for race_id in g1_race_ids:
    print(f"Fetching {race_id} ...")
    result = get_race_result(race_id)
    if result:
        for row in result:
            all_results.append([race_id] + row)
    time.sleep(2)  # サーバー負荷軽減のため2秒待機

# デバッグ情報の出力
print("\n=== デバッグ情報 ===")
print(f"取得したデータの行数: {len(all_results)}")
if all_results:
    print(f"1行目の要素数: {len(all_results[0])}")
    print(f"1行目のデータ: {all_results[0]}")
    print(f"カラム名の数: {len(columns)}")
    print(f"カラム名: {columns}")

# データが存在する場合のみDataFrameを作成
if all_results:
    df = pd.DataFrame(all_results, columns=columns)
    df.to_csv("g1_race_results.csv", index=False, encoding="utf-8-sig")
    print("保存完了: g1_race_results.csv")
else:
    print("データが取得できませんでした。")