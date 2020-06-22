import shutil
import os
import argparse

def cp(src, dst):
    shutil.copy(src, dst)


def choose(src, dst):
    src_imgs = os.listdir(src)
    dst_imgs = os.listdir(dst)
    src_str_id = [x[:-4] for x in src_imgs]
    dst_str_id = [x[:-4] for x in dst_imgs]
    src_id = list(map(int, src_str_id))
    dst_id = list(map(int, dst_str_id))
    for i in range(len(src_id)):
        if not src_id[i] in dst_id:
            s = os.path.join(src, src_imgs[i])
            d = os.path.join(dst, '0'+src_imgs[i])
            cp(s, d)
            print(d)


if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument('--i', type=str)
    opt = parse.parse_args()
    i = opt.i
    src = '/mnt/interndata/2020_06_03/20' + i
    dst = '/mnt/interndata/2020_06_03/vis_results/20' + i + '/imgs'
    print(src, dst)
    choose(src, dst)
    out_path = '/mnt/interndata/2020_06_03/vis_results/20' + i + '/'
    out_folder = os.path.join(out_path, 'imgs')
    video_dir = os.path.join(out_path, 'finish.mp4')
    cmd_str = 'ffmpeg -f image2 -i {}/%06d.jpg -b 5000k -c:v mpeg4 {}'.format(out_folder, video_dir)
    os.system(cmd_str)