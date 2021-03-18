import cv2
import numpy as np


def ConnectedComponent(frame):
    height, width = frame.shape
    keymap = np.zeros((height+2,width+2), np.uint32)


    newkey = 1
    sameKeyLog = {}

    for y in range(height):
        for x in range(width):
            pixel = frame[y][x]
            if(pixel == 0):
                keymap[y+1][x+1] = 0
                continue

            upkey = keymap[y][x+1]
            leftkey = keymap[y+1][x]

            if(upkey == 0 and leftkey == 0):
                key = newkey
                newkey += 1
            elif(upkey == 0):
                key = leftkey
            elif(leftkey == 0):
                key = upkey
            elif(leftkey == upkey):
                key = upkey
            else:
                key = upkey
                if(key not in sameKeyLog):
                    sameKeyLog[key] = [leftkey]
                else:
                    sameKeyLog[key].append(leftkey)

            keymap[y+1][x+1] = key

    for dictkey in list(sameKeyLog.keys()):
        if(dictkey not in sameKeyLog):
            continue
        value = sameKeyLog[dictkey]
        for mapkey in value:
            if(mapkey in sameKeyLog and dictkey in sameKeyLog):
                sameKeyLog[dictkey] += sameKeyLog[mapkey]
                del sameKeyLog[mapkey]

    keymap = keymap[1:height+1, 1:width+1]
    
    # print(sameKeyLog)
    for dictkey, value in sameKeyLog.items():
        for mapkey in value:
            keymap[keymap==mapkey] = dictkey

    return keymap

def selectConnectedComponent(keymap,T):
    areaDict = {}
    minmaxDict = {}

    height, width = keymap.shape

    for y in range(height):
        for x in range(width):
            pixel = keymap[y][x]

            if(pixel in areaDict):
                areaDict[pixel] += 1
            else:
                areaDict[pixel] = 1

            if(pixel in minmaxDict):
                value = minmaxDict[pixel]
                if(x < value["minX"]):
                    minmaxDict[pixel]["minX"] = x
                if(x > value["maxX"]):
                    minmaxDict[pixel]["maxX"] = x
                if(y < value["minY"]):
                    minmaxDict[pixel]["minY"] = y
                if(y > value["maxY"]):
                    minmaxDict[pixel]["maxY"] = y

            else:
                minmaxDict[pixel] = {"minX": x,
                                     "maxX": x,
                                     "minY": y,
                                     "maxY": y
                                    }
            

    del areaDict[0]
    del minmaxDict[0]

    for dictkey in list(areaDict.keys()):
        value = areaDict[dictkey]
        if(value < T):
            del areaDict[dictkey]
            del minmaxDict[dictkey]

    # print(areaDict)
    # print(minmaxDict)

    return minmaxDict



# arr = np.array([[0,1,0,1,0,0,0,1],
#                 [0,1,0,1,1,0,0,0],
#                 [1,1,0,0,1,0,0,0],
#                 [0,1,0,0,1,0,0,0],
#                 [0,1,1,1,1,1,1,0],
#                 [0,0,0,0,0,1,0,0],
#                 [0,0,0,0,0,1,0,0],
#                 [0,0,0,0,0,0,0,0]])

# keymap = ConnectedComponent(arr)
# print(keymap)
# selectConnectedComponent(keymap,0)






cap = cv2.VideoCapture('./inputs/vtest.avi')

backSub = cv2.createBackgroundSubtractorMOG2()

while True:
    ret, frame = cap.read()
    if frame is None:
        break

    fgmask = backSub.apply(frame)

    shadowval = backSub.getShadowValue()
    ret, nmask = cv2.threshold(fgmask, shadowval, 255, cv2.THRESH_BINARY)
    
    keymap = ConnectedComponent(nmask)
    pointDict = selectConnectedComponent(keymap,100)

    for key, value in pointDict.items():
        p1, p2 = (value['minX'],value['minY']), (value['maxX'], value['maxY'])
        cv2.rectangle(frame, p1, p2, (255, 0, 0),1)

    cv2.waitKey(1)

    cv2.imshow("frame", frame)






