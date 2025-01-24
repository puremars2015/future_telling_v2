from datetime import datetime
import os
from flask import Flask, request, jsonify, render_template, send_file
from openai import OpenAI
from chance60 import Chance60Service
import random

from config import key
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# 設置您的 OpenAI API 密鑰
api_key = key['OpenAI']

GPT = OpenAI(api_key=api_key)


# 首頁
@app.route('/')
def index():
    return render_template('index.html',  error=None)

# 大師歡迎詞
@app.route('/welcome')
def view_welcome():
    return render_template('index.html',  error=None)


# 與大師對話
@app.route('/chat')
def view_chat():
    return render_template('chat.html')

# 與大師對話
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'response': '請輸入問題'})
    
    # 使用 OpenAI API 判斷問題屬性,是否需要籤詩
    response = GPT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一個台灣命理問題分析機器人，專門判斷這個問題是否適合用媽祖60支籤詩。適合回答1,不適合回答0"},
            {"role": "user", "content": user_input}
        ]
    )

    # 使用 OpenAI API 判斷問題是否需要生辰八字
    response = GPT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一個台灣命理問題分析機器人，專門判斷這個問題是否需要生辰八字。適合回答1,不適合回答0"},
            {"role": "user", "content": user_input}
        ]
    )

    # 使用 OpenAI API 生成回應
    response = GPT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一個台灣命理大師，專門解答問題。"},
            {"role": "user", "content": user_input}
        ]
    )
    response_message = response.choices[0].message.content

    return jsonify({'response': response_message, 'ok': True})


# info
@app.route('/info')
def view_intro():
    return render_template('info.html',  error=None)

@app.route('/draw_straws', methods=['GET'])
def view_draw_straws():
    return render_template('draw_straws.html',  error=None)

@app.route('/draw_straws', methods=['POST'])
def draw_straws():

    problemSituation = request.json.get('problemSituation')
    if not problemSituation:
        return jsonify({'signPoems': '無事所求，不必問，自有安排，自有分配。'})

    # 使用當天的日期和基數生成隨機種子，以確保每天的運氣是不同的
    random.seed(int(datetime.now().timestamp()))
    
    # 生成一個0到100之間的隨機數，作為運氣指數
    luck_index = random.randint(1, 65)

    # 從future_telling.db取得資料,亂數取出一筆籤詩
    lots = Chance60Service()
    signPoems = lots.GetCardById(luck_index)
    return jsonify({'signPoems': signPoems[1]})

@app.route('/explain', methods=['POST'])
def explain():
    problemSituation = request.json.get('problemSituation')
    signPoems = request.json.get('signPoems')

    # problemSituation 是否為空值,若為空值則回傳錯誤訊息
    if not problemSituation:
        return jsonify({'explain': '請輸入您的問題'})
    
    # signPoems 是否為空值,若為空值則回傳錯誤訊息
    if not signPoems:
        return jsonify({'explain': '請抽籤'})
    
    prompt = f'''
    我想詢問:{problemSituation}。
    我抽到的籤詩是:\n\n{signPoems}。
    以上，請專注在回答從這個籤詩看我想詢問的事項，是好還是壞，如果是需要從選項中選一個的問題，請盡量從其中一個選出答案，不要用通通都可以的回答。
    請大師幫我說明一下，謝謝。
    '''

    if signPoems:
        # 使用 OpenAI API 生成文章大綱
        explain_response = GPT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是一個命理大師，專門解釋籤詩的含義。"},
                {"role": "user", "content": prompt}
            ]
        )
        explain = explain_response.choices[0].message.content

    # 存入資料庫
    lots = Chance60Service()
    lots.InsertRecord(problemSituation, signPoems, explain)

    return jsonify({'explain': explain})


# 取得資料庫中的籤詩
@app.route('/get_sign_poems', methods=['GET'])
def get_sign_poems():
    lots = Chance60Service()
    signPoems = lots.GetCard()
    return jsonify({'signPoems': signPoems})

# 取得資料庫中的紀錄
@app.route('/get_records', methods=['GET'])
def get_records():
    lots = Chance60Service()
    records = lots.GetRecord()
    return jsonify({'records': records}), 200, {'Content-Type': 'application/json; charset=utf-8'}

# 下載future_telling.db
@app.route('/download_db', methods=['GET'])
def download_db():
    return send_file('database/future_telling.db', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)