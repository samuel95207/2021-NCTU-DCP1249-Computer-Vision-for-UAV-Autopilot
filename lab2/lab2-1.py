import cv2
import numpy as np

# Q1
def histogram(img):
    height, width = img.shape
    img_histogram = np.zeros((height,width,3), np.uint8)

    intensity_arr = np.zeros((256), np.uint32)
    intensity_acc_arr = np.zeros((256), np.uint32)

    for y in range(height):
        for x in range(width):
            intensity_arr[img[y][x]] += 1
    
    previous = 0
    for index, intensity in enumerate(intensity_arr):
        intensity_acc_arr[index] = (intensity + previous)
        previous = intensity_acc_arr[index]

    intensity_acc_arr_percent = intensity_acc_arr * (1/(height*width))
    output_value = intensity_acc_arr_percent*255
    quantized = output_value.astype(int)


    for y in range(height):
        for x in range(width):
            img_histogram[y][x] = quantized[img[y][x]]

    return img_histogram


print("Q1 running ...")
img = cv2.imread('./inputs/mj.tif',0)
img_histogram = histogram(img)
cv2.imwrite('./outputs/Q1.jpg',img_histogram)
print("Q1 finished\n")
