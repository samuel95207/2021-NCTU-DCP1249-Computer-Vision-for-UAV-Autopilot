from darkflow.net.build import TFNet
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os 

threshold = 0.5
options = {"pbLoad": "../result/0508_carna_2/yolov2-tiny-voc-lab9.pb",
            "threshold": threshold,
           "metaLoad": "../result/0508_carna_2/yolov2-tiny-voc-lab9.meta" 
           }
eval_path = 'test_img/'         

tfnet = TFNet(options)



def boxing(original_img, predictions, thre):
    newImage = np.copy(original_img)

    for result in predictions:
        top_x = result['topleft']['x']
        top_y = result['topleft']['y']

        btm_x = result['bottomright']['x']
        btm_y = result['bottomright']['y']

        confidence = result['confidence']
        label = result['label'] + " " + str(round(confidence, 2))

        if confidence > thre:
            newImage = cv2.putText(newImage, label, (top_x, top_y-5), cv2.FONT_HERSHEY_SIMPLEX ,1, (0, 255, 0), 1, cv2.LINE_AA)
            newImage = cv2.rectangle(newImage, (top_x, top_y), (btm_x, btm_y), (255,0,0), 3)
            
            
    return newImage



# images_ls = [f for f in os.listdir(eval_path) if f.endswith('.jpg')]

# for img in images_ls:
#     path = eval_path+img
#     imgcv = cv2.imread(path)
#     result = tfnet.return_predict(imgcv)

#     if len(result)!=0:
#         cv2.imshow("result", boxing(imgcv, result, threshold))
#         cv2.waitKey(0)
#     else:
#         print("Nothing detected")


cap = cv2.VideoCapture('../demo_video/demo.wmv')

while True:
    ret, imgcv = cap.read()
    result = tfnet.return_predict(imgcv)

    if(not ret):
        print("Video end")
        break

    if len(result)!=0:
        cv2.imshow("result", boxing(imgcv, result, threshold))
    else:
        cv2.imshow("result", imgcv)
        print("Nothing detected")

    cv2.waitKey(10)



