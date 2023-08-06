import requests
from PIL import Image
from io import BytesIO
import json
import time
print("画像生成開始")
start = time.time()

# エンドポイントのURL
endpoint_url = "http://localhost/buildimage/genshinstat/0/"

# POSTするJSONデータ
with open('response_1687156408314.json', "r", encoding="utf-8") as json_file:
    json_data = json.load(json_file)

#ビルドタイプを指定
json_data = json_data['characters'][1]
json_data['build_type'] = 'atk'

# JSONをPOSTリクエストで送信
response = requests.post(endpoint_url, json=json_data)

# 画像データを取得して表示
if response:
    # レスポンスから画像データを取得
    image_data = response.content

    # 画像データをPILのImageオブジェクトに変換
    image = Image.open(BytesIO(image_data))

    print(f"ダウンロード開始 / {str(time.time() - start)}秒")
    # 画像を表示
    image.show()
    print(f"ダウンロード終了 / {str(time.time() - start)}秒")
else:
    print("No image data found in the response.")
