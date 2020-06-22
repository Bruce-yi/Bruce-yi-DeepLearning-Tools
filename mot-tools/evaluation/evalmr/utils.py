# coding=utf-8
import os
import glob
import json

def IntersectBBox(bbox1, bbox2):
    intersect_bbox = []
    if bbox2[0] >= bbox1[2] or bbox2[2] <= bbox1[0] or bbox2[1] >= bbox1[3] or bbox2[3] <= bbox1[1]:
        # return [0, 0, 0, 0], if there is no intersection
        return intersect_bbox
    else:
        intersect_bbox.append([max(bbox1[0], bbox2[0]), max(bbox1[1], bbox2[1]),
                                min(bbox1[2], bbox2[2]), min(bbox1[3], bbox2[3])])
    return intersect_bbox


def JaccardOverlap(bbox1, bbox2):
    intersect_bbox = IntersectBBox(bbox1, bbox2)
    if len(intersect_bbox) == 0:
        return 0
    else:
        intersect_width = int(intersect_bbox[0][2]) - int(intersect_bbox[0][0])
        intersect_height = int(intersect_bbox[0][3]) - int(intersect_bbox[0][1])
        if intersect_width and intersect_height > 0:
            intersect_size = float(intersect_width) * float(intersect_height)
            bbox1_size = float(bbox1[3] - bbox1[1]) * float(bbox1[2] - bbox1[0])
            bbox2_size = float(bbox2[3] - bbox2[1]) * float(bbox2[2] - bbox2[0])
            return float(intersect_size / float(bbox1_size + bbox2_size - intersect_size))
        else:
            return 0


'''
GT
'''
def LoadIMG(path,final_dir):
    return sorted(glob.glob("%s/*.*" % os.path.join(path, final_dir)))


def LoadMOTGT(path,final_dir):
    gtfile = os.listdir(os.path.join(path, final_dir))
    if len(gtfile) != 1:
        print("error")
        return
    gt = os.path.join(path, final_dir, gtfile[0])
    with open(gt, 'r') as f:
        motgt =  f.readlines()
    return motgt


def LoadASS(path,final_dir):
    assfile = os.listdir(os.path.join(path, final_dir))
    if len(assfile) != 1:
        print("error")
        return
    ass = os.path.join(path, final_dir, assfile[0])
    with open(ass, 'r') as f:
        assrp = json.load(f)
    return assrp


def RestructMotRes(motgt):
    results_dict = {}
    for line in motgt:
        linelist = line.split(',')
        tlwh = tuple(map(float, linelist[2:6]))
        track_id = int(linelist[1])
        frame_id = int(linelist[0])
        results_dict.setdefault(frame_id, list())
        results_dict[frame_id].append((tlwh, track_id))
    return results_dict


def FindPID(tid,assrp):
    for key in assrp.keys():
        if tid in assrp[key]['track_ids']:
            return int(key)


def FusionIGA(imgs,rmotgt,assrp):
    results_dict = {}
    for img in imgs:
        img_index = img.split('/')[-1].split('.')[0]
        results_dict.setdefault(int(img_index), list())
        if int(img_index) in rmotgt.keys():
            pairBTs = rmotgt[int(img_index)]
            for pairBT in pairBTs:
                tlwh = pairBT[0]
                tid = pairBT[1]
                pid = FindPID(tid, assrp)
                results_dict[int(img_index)].append((tlwh, pid))
        else:
            results_dict[int(img_index)].append(' ')
    return results_dict


def LoadMRGT(path,sub_dir):
    imgs = LoadIMG(os.path.join(path,sub_dir), 'img1')
    motgt = LoadMOTGT(os.path.join(path,sub_dir), 'gt')
    rmotgt = RestructMotRes(motgt)
    assrp = LoadASS(os.path.join(path,sub_dir), 'ass')
    print("load final")
    # 需要按照img整理gt，避免FP
    MRGT = FusionIGA(imgs,rmotgt,assrp)
    return MRGT


def LoadMRGTs(path, select_camids = None):
    all_MRGT = {}
    list_dirs = os.listdir(path)
    for sub_dir in list_dirs:
        if select_camids:
            if sub_dir in select_camids:
                all_MRGT[sub_dir] = LoadMRGT(path,sub_dir)
            else:
                continue
        else:
            all_MRGT[sub_dir] = LoadMRGT(path,sub_dir)
    return all_MRGT


'''
PRE
'''
def LoadMOTPRE(path,sub_txt):
    pre = os.path.join(path, sub_txt)
    with open(pre, 'r') as f:
        motpre = f.readlines()
    return motpre


def LoadReIDPRE(path,sub_file):
    assfile = os.listdir(os.path.join(path, final_dir))
    if len(assfile) != 1:
        print("error")
        return
    ass = os.path.join(path, final_dir, assfile[0])
    with open(ass, 'r') as f:
        assrp = json.load(f)
    return assrp



def LoadPRE(path,sub_file):
    motpre = LoadMOTPRE(path,sub_file+'.txt')
    rmotpre = RestructMotRes(motpre)
    imgs = LoadIMG(os.path.join('/mnt/data/AIFWMR4-7500',sub_file), 'img1')
    print(motpre)


def LoadPREs(path, select_camids = None):
    all_MRPRE = {}
    list_files = os.listdir(path)
    for sub_file in list_files:
        sub_file = sub_file.split('.')[0]
        if select_camids:
            if sub_dir in select_camids:
                all_MRPRE[sub_file] = LoadPRE(path,sub_file)
            else:
                continue
        else:
            all_MRPRE[sub_file] = LoadPRE(path,sub_file)
    return all_MRPRE


if __name__ == "__main__":
    all_MRGT = LoadMRGTs('/mnt/data/AIFWMR4-7500')
    LoadPREs('exptemdata/predictions/aifw4_dlacoco30')