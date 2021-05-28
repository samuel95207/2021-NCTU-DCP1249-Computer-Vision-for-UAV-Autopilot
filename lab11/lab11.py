import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import time

def featureMatching(img1, img2, outFilename, detector):

    # Timer
    detectorStartTime = time.time_ns() // 1_000_000 

    # find the keypoints and descriptors with detector
    kp1, des1 = detector.detectAndCompute(img1, None)
    kp2, des2 = detector.detectAndCompute(img2, None)

    detectorEndTime = time.time_ns() // 1_000_000 

    des1 = np.float32(des1)
    des2 = np.float32(des2)

    # Timer
    matchingStartTime = time.time_ns() // 1_000_000 

    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50) 
    
    # Create FLANN matcher  
    flann = cv.FlannBasedMatcher(index_params, search_params)

    # Match descriptors
    matches = flann.knnMatch(des1, des2, k=2)

    matchingEndTime = time.time_ns() // 1_000_000 

    # Need to draw only good matches, so create a mask
    matchesMask = [[0, 0] for i in range(len(matches))]

    # Draw the result
    for i, (m, n) in enumerate(matches):
        if m.distance < 0.7*n.distance:
            matchesMask[i] = [1, 0]

    draw_params = dict(matchColor=(0, 255, 0),
                       singlePointColor=(255, 0, 0),
                       matchesMask=matchesMask,
                       flags=cv.DrawMatchesFlags_DEFAULT)
    img_out = cv.drawMatchesKnn(img1, kp1, img2, kp2,
                                matches, None, **draw_params)

    cv.imwrite(outFilename, img_out)

    print(f'Detect time = {detectorEndTime - detectorStartTime} ms')
    print(f'Matching time = {matchingEndTime - matchingStartTime} ms')
    print()



# Load images
img_boxes = cv.imread('./images/boxes.jpg',
                      cv.IMREAD_GRAYSCALE)    # queryImage
img_z370 = cv.imread('./images/Z370.jpg', cv.IMREAD_GRAYSCALE)     # trainImage
img_rtx3080 = cv.imread('./images/RTX3080.jpg',
                        cv.IMREAD_GRAYSCALE)     # trainImage


# Initiate detectors
sift = cv.xfeatures2d.SIFT_create()
surf = cv.xfeatures2d.SURF_create()
orb = cv.ORB_create()


print("SIFT: ")
featureMatching(img_z370, img_boxes, "output/sift_z370_out.jpg", sift)
featureMatching(img_rtx3080, img_boxes, "output/sift_rtx3080_out.jpg", sift)

print("SURF: ")
featureMatching(img_z370, img_boxes, "output/surf_z370_out.jpg", surf)
featureMatching(img_rtx3080, img_boxes, "output/surf_rtx3080_out.jpg", surf)

print("ORB: ")
featureMatching(img_z370, img_boxes, "output/orb_z370_out.jpg", orb)
featureMatching(img_rtx3080, img_boxes, "output/orb_rtx3080_out.jpg", orb)
