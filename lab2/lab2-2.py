import cv2
import numpy as np

def otsuThresholding(img):
    height, width = img.shape
    img_otsu = np.zeros((height,width,3), np.uint8)

    intensity_arr = np.zeros((256), np.uint32)
    intensity_acc_arr = np.zeros((256), np.uint32)

    for y in range(height):
        for x in range(width):
            intensity_arr[img[y][x]] += 1


    nB = 0
    nO = width*height
    uB = 0
    uO = 0

    for i in range(256):
        uO += i * intensity_arr[i]
    uO /= width*height


    sig2Between = np.zeros((256), float)

    for i in range(255):
        sig2Between[i] = nB*nO*(uB-uO)**2

        nT = intensity_arr[i]
        nB_new = nB + nT
        nO_new = nO - nT
        uB_new = (uB*nB+nT*i)/nB_new
        uO_new = (uO*nO-nT*i)/nO_new

        nB = nB_new
        nO = nO_new
        uB = uB_new
        uO = uO_new

    threshold = np.argmax(sig2Between)-1

    print(f"threshold: {threshold} ")

    for y in range(height):
        for x in range(width):
            img_otsu[y][x] = 255 if img[y][x] >= threshold else 0

    return img_otsu


print("Q2 running ...")
img = cv2.imread('input.jpg',0)
img_otsu = otsuThresholding(img)
cv2.imwrite('Q2.jpg',img_otsu)
print("Q2 finished\n")