import cv2
import numpy as np


def merge_image(img, cover_img):
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if(not cover_img[i][j].all() == 0):
                img[i][j] = cover_img[i][j]

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

def warp(newimg, srcimg, M):

    srcimg = interpolation_NearistNeighbor(srcimg,2)
    h, w, _ = srcimg.shape

    for y in range(h):
        for x in range(w):
            a, b, _ = tuple(M.dot((x, y, 1)))
            times = 1/_
            newimg[int(times*b), int(times*a), :] = srcimg[y, x, :]


camera = 1

cap = cv2.VideoCapture(camera)
_, src_img = cap.read()


dst_img = cv2.imread("./warp.jpg")
src_img = interpolation_NearistNeighbor(src_img,2)


src_size = src_img.shape[0:2]
dst_size = dst_img.shape[0:2]

src_corner = np.float32([
                         [0, 0],
                         [src_size[1]-1, 0],
                         [0, src_size[0]-1],
                         [src_size[1]-1, src_size[0]-1],
                        ])

dst_corner = np.float32([
                    [241 ,203],
                    [463 ,247],
                    [260 ,631],
                    [432 ,762]])

# compute the transform matrix M
M = cv2.getPerspectiveTransform(src_corner, dst_corner)


# Get Images
while True:
    cap = cv2.VideoCapture(camera)
    _, src_img = cap.read()

    # print("src_size: ",src_size)
    # print("dst_size: ",dst_size)

    #  transform
    warp(dst_img,src_img,M)

    # merge_image(dst_img,warped_img)
    cv2.imshow('img', dst_img)
    cv2.waitKey(1)
