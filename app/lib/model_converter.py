from pydantic import BaseModel


def conversion_dict_to_model(data: dict, model: BaseModel) -> dict[str, BaseModel]:
    """dictをmodelの型に変換し返却します

    Args:
        data (dict): json形式のデータ
        model (BaseModel): BaseModelを継承したクラス

    Returns:
        dict[str, BaseModel]: 引数のモデルに変換したdictオブジェクト
    """
    return {
        k: model(**v) for k, v in data.items() if len(v) > 0
    }


def conversion_list_to_model(data: list[dict], model: BaseModel) -> list[BaseModel]:
    """listをmodelの型に変換し返却します

    Args:
        data (list[dict]): json形式のデータ
        model (BaseModel): BaseModelを継承したクラス

    Returns:
        list[BaseModel]: 引数の型に変換したlistオブジェクト
    """
    return [
        model(**v) for v in data
    ]
