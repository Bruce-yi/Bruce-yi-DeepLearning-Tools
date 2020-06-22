import os
import argparse


def transfer(opt):
    root = opt.data_path
    diff = opt.diff
    seqs = []
    for _ in os.listdir(root):
        _ = os.path.join(root, _)
        if os.path.isdir(_):
            seqs.append(_)
    for seq in seqs:
        # img transfer
        if opt.trans_img:
            img_folder = os.path.join(root, seq, 'img1')
            imgs = os.listdir(img_folder)
            for img in imgs:
                fid = int(img[:-4])
                new_fid = fid - diff
                new_img = '{0:06d}.jpg'.format(new_fid)
                img = os.path.join(img_folder, img)
                new_img = os.path.join(img_folder, new_img)
                os.rename(img, new_img)
                print(img, new_img)
            

        # gt transfer
        if opt.trans_gt:
            gt_folder = os.path.join(root, seq, 'gt')
            gts = os.listdir(gt_folder)
            for gt in gts:
                new_gt = os.path.join(gt_folder, 'new'+gt)
                gt = os.path.join(gt_folder, gt)
                # print(gt, new_gt)
                with open(gt, 'r') as f:
                    with open(new_gt, 'w') as f_new:
                        for line in f.readlines():
                            fid = int(line.split(',')[0])
                            if opt.crop_gt:
                                if fid < 1200 or fid > 8699:
                                    continue
                            index = line.index(',')
                            new_fid = fid - diff
                            new_line = str(new_fid) + line[index:]
                            f_new.write(new_line)
                    f_new.close()
                f.close()
                print(gt)
                # os.replace(new_gt, gt)


if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument('--data_path', default='/mnt/interndata/AIFWMOT4-7500')
    parse.add_argument('--diff', default=1199, type=int, help='old id - new id')
    parse.add_argument('--trans_img',action='store_true',  help='set True while transfer img')
    parse.add_argument('--trans_gt', action='store_true', help='set True while transfer gt')
    parse.add_argument('--crop_gt', action='store_true', help='crop gt file from 12000 to 7500')
    opt = parse.parse_args()
    transfer(opt)