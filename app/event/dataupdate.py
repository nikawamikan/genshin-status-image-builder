from watchdog.events import PatternMatchingEventHandler, FileSystemEvent
from watchdog.observers.polling import PollingObserver
import repository.util_repository as util_repository
import service.character_position_service as position_service
import asyncio


class FileModifiedHandler(PatternMatchingEventHandler):
    def __init__(self, observation_file_hash_function: dict[str, any]):
        patterns = [k for k in observation_file_hash_function.keys()]
        self.function_map = observation_file_hash_function
        case_sensitive = True  # 大文字小文字の区別
        super().__init__(patterns=patterns, case_sensitive=case_sensitive)

    def on_modified(self, event: FileSystemEvent):
        file_name = event.src_path.split("/")[-1]
        self.function_map[file_name]()
        print(f"model update done -> {file_name}")


def json_update_observation_start():
    observation_files = {
        "artifacts.json": util_repository.update_artfact_model_dict,
        "weapons.json": util_repository.update_weapon_model_dict,
        "namecards.json": util_repository.update_namecard_model_dict,
        "names.json": util_repository.update_namehash_model_dict,
        "characters.json": util_repository.update_character_model_dict,
        "statusnames.json": util_repository.update_status_namehash_model_dict,
        "positions.json": position_service.position_update,
    }
    dir_path = "data"
    recursive = True  # フォルダだった場合それ以下も探索する
    observer = PollingObserver()
    observer.schedule(
        FileModifiedHandler(observation_files),
        dir_path,
        recursive
    )
    observer.start()  # バックグラウンドで監視開始
