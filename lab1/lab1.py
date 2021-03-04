import cv2
import numpy as np


# Q1
def flip(img):
    height, width, _ = img.shape
    img_flip = np.zeros((height,width,3), np.uint8)

    for y in range(height):
        for x in range(width):
            img_flip[y][width-x-1] = img[y][x]
    return img_flip

img = cv2.imread('kobe.jpg')
img_flip = flip(img)
cv2.imwrite('kobe_flip.jpg',img_flip)
# cv2.imshow('img',img_flip)
# cv2.waitKey(0)