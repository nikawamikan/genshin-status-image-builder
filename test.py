import requests
from PIL import Image
from io import BytesIO
import json
import time

UID = 857377017

def gen_image_test(gen_mode:str):
    global start

    # エンドポイントのURL
    endpoint_url = f"http://localhost/buildimage/genshinstat/{gen_mode}/"

    # POSTするJSONデータ
    with open('response_1687156408314.json', "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)

    for index, i in enumerate(json_data['characters']):
        #ビルドタイプを指定
        # json_data = json_data['characters'][2]
        json_data = i
        json_data['build_type'] = 'atk'

        # JSONをPOSTリクエストで送信
        response = requests.post(endpoint_url, json=json_data)

        # 画像データを取得して表示
        if response:
            # レスポンスから画像データを取得
            image_data = response.content

            # 画像データをPILのImageオブジェクトに変換
            image = Image.open(BytesIO(image_data))

            print(f"{index+1}枚目：ダウンロード開始 / {str(time.time() - start)}秒")
            # 画像を表示
            image.show()
            print(f"{index+1}枚目：ダウンロード終了 / {str(time.time() - start)}秒")
        else:
            print("No image data found in the response.")
    print(f"平均処理時間：{str((time.time() - start)/index+1)}秒")

select = input("1:画像生成、2:uidデータ")

if select=="1":
    print("画像生成開始")
    start = time.time()

    print("========《GenshinStatus版画像生成》========")
    gen_image_test("0")
    print("========《Artifact版画像生成》========")
    gen_image_test("1")
    print("========《処理終了》========")
    print(f"処理時間：{str(time.time() - start)}秒")

elif select=="2":
    endpoint_url = f"http://localhost/status/uid/{UID}/"
    # JSONをPOSTリクエストで送信
    response = requests.get(endpoint_url)
    print(response)
    print(response.content)