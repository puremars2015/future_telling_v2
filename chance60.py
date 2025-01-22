
try:
    import pandas as pd
except:
    import os
    os.system('pip install pandas')
    import pandas as pd
import sqlite3
import json

def CreateTable():
    conn = sqlite3.connect('database/future_telling.db')

    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS DRAW_STRAWS_RECORD
                (id INTEGER PRIMARY KEY, 
                PROBLEM_SITUATION TEXT,
                SIGN_POEMS TEXT,
                EXPLAIN TEXT)''')
    conn.commit()
    conn.close()


def ETL_excel_to_db():
    conn = sqlite3.connect('database/future_telling.db')
    df = pd.read_excel('chance60.xlsx')

    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS TB_CHANCE_60
                (id INTEGER PRIMARY KEY, 
                content TEXT)''')

    for i in range(1, 65):
        content = ','.join(df.iloc[0:4, i-1].array.tolist())
        r = cursor.execute('INSERT INTO TB_CHANCE_60 (CONTENT) VALUES (?)', (content,))
        print(r.arraysize)

    conn.commit()
    conn.close()

    return True

def ETL_db_to_json():
    conn = sqlite3.connect('database/future_telling.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM TB_CHANCE_60')
    data = cursor.fetchall()
    conn.close()

    with open('chance60.json', 'w') as f:
        json.dump(data, f)

    return True

def GetCard():
    with open('chance60.json', 'r') as f:
        data = json.load(f)
    return data

def GetCardById(id):
    with open('chance60.json', 'r') as f:
        data = json.load(f)
    return data[id-1]



class Chance60Service:
    def __init__(self):
        self.conn = sqlite3.connect('database/future_telling.db')
        self.cursor = self.conn.cursor()

    def GetCard(self):
        self.cursor.execute('SELECT * FROM TB_CHANCE_60')
        data = self.cursor.fetchall()
        return data

    def GetCardById(self, id):
        self.cursor.execute('SELECT * FROM TB_CHANCE_60 WHERE ID = ?', (id,))
        data = self.cursor.fetchone()
        return data

    def InsertRecord(self, problem_situation, sign_poems, explain):
        self.cursor.execute('INSERT INTO TB_DRAW_STRAWS_RECORD (PROBLEM_SITUATION, SIGN_POEMS, EXPLAIN) VALUES (?,?,?)', (problem_situation, sign_poems, explain))
        self.conn.commit()

    def __del__(self):
        self.conn.close()


