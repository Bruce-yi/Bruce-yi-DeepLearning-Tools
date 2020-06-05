import cv2
import os, sys

prefix = sys.path[0]
# print(prefix)
img = cv2.imread(os.path.join(prefix, '000000516805.jpg'))
h, w = img.shape[0], img.shape[1]
print(img.shape)

form = 'ltwh'
ab = False

f = open(os.path.join(prefix, '000000516805.txt'))
for i in f.readlines():
    i = i.split()
    # print(float(i[2]))
    if ab:
        if form == 'ltrb': #左上角加右下角
            x = (int(float(i[2])), int(float(i[3])))
            y = (int(float(i[4])), int(float(i[5])))
        elif form == 'ltwh': #左上角加宽高
            x = (int(float(i[2])), int(float(i[3])))
            y = (x[0]+int(float(i[4])), x[1]+int(float(i[5])))
        else:  # 中心点+宽高
            c = (float(i[2]), float(i[3]))
            x = (int(c[0]-float(i[4])/2), int(c[1]-float(i[5])/2))
            y = (int(c[0]+float(i[4])/2), int(c[1]+float(i[5])/2))
    else:
        if form == 'ltrb': #左上角加右下角
            x = (int(c[0]-w*float(i[4])/2), int(c[1]-h*float(i[5])/2))
            y = (int(c[0]+w*float(i[4])/2), int(c[1]+h*float(i[5])/2))
        else:  # 中心点+宽高
            c = (w*float(i[2]), h*float(i[3]))
            x = (int(c[0]-w*float(i[4])/2), int(c[1]-h*float(i[5])/2))
            y = (int(c[0]+w*float(i[4])/2), int(c[1]+h*float(i[5])/2))
    # print(x, y)
    print(x, y)
    cv2.rectangle(img, x, y, (0,0,255), 2)

cv2.imshow('img', img)
cv2.waitKey(0)
