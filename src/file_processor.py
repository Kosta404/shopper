import os
from shutil import rmtree, move
from datetime import datetime


class FileProcessor:
    """
    Class made to work on files
    Paths generation, file lookup and R/W ops
    """

    def __init__(self,
                 force_path_generation=False,
                 path_to_photos="photos",
                 path_to_feed="photo_feed",
                 path_to_reports="reports"):
        self.abs_path = os.path.dirname(os.path.abspath(__file__))
        self.path_to_photos = os.path.join(self.abs_path, "..", path_to_photos)
        self.path_to_feed = os.path.join(self.abs_path, "..", path_to_feed)
        self.path_to_reports = os.path.join(self.abs_path, "..", path_to_reports)
        self.feed_not_empty_flag = len(os.listdir(self.path_to_feed)) > 1
        current_day = datetime.today().strftime("%Y-%m-%d")
        if self.feed_not_empty_flag:
            self.path_generator(os.path.join(self.path_to_photos, current_day), force=force_path_generation)
        self.path_generator(os.path.join(self.path_to_reports, current_day), force=force_path_generation)

    def path_generator(self, path_to_generate, force=False):
        """
        Generate path to put bills to scan

        :param path_to_generate: what path should be generated
        :param force: force overwrite of the folder flag
        :return: path is generated, NONE
        """
        path_to_create = os.path.exists(os.path.join(self.path_to_photos, path_to_generate))
        if not path_to_create:
            print("[INFO] Directory does not exist! Creating...")
            os.mkdir(path_to_generate)
        elif path_to_create and force:
            print("[INFO] Force overwrite of the directory!")
            rmtree(path_to_generate, ignore_errors=True)
            os.mkdir(path_to_generate)
        else:
            print(f"[INFO] Directory {path_to_generate} already exists!")

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
        Get last modified file in the directory

        :param path_to_dir: optional path to a desired directory.
        :return: latest file
        """
        if not path_to_dir:
            return self.get_last_modified_path(self.get_last_modified_path(self.path_to_photos))
        else:
            return f"../photos/{path_to_dir}"

    def get_report_files(self, year=datetime.now().year, month=datetime.now().month):
        """
        Get all the report files for a desired month

        :param year: year of the report
        :param month: month of the report
        :return: all report files for a desired year + date
        """
        current_month_reports = []
        # get all the paths to the files
        for root, dirs, files in os.walk(self.path_to_reports):
            for filename in files:
                split_folder = root.split("\\")[-1].split("-")
                # 0 element is always a year in split folder name
                # 1 element is always month in split folder name
                # f.e. 2024-05-25 = ['2024', '05', '25']
                try:
                    if int(split_folder[0]) == year and int(split_folder[1]) == month:
                        current_month_reports.append(os.path.join(root, filename))
                except Exception:
                    pass
        return current_month_reports
