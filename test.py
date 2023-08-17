import requests
from PIL import Image
from io import BytesIO
import json
import time
from concurrent.futures import ThreadPoolExecutor
import copy

UID = 857377017


def get_image(json_data, image_list, endpoint_url):
    print(f"download -> {json_data['id']}")
    response = requests.post(endpoint_url, json=json_data)

    # 画像データを取得して表示
    if response:
        # レスポンスから画像データを取得
        image_data = response.content

        # 画像データをPILのImageオブジェクトに変換
        image_list.append(Image.open(BytesIO(image_data)))

    else:
        print("No image data found in the response.")

def gen_image_bench_test(gen_mode:str):
    global start

    # エンドポイントのURL
    endpoint_url = f"http://localhost/buildimage/genshinstat/{gen_mode}/"

    with open("./app/data/characters.json", "r", encoding="utf-8") as f:
        characters = json.load(f)

    # POSTするJSONデータ
    with open('response_1687156408314.json', "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)

    json_data = json_data['characters'][0]
    image_list = []
    filetime = str(time.time())
    json_data['create_date'] = filetime

    tyohukucheck = set()
    with ThreadPoolExecutor(thread_name_prefix="__create") as pool:
        for k, v in characters.items():
            local_json = copy.deepcopy(json_data)
            try:
                #ビルドタイプを指定
                # json_data = json_data['characters'][2]
                local_json['id'] = k
                local_json['element'] = v['element']
                local_json['build_type'] = 'atk'

                pool.submit(
                    get_image,
                    local_json,
                    image_list,
                    endpoint_url
                )

                print(f"ID: {k}生成")
            except:
                print(f"ID: {k}スキップ")
                continue

    for i, image in enumerate(image_list):
        image:Image.Image = image
        try:
            image.save(f'./result/{i}.jpeg')
        except:
            pass
            
    print(f"平均処理時間：{str((time.time() - start)/len(characters))}秒")

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

def gen_profile_test():
    global start

    # エンドポイントのURL
    endpoint_url = f"http://localhost/buildimage/profile/"

    # POSTするJSONデータ
    with open('response_1687156408314.json', "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)

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








select = input("1:画像生成、2:uidデータ、3:プロフィール画像生成、4:全キャラクターベンチマーク")

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
    endpoint_url = f"http://localhost/status/uid/{UID}"
    # JSONをPOSTリクエストで送信
    response = requests.get(endpoint_url)
    print(response)
    print(response.content.decode())

elif select=="3":
    print("画像生成開始")
    start = time.time()

    print("========《Artifact版画像生成》========")
    gen_profile_test()
    print("========《処理終了》========")
    print(f"処理時間：{str(time.time() - start)}秒")

elif select=="4":
    print("画像生成開始")
    
    print("========《GenshinStatus版画像生成》========")
    start = time.time()
    gen_image_bench_test("0")
    print(f"処理時間：{str(time.time() - start)}秒")
    print("========《Artifact版画像生成》========")
    start = time.time()
    gen_image_bench_test("1")
    print(f"処理時間：{str(time.time() - start)}秒")
    print("========《処理終了》========")