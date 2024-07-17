from src.text_extractor import TextExtractor
from src.statistic_generator import StatisticGenerator


if __name__ == "__main__":
    extractor = TextExtractor()
    with open("gpt_request.txt") as request_txt:
        extractor.parse_text(request_txt)
    stat_gen = StatisticGenerator()
    stat_gen.graphical_report()