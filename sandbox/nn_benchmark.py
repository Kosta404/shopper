import cv2
import numpy as np
import argparse
import pytesseract
import easyocr
from doctr.models import ocr_predictor
from doctr.io import DocumentFile


def enhance_photo(image):
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
    cv2.imwrite("../benchmark_tests/img_enhanced.jpg", eroded)


def analyze_with_ocr(path_to_photo):
    reader = easyocr.Reader(['pt'])
    extracted_text = reader.readtext(path_to_photo)
    with open("../benchmark_tests/results/easyocr_output.txt", "w") as output_file:
        output_file.write(extracted_text)


def analyze_with_tesseract(path_to_image):
    extracted_text = pytesseract.image_to_string(path_to_image, config="-l por")
    with open("../benchmark_tests/results/tesseract_output.txt", "w") as output_file:
        output_file.write(extracted_text)


def analyze_with_doct(path_to_image):
    reader = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
    file = DocumentFile.from_images(path_to_image)
    extracted_text = reader(file)
    with open("../benchmark_tests/results/doctr_output.txt", "w") as output_file:
        output_file.write(extracted_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-nn", "--network", type=str, default="eocr")
    parser.add_argument("-e", "--enhance", type=str, default="n")
    args = parser.parse_args()

    base_path = "../benchmark_tests/photo_2024-06-06_21-06-17.jpg"
    input_image = cv2.imread(base_path)
    if args.enhance == "y":
        enhance_photo(input_image)

    # Test EOcr
    # Result - questionable
    if args.network == "eocr" and args.enhance == "y":
        analyze_with_ocr("../benchmark_tests/img_enhanced.jpg")
    elif args.network == "eocr":
        analyze_with_ocr("../benchmark_tests/photo_2024-06-06_21-06-17.jpg")

    # Test tesseract
    # Result - already workable
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    if args.network == "tes" and args.enhance == "y":
        analyze_with_tesseract("../benchmark_tests/img_enhanced.jpg")
    elif args.network == "tes":
        analyze_with_tesseract("../benchmark_tests/photo_2024-06-06_21-06-17.jpg")

    # Test doctr
    # Grasped the text well, struggled with numbers
    # Output is very chaotic
    if args.network == "doctr" and args.enhance == "y":
        analyze_with_doct("../benchmark_tests/img_enhanced.jpg")
    elif args.network == "doctr":
        analyze_with_doct("../benchmark_tests/photo_2024-06-06_21-06-17.jpg")
