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


# Q2
def rotateLeft90(img):
    height, width, _ = img.shape
    img_rotate = np.zeros((width,height,3), np.uint8)
    for y in range(height):
        for x in range(width):
            img_rotate[width-x-1][y] = img[y][x]
    return img_rotate

img = cv2.imread('curry.jpg')
img_rotate = rotateLeft90(img)
cv2.imwrite('curry_rotate.jpg',img_rotate)


# Q3
def interpolation_NearistNeighbor(img, scale):
    scale = int(scale)

    height, width, _ = img.shape
    height_resize = height*scale
    width_resize = width*scale

    img_resize = np.zeros((height_resize,width_resize,3), np.uint8)

    for y in range(height):
        for x in range(width):
            img_resize[scale*y:scale*(y+1),scale*x:scale*(x+1)] = img[y][x]

    return img_resize

img = cv2.imread('IU.png')
img_resize = interpolation_NearistNeighbor(img,3)
cv2.imwrite('IU_NNInterpolation.png',img_resize)


# Q4

# cv2.imshow('img',img_flip)
# cv2.waitKey(0)