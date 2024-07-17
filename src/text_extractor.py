import pandas
import os
from datetime import datetime
from src.photo_scanner import PhotoScanner


class TextExtractor:
    """
    Class responsible for extracting text from photo and making it a dataframe
    """

    def __init__(self):
        self.scanner = PhotoScanner()
        self.dataframe_dict = {
            "products": [],
            "price": [],
            "category": []
        }

    def parse_subcategory(self, dataframe_column, text_to_parse):
        """
        Parse subcategory of a dataframe

        :param dataframe_column: column to put data into
        :param text_to_parse: text to clean and put in dataframe
        :return: NONE, writes data into pre-created variable
        """
        split_text = text_to_parse[text_to_parse.index(":") + 1:].split(",")
        # the first element is a column name, therefore skip
        split_text = [text for text in split_text if text != '']
        # First 3 characters is indices given by ChatGPT, which are not needed
        self.dataframe_dict[dataframe_column] = [text.strip() for text in split_text]

    def parse_text(self, request_text):
        """
        Parse text from text image

        :return: dictionary with parsed items
        """
        data = self.scanner.make_request(request_text)
        data = data["choices"][0]["message"]["content"]
        retries = 0
        while "products" not in data and "corresponding price" not in data and "corresponding category" not in data and retries < 3:
            print("[INFO] GPT didn't process request correctly, retrying...")
            data = self.scanner.make_request(request_text)
            retries += 1
        else:
            columns_indices = [data.index("products"),
                               data.index("corresponding price"),
                               data.index("corresponding category"),
                               -1]
        for idx, column in zip(range(len(columns_indices) - 1), self.dataframe_dict.keys()):
            if columns_indices[idx + 1] == -1:
                text = data[columns_indices[idx]:]
            else:
                text = data[columns_indices[idx]:columns_indices[idx + 1]]
            self.parse_subcategory(column, text)
        try:
            current_day = datetime.today().strftime("%Y-%m-%d")
            df = pandas.DataFrame.from_dict(self.dataframe_dict)
            path_reports = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
            df.to_excel(os.path.join(path_reports, current_day,
                                     f"{datetime.now().hour}_{datetime.now().minute}.xlsx"))
        except ValueError:
            print("[ERROR] Writing to the table went wrong. Try again.")
