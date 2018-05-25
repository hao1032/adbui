# coding=utf-8

# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2


class Shape(object):
    def __init__(self):
        self.debug = False

    def midpoint(self, ptA, ptB):
        return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)
    
    def get_rectangle(self, image, width_range=None, height_range=None):
        # load the image, convert it to grayscale, and blur it slightly
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        base_img = image  # 为debug显示原图而保存
        height, width, channels = image.shape
        cv2.rectangle(image, (0, 0), (width, height), (255, 255, 255), 10)
        image[np.where((image != [255, 255, 255]).all(axis=2))] = [0, 0, 0]  # 将图片二值化
        kernel = np.ones((5, 5), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)  # 腐蚀，去噪点
        image = cv2.dilate(image, kernel, iterations=5)  # 膨胀，去除页面文字
        edged = cv2.Canny(image, 50, 100)

        # find contours in the edge map
        cnts = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        (cnts, _) = contours.sort_contours(cnts)

        # loop over the contours individually
        rectangles = []
        squares = []
        for cnt in cnts:
            x, y, w, h = cv2.boundingRect(cnt)

            if (w < width_range[0] or w > width_range[1]) and (h < height_range[0] or h > height_range[1]):
                continue
            cnt_len = cv2.arcLength(cnt, True)
            square = cv2.approxPolyDP(cnt, 0.02 * cnt_len, True)
            if len(square) == 4 and cv2.isContourConvex(square):
                rectangles.append((x, y, x + w, y + h, w, h))
                square = square.reshape(-1, 2)
                squares.append(square)
        if self.debug:
            cv2.drawContours(base_img, squares, -1, (0, 255, 0), 1)
            rate = 1000.0 / height
            base_img = cv2.resize(base_img, (int(width * rate), int(height * rate)), interpolation=cv2.INTER_CUBIC)
            cv2.imshow('image', base_img)
            cv2.waitKey(0)
        return list(set(rectangles))
        