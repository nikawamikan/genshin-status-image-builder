from ordered_set import OrderedSet
import os
import glob

URL_CACHE = OrderedSet(glob.glob('build_images/*.jpg'))
MAX_CACHE_SIZE = 1000


def check_cache_exists(file_path: str) -> bool:
    if file_path in URL_CACHE:
        return True
    else:
        return False


def cache_append(file_path: str):
    URL_CACHE.add(file_path)
    if len(URL_CACHE) > MAX_CACHE_SIZE:
        image_path = URL_CACHE.pop(0)
        try:
            os.remove(image_path)
        except:
            pass
