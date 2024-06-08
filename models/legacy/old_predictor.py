import sys

import numpy as np
import cv2

from keras.models import load_model
from keras.optimizers import Adam, SGD

import matplotlib.pyplot as plt


class Predictor:

    def predict(self, path_to_image):
        # Filter image to black-white format
        original = cv2.imread(path_to_image)
        rgb = original
        lab = cv2.cvtColor(rgb, cv2.COLOR_BGR2Lab)

        average_a = np.array(list(x[1] for i in range(len(lab)) for x in lab[i])).mean()
        average_b = 0

        a = cv2.split(lab)[1]
        if average_a < 130:
            # print("many green or blue")
            rgb = cv2.threshold(a, 132, 255, cv2.THRESH_BINARY)[1]
            state = 1
        else:
            average_b = np.array(list(x[2] for i in range(len(lab)) for x in lab[i])).mean()
            if average_b < 135:
                # print("low on red")
                state = 2
                rgb = cv2.threshold(a, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]  #
            else:
                # print("high on red")
                state = 3
                rgb = cv2.threshold(cv2.split(rgb)[2], 227, 255, cv2.THRESH_BINARY)[1]
                rgb = cv2.bitwise_not(rgb)

        kernel_opening = np.ones((2, 2), np.uint8)
        kernel_closing = np.ones((12, 12), np.uint8)

        opening = cv2.morphologyEx(rgb, cv2.MORPH_OPEN, kernel_opening)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel_closing)

        result = cv2.medianBlur(closing, 5)
        result = cv2.resize(result, (32, 32))
        # print(result.shape)

        # Predict
        reconstructed_model = load_model("LeNet(1058, Adam).keras")
        prediction_values = reconstructed_model.predict(result[None, ...])  # Add dimensions if needed
        # print(prediction_values)

        # print(f"Predicted number is: {np.argmax(prediction_values)}")

        # _, axs = plt.subplots(1, 2, figsize=(12, 12))
        # axs = axs.flatten()
        # for img, ax in zip([(original, None, None), (result, plt.cm.gray_r, str(np.argmax(prediction_values)))], axs):
        #     ax.imshow(img[0], cmap=img[1])
        #     ax.text(15, 35, img[2], horizontalalignment='center', verticalalignment='center', fontsize=30)
        #     ax.grid(False)
        # plt.show()

        # topNmax = int(input("how many most possible answers you want to get:"))
        # print(f"Getting {topNmax} numbers based on CNN softmax results:{prediction_values.argsort()[0][-topNmax:][::-1]}")
        result = prediction_values.argsort()[0][-6:][::-1]
        print(result, path_to_image)
        return result

predictor = Predictor()

