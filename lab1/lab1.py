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

print("Q1 running ...")
img = cv2.imread('kobe.jpg')
img_flip = flip(img)
cv2.imwrite('kobe_flip.jpg',img_flip)
print("Q1 finished\n")

# Q2
def rotateLeft90(img):
    height, width, _ = img.shape
    img_rotate = np.zeros((width,height,3), np.uint8)
    for y in range(height):
        for x in range(width):
            img_rotate[width-x-1][y] = img[y][x]
    return img_rotate

print("Q2 running ...")
img = cv2.imread('curry.jpg')
img_rotate = rotateLeft90(img)
cv2.imwrite('curry_rotate.jpg',img_rotate)
print("Q2 finished\n")

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

print("Q3 running ...")
img = cv2.imread('IU.png')
img_resize = interpolation_NearistNeighbor(img,3)
cv2.imwrite('IU_NNInterpolation.png',img_resize)
print("Q3 finished\n")


# Q4
def interpolation_Bilinear(img, scale):
    scale = int(scale)

    height, width, _ = img.shape
    height_resize = height*scale
    width_resize = width*scale

    img_resize = np.zeros((height_resize,width_resize,3), np.uint8)

    for y in range(height):
        for x in range(width):
            for scale_y in range(scale):
                for scale_x in range(scale):
                    Q12 = img[y][x]
                    Q11 = img[y+1][x] if y+1 < height else 0
                    Q22 = img[y][x+1] if x+1 < width else 0
                    Q21 = img[y+1][x+1] if (y+1 < height and x+1 < width) else 0
                    R1 = (scale-scale_x)/scale*Q11 + scale_x/scale*Q21
                    R2 = (scale-scale_x)/scale*Q12 + scale_x/scale*Q22
                    P = scale_y/scale*R1 + (scale-scale_y)/scale*R2

                    img_resize[y*scale+scale_y][x*scale+scale_x] = P

    return img_resize

print("Q4 running ...")
img = cv2.imread('IU.png')
img_resize = interpolation_Bilinear(img,3)
cv2.imwrite('IU_BilinearInterpolation.png',img_resize)
print("Q4 finished\n")
