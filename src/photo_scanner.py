import requests
import base64
import cv2
import numpy as np
from src.file_processor import FileProcessor


class PhotoScanner:
    """
    Class which is responsible for image processing and symbols recognition
    """

    def __init__(self, model="gpt-4o", enhance_photo=False):
        with open("gpt_key.txt") as gpt_key:
            self.api_key = gpt_key.readlines()[0]
        if len(self.api_key) == 0:
            print("[WARNING] Your key is empty!")
            raise ValueError
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.model = model
        self.file_worker = FileProcessor()
        self.do_enhance = enhance_photo

    @staticmethod
    def enhance_photo(path_to_photo):
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

    def image_to_64_base(self):
        """
        Format photo into base64 to pass to GPT

        :return base 64 photo
        """
        self.file_worker.read_from_feed()
        path_to_photo = self.file_worker.get_file_name()
        if self.do_enhance:
            self.enhance_photo(path_to_photo)
        with open(path_to_photo, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def make_request(self,
                     text_request,
                     max_tokens=300):
        """
        Make request to ChatGPT

        :param text_request: request about an image
        :param max_tokens: maximum output tokens
        :return:
        """
        print("---------------------")
        print("[INFO] Your request: ", text_request)
        print("---------------------")
        print("[INFO] Converting image to base 64...")
        image = self.image_to_64_base()
        payload = {
            "model": f"{self.model}",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text_request
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": max_tokens
        }
        print("[INFO] Passing request to Chat GPT")
        response = requests.post("https://api.openai.com/v1/chat/completions",
                                 headers=self.headers,
                                 json=payload)
        print("[INFO] Request processed!")
        return response.json()
