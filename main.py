from src.text_extractor import TextExtractor
from src.statistic_generator import StatisticGenerator

if __name__ == "__main__":
    extractor = TextExtractor()
    with open("gpt_request.txt") as request_txt:
        extractor.parse_text(" ".join(request_txt.readlines()))
    stat_gen = StatisticGenerator()
    stat_gen.graphical_report()
