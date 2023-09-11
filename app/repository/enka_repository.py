import lib.downloader as downloader
from aiohttp import client_exceptions
from fastapi import HTTPException
from model.enka_model import Enka


MESSAGES = {
    400: "UIDのフォーマットが間違っています。\n半角数字で入力してください",
    404: "入力されたものが存在するUIDではありません\nもう一度確認してやり直してください。",
    424: "ゲームメンテナンスやアップデートの影響により\nEnka.network（ビルドデータを取得するサービス）が停止している状態です。\nこのエラーはしばらく時間をおいてから試すと回復している可能性が高いです。",
    429: "処理が追いついていません。\nしばらくしても解決しない場合は、開発者に対してコンタクトをとってください。",
    500: "Enka.network（ビルドデータを取得するサービス）のサーバーにエラーが発生しています。\n詳しくはEnkaのTwitterを確認してください。https://twitter.com/EnkaNetwork",
    503: "Enka.network（ビルドデータを取得するサービス）サーバーの一時停止中です。\nしばらくお待ちください。※開発者はこれについて確認ぐらいしか取れないです。\n詳しくはEnkaのTwitterを確認してください"
}


async def get_enka_model(uid: int):
    try:
        data = await downloader.json_download(
            url=f"https://enka.network/api/uid/{uid}"
        )
        enka_model = Enka(** data)

        return enka_model

    except client_exceptions.ClientResponseError as e:
        print(e)
        raise HTTPException(
            status_code=451, detail=f"{MESSAGES[e.status]} \ncode: {e.status}")
