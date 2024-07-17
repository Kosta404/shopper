import pandas
from datetime import datetime
import matplotlib.pyplot as plt
from src.file_processor import FileProcessor


class StatisticGenerator:
    def __init__(self):
        self.file_worker = FileProcessor()

    def reports_scanner(self):
        """
        Scan all the report files and sum + group by category

        :return: grouped dataframe
        """
        report_files = self.file_worker.get_report_files()
        products_dataframes = [pandas.read_excel(file) for file in report_files]
        final_dataframe = pandas.concat(products_dataframes)
        final_dataframe = final_dataframe[["price", "category"]].groupby("category", as_index=False).sum()
        return final_dataframe

    def graphical_report(self, display=False):
        """
        Display or save a monthly report

        :param display: if False - save the file
        :return: NONE
        """
        final_dataframe = self.reports_scanner()
        plt.figure(figsize=(10, 5))
        plt.bar(final_dataframe["category"], final_dataframe["price"], width=0.5, color="orange")
        plt.title("Monthly spending report")
        plt.xlabel("Category")
        plt.ylabel("Spending")
        for idx, value in enumerate(final_dataframe["price"]):
            plt.text(final_dataframe["category"][idx], value, str(value), ha="center", va="bottom")
        if display:
            plt.grid(True)
            plt.show()
        else:
            plt.savefig(f"../graphical_reports/{datetime.now().year}_{datetime.now().month}.png")
