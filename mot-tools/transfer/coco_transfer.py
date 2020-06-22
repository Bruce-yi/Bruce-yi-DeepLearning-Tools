# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function
# import _init_paths

# from opts import opts

import os
import json
import cv2
import collections

def xychange(a, w, h):
    ans = [(a[0]+a[2]/2)/w, (a[1]+a[3]/2)/h, a[2]/w, a[3]/h]
    return ans


prefix = '/home/yix/track_traindata/'

with open(prefix + 'coco2017/annotations/person_keypoints_train2017.json', 'r') as load_f:
    f = json.load(load_f)

 
length = len(f['annotations'])
# test = len(f['categories'])
# print(length, test)
dic = collections.defaultdict(list)
dic1 = collections.defaultdict(list)
for i in range(length):
    # print(f['annotations'][i])
    # print(f['categories'][i])
    # break
    dic['{0:012d}.jpg'.format(f['annotations'][i]['image_id'])].append(f['annotations'][i]['bbox'])
    dic1['{0:012d}.jpg'.format(f['annotations'][i]['image_id'])].append(f['annotations'][i]['keypoints'])
    # dic1['{0:012d}.jpg'.format(f['annotations'][i]['image_id'])].append(f['categories'][i]['skeleton'])
    # print(f['annotations'][i]['image_id'], f['annotations'][i]['bbox'], f['annotations'][i]['category_id'])
    # if f['annotations'][i]['image_id'] == 455677:
    #     print(f['annotations'][i]['keypoints'])
    #     break
    # print(dic1)
    # break

load_f.close()


t = 'key'

if t == 'bbox':
    with open("/mnt/track_traindata/coco2017/coco17.train",'w') as f:
        for item in dic:
            path = os.path.join(prefix, 'coco2017/images/', item)
            print(path)
            img = cv2.imread(path)
            h, w = img.shape[0], img.shape[1]
            f.write(os.path.join('coco2017/images/', item) +'\n')
            with open("/mnt/track_traindata/coco2017/labels_with_ids/{}.txt".format(item[:-4]),'w') as anno:
                for l in dic[item]:
                    anno.write('0 -1 ')
                    l = xychange(l, w, h)
                    for i in range(4):
                        anno.write(str(l[i]))
                        if i == 3:
                            anno.write('\n')
                        else:
                            anno.write(' ')
            anno.close()
    f.close()

else:
    for item in dic1:
        # path = os.path.join(prefix, 'coco2017/images/', item)
        # print(path)
        # img = cv2.imread(path)
        # h, w = img.shape[0], img.shape[1]
        with open(prefix + "coco2017/keypoints/{}.txt".format(item[:-4]),'w') as anno:
            for l in dic1[item]:
                # print(dic[item])
                for i in range(len(l)):
                    anno.write(str(l[i]))
                    if (i+1)%51 == 0:
                        anno.write('\n')
                    else:
                        anno.write(' ')
        anno.close()








# with open("C:\\downloads\\dataset\\gt.txt",'w') as f:
#     for item in dic:
#         f.write('0 -1 ')
#         for i in range(len(dic[item])):
#             f.write(str(dic[item][i]))
#             if i == len(dic[item])-1:
#                 f.write('\n')
#             else:
#                 f.write(' ')
# f.close()