import cv2
import os, sys
import argparse
import numpy as np
import collections

def mkdir_if_missing(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def drawline(img, pt1, pt2, color, thickness=1, style='dotted', gap=10):
    dist =((pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2)**.5
    pts= []
    for i in np.arange(0,dist,gap):
        r = i/dist
        x = int((pt1[0]*(1-r)+pt2[0]*r)+.5)
        y = int((pt1[1]*(1-r)+pt2[1]*r)+.5)
        p = (x,y)
        pts.append(p)

    if style =='dotted':
        for p in pts:
            cv2.circle(img, p, thickness, color, -1)
    else:
        s = pts[0]
        e = pts[0]
        i = 0
        for p in pts:
            s = e
            e = p
            if i%2==1:
                cv2.line(img, s, e, color, thickness)
            i += 1

def drawpoly(img, pts, color, thickness=1, style='dotted'):
    s = pts[0]
    e = pts[0]
    pts.append(pts.pop(0))
    for p in pts:
        s = e
        e = p
        drawline(img, s, e, color, thickness, style)

def drawrect(img, pt1, pt2, color, thickness=1, style='dotted'):
    pts = [pt1, (pt2[0], pt1[1]), pt2, (pt1[0], pt2[1])] 
    drawpoly(img, pts, color, thickness, style)


def get_color(idx):
    idx = idx * 3
    color = ((37 * idx) % 255, (17 * idx) % 255, (29 * idx) % 255)

    return color


def draw_bbox(img_path, anno, opts, count):
    img = cv2.imread(img_path)
    h, w = img.shape[0], img.shape[1]
    # print('img shape: ', img.shape)
            
    ab = int(anno[0][1]) > 1
    form = opts.gt_format

    for i in anno:
        # print(float(i[2]))
        # print(i)
        if ab:
            if form == 'ltrb': #左上角加右下角
                x = (int(float(i[1])), int(float(i[2])))
                y = (int(float(i[3])), int(float(i[4])))
            elif form == 'ltwh': #左上角加宽高
                x = (int(float(i[1])), int(float(i[2])))
                y = (x[0]+int(float(i[3])), x[1]+int(float(i[4])))
            else:  # 中心点+宽高
                c = (float(i[1]), float(i[2]))
                x = (int(c[0]-float(i[3])/2), int(c[1]-float(i[4])/2))
                y = (int(c[0]+float(i[3])/2), int(c[1]+float(i[4])/2))
        else:
            if form == 'ltrb': #左上角加右下角
                x = (int(w*float(i[1])), int(h*float(i[2])))
                y = (int(w*float(i[3])), int(h*float(i[4])))
            else:  # 中心点+宽高
                c = (w*float(i[1]), h*float(i[2]))
                x = (int(c[0]-w*float(i[3])/2), int(c[1]-h*float(i[4])/2))
                y = (int(c[0]+w*float(i[3])/2), int(c[1]+h*float(i[4])/2))
        obj_id = int(i[0])
        color = get_color(abs(obj_id))
        if i[5] == '1':
            cv2.rectangle(img, x, y, color=color, thickness=2)
        else:
            drawrect(img, x, y, color, 2 ,'dotted')

    # cv2.imshow('img', img)
    # cv2.waitKey(0)
    out_folder = os.path.join(opts.out_path, 'imgs')
    mkdir_if_missing(out_folder)
    finished_img_path = os.path.join(out_folder, '{0:06d}.jpg'.format(count))
    print(finished_img_path)
    cv2.imwrite(finished_img_path, img)
    return finished_img_path


def visual(opts):
    if opts.format == 'movie':
        #TODO 
        print('split movie into pictures')
    
    print('loading annotations')
    dic = collections.defaultdict(list)
    f = open(opts.gt_path)
    for i in f.readlines():
        i = i.rstrip('\n')
        i = i.split(',')
        if i[7] in ['1', '2', '7']:
            dic[i[0]].append(i[1:7])
    f.close()

    # print(dic['1'])    
    print('loading imgs')
    imgs = os.listdir(opts.path)
    imgs = sorted(imgs)
    print('start visualization')
    count = 1
    finished_imgs = []
    for img in imgs:
        if img.endswith('jpg') or img.endswith('png'):
            img_path = os.path.join(opts.path, img)
            anno = dic[str(count)]
            finished_img_path = draw_bbox(img_path, anno, opts, count)
            finished_imgs.append(finished_img_path)
            print(img_path, '    done!')
            count += 1
    
    
    if opts.out_format == 'movie':
        video_dir = os.path.join(opts.out_path, 'output.avi')
        fps = 30
        img = cv2.imread(finished_imgs[0])
        h, w = img.shape[0], img.shape[1]
        img_size = (w, h)
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        video_writer = cv2.VideoWriter(video_dir, fourcc, fps, img_size)
        
        for i in range(1, len(finished_imgs)):
            frame = cv2.imread(finished_imgs[i])
            video_writer.write(frame)
            # cv2.imshow('rr', frame)
            # cv2.waitKey(20)
        
        
        video_writer.release()

            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--format', default='pic', type=str, help='the format of input, picture or movie')
    parser.add_argument('--path', default='/home/yix/track_traindata/MOT16/train/MOT16-04/img1', help='the path of input pictures or movies')
    parser.add_argument('--gt_path', default='/home/yix/track_traindata/MOT16/train/MOT16-04/gt/gt.txt', help='the path of input groundtruth')
    parser.add_argument('--gt_format', default='ltwh', choices=['ltrb', 'ltwh', 'cwh'], 
                        help='the groundtruth format, like ltrb: left top corner and right bottom corner')
    parser.add_argument('--out_format', default='movie', type=str, help='the format of output, picture or movie')
    parser.add_argument('--out_path', default='./results/MOT16-04/', help='the output path')
    opts = parser.parse_args()
    mkdir_if_missing(opts.out_path)
    visual(opts)