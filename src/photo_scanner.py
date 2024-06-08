import cv2
import numpy as np
import os
import easyocr
from shutil import rmtree, move
from datetime import datetime


class FileProcessor:
    """
    Class made to work on files
    Paths generation, file lookup and R/W ops
    """

    def __init__(self,
                 force_path_generation=False,
                 path_to_photos="../photos/",
                 path_to_feed="../photo_feed/"):
        self.path_to_photos = path_to_photos
        self.path_to_feed = path_to_feed
        self.feed_not_empty_flag = len(os.listdir(self.path_to_feed)) > 0
        if self.feed_not_empty_flag:
            self.path_generator(force=force_path_generation)

    @staticmethod
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

    @staticmethod
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

    def read_from_feed(self):
        """
        Read latest file from feed.
        :return: NONE, latest file from feed is moved to a corresponding date location
        """
        if self.feed_not_empty_flag:
            print("[INFO] Reading from feed...")
            file_to_move = self.get_last_modified_path(self.path_to_feed)
            destination = self.get_last_modified_path(self.path_to_photos)
            move(file_to_move, destination)
        else:
            print("[INFO] Feed is empty. Nothing to read...")

    def get_file_name(self, path_to_dir=None):
        """

        :param path_to_dir: optional path to a desired directory.
        :return:
        """
        if not path_to_dir:
            return self.get_last_modified_path(self.get_last_modified_path(self.path_to_photos))
        else:
            return f"../photos/{path_to_dir}"


class PhotoScanner:
    """
    Class which is responsible for image processing and symbols recognition
    """

    def __init__(self):
        self.reader = easyocr.Reader(['pt'])
        self.file_worker = FileProcessor()

    def enhance_photo(self, path_to_photo):
        """
        Enhance symbols visibility on the photo

        :param path_to_photo: path to a photo that needs to be enhanced
        :return: NONE, enhanced photo written to a location
        """
        image = cv2.imread(path_to_photo)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        alpha = 1.5  # Contrast control (1.0-3.0)
        beta = 50  # Brightness control (0-100)
        adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        sharpened = cv2.filter2D(adjusted, -1, kernel)
        denoised = cv2.fastNlMeansDenoising(sharpened, None, 30, 7, 21)
        kernel = np.ones((2, 2), np.uint8)
        eroded = cv2.erode(denoised, kernel, iterations=1)
        cv2.imwrite(path_to_photo, eroded)

    def analyze_photo(self, enhance_photo=True):
        """
        Analyze photo with OCR and extract text

        :param enhance_photo: flag which tells whether to enhance a photo or no
        :return: array with an extracted text
        """
        self.file_worker.read_from_feed()
        path_to_photo = self.file_worker.get_file_name()
        if enhance_photo:
            self.enhance_photo(path_to_photo)
        print(f"[INFO] Scanning file {path_to_photo}")
        return self.reader.readtext(path_to_photo)


if __name__ == "__main__":
    scaner = PhotoScanner()
    result = scaner.analyze_photo()
    print(result)
