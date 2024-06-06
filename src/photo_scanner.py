import cv2
import os
import easyocr
from shutil import rmtree
from datetime import datetime


def path_generator(force=False):
    """
    Generate path to put bills to scan

    :param force: force overwrite of the folder flag
    :return: path is generated, NONE
    """
    current_day = datetime.today().strftime("%Y-%m-%d")
    path_to_create = os.path.exists(f"../photos/{current_day}")
    if not path_to_create:
        print("[INFO] Directory does not exist! Creating...")
        os.mkdir(f"../photos/{current_day}")
    elif path_to_create and force:
        print("[INFO] Force overwrite of the directory!")
        rmtree(f"../photos/{current_day}", ignore_errors=True)
        os.mkdir(f"../photos/{current_day}")
    else:
        print("[INFO] Directory already exists!")


def get_last_modified_path(path):
    """
    Get last modified file/folder
    :param path: path to walk through
    :return: path to the latest file in string format
    """
    folder_to_walk = os.listdir(path)
    max_date, max_path = -1, ""
    for file in folder_to_walk:
        cur_time = os.path.getmtime(os.path.join(path, file))
        if cur_time > max_date:
            max_date = cur_time
            max_path = file
    return os.path.join(path, max_path)


class PhotoScanner:
    def __init__(self, force_path_generation=False, path_to_photos="../photos/"):
        self.path_to_photos = path_to_photos
        path_generator(force=force_path_generation)
        self.reader = easyocr.Reader(['pt'])

    def get_file_name(self, path_to_dir=None):
        if not path_to_dir:
            return get_last_modified_path(get_last_modified_path(self.path_to_photos))
        else:
            return f"../photos/{path_to_dir}"

    def read_photo(self):
        path_to_photo = self.get_file_name()
        print(f"[INFO] Scanning file {path_to_photo}")
        return self.reader.readtext(path_to_photo)


if __name__ == "__main__":
    scaner = PhotoScanner()
    result = scaner.read_photo()
    print(result)
