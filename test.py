import requests
from PIL import Image
from io import BytesIO
import json

# エンドポイントのURL
endpoint_url = "http://localhost/genshinstat/1/"

# POSTするJSONデータ
with open('response_1687156408314.json', "r", encoding="utf-8") as json_file:
    json_data = json.load(json_file)

# JSONをPOSTリクエストで送信
response = requests.post(endpoint_url, json=json_data)

# レスポンスをJSONとして解析
print(response)
image_data = response

# 画像データを取得して表示
if image_data:
    image = Image.open(BytesIO(image_data))
    image.show()
else:
    print("No image data found in the response.")
