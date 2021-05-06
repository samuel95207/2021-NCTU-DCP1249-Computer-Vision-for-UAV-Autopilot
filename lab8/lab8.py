import numpy as np
import cv2
import dlib


def drawBoxFromRect(img, rect, color=(0, 255, 0)):
    x, y, w, h = rect
    cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)


def calculateDistance(rect, targetHeight, m=1, b=0):
    x, y, w, h = rect
    # print(h)
    dis = targetHeight/h * m + b
    return dis


cap = cv2.VideoCapture(0)

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

detector = dlib.get_frontal_face_detector()


while True:
    _, img = cap.read()

    body_rects, weights = hog.detectMultiScale(img,
                                               winStride=(4, 4),
                                               scale=1.1,
                                               useMeanshiftGrouping=False)

    face_rects = detector(img, 0)

    for rect in body_rects:
        drawBoxFromRect(img, rect, color=(255, 0, 0))
        distance = calculateDistance(rect, 183, m=1064, b=-169)
        string = str(f"{distance} cm")
        cv2.putText(img, string, (rect[0], rect[1]), cv2.FONT_HERSHEY_DUPLEX,
                    0.5, (255, 0, 0), 1, cv2.LINE_AA)


    for rect_raw in face_rects:
        rect = [
            rect_raw.left(),
            rect_raw.top(),
            rect_raw.right() - rect_raw.left(),
            rect_raw.bottom() - rect_raw.top()
        ]

        drawBoxFromRect(img, rect, color=(0, 0, 255))
        distance = calculateDistance(rect, 30, m=464.88, b=-14.343)
        string = str(f"{distance} cm")
        cv2.putText(img, string, (rect[0], rect[1]), cv2.FONT_HERSHEY_DUPLEX,
                    0.5, (0, 0, 255), 1, cv2.LINE_AA)
        # print(rect[3])

    cv2.imshow('img_original', img)
    cv2.waitKey(10)
