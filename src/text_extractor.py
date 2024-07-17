import pandas
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
        split_text = text_to_parse[text_to_parse.index(":")+1:].split(",")
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
            df.to_excel(f"../reports/{current_day}/{datetime.now().hour}_{datetime.now().minute}.xlsx")
        except ValueError:
            print("[ERROR] Writing to the table went wrong. Try again.")
