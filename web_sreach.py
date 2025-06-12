import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sqlite3
from datetime import datetime

# G1レースのIDリスト（例: 2023年のG1レース）
g1_race_ids = [
    "202305010811",  # 例: 2023年の天皇賞（春）
]

# カラム名の定義（実際のデータ構造に合わせて更新）
columns = [
    "race_id", "着順", "枠番", "馬番", "馬名", "性齢", "斤量", "騎手", "タイム", 
    "着差", "通過", "上り", "単勝", "人気", "馬体重", "調教師", "馬主", "賞金",
    "備考1", "備考2", "備考3", "備考4"
]

def create_database():
    """データベースとテーブルを作成する"""
    conn = sqlite3.connect('keiba.db')
    cursor = conn.cursor()
    
    # レース結果テーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS race_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id TEXT,
        post_position INTEGER,
        horse_number INTEGER,
        horse_name TEXT,
        age_sex TEXT,
        weight TEXT,
        jockey TEXT,
        time TEXT,
        margin TEXT,
        position TEXT,
        last_3f TEXT,
        odds TEXT,
        popularity INTEGER,
        horse_weight TEXT,
        trainer TEXT,
        owner TEXT,
        prize TEXT,
        note1 TEXT,
        note2 TEXT,
        note3 TEXT,
        note4 TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

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

def save_to_database(race_id, results):
    """レース結果をデータベースに保存する"""
    conn = sqlite3.connect('keiba.db')
    cursor = conn.cursor()
    
    for row in results:
        # データの整形
        data = {
            'race_id': race_id,
            'post_position': row[1],  # 枠番
            'horse_number': row[2],   # 馬番
            'horse_name': row[3],     # 馬名
            'age_sex': row[4],        # 性齢
            'weight': row[5],         # 斤量
            'jockey': row[6],         # 騎手
            'time': row[7],           # タイム
            'margin': row[8],         # 着差
            'position': row[9],       # 通過
            'last_3f': row[10],       # 上り
            'odds': row[11],          # 単勝
            'popularity': row[12],    # 人気
            'horse_weight': row[13],  # 馬体重
            'trainer': row[14],       # 調教師
            'owner': row[15],         # 馬主
            'prize': row[16],         # 賞金
            'note1': row[17] if len(row) > 17 else None,
            'note2': row[18] if len(row) > 18 else None,
            'note3': row[19] if len(row) > 19 else None,
            'note4': row[20] if len(row) > 20 else None
        }
        
        # SQLクエリの作成と実行
        placeholders = ', '.join(['?' for _ in data])
        columns = ', '.join(data.keys())
        query = f"INSERT INTO race_results ({columns}) VALUES ({placeholders})"
        
        cursor.execute(query, list(data.values()))
    
    conn.commit()
    conn.close()

# test comment

def main():
    # データベースの作成
    create_database()
    
    # レースデータの取得と保存
    for race_id in g1_race_ids:
        print(f"Fetching {race_id} ...")
        result = get_race_result(race_id)
        if result:
            save_to_database(race_id, result)
            print(f"レースID {race_id} のデータを保存しました")
        time.sleep(2)  # サーバー負荷軽減のため2秒待機

if __name__ == "__main__":
    main() 