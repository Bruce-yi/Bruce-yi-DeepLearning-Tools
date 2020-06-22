'''
script of offline draw
track reid 
facedet pesdet
facelandmark pespose  
'''

import argparse
import _init_paths
import cv2
import numpy as np
import json
import os.path as osp
import os
import glob
import vis


def load_tpid(assoc_tpid):
    with open(assoc_tpid, "r") as f:
            tpid_contxt = json.load(f)
    return tpid_contxt


def asset_fusion(fusion_images, fusion_frame):
    if "201" not in fusion_images.keys() or "201" not in fusion_frame.keys() or fusion_images["201"] is None:
        return False
    elif "202" not in fusion_images.keys() or "202" not in fusion_frame.keys() or fusion_images["202"] is None:
        return False
    elif "203" not in fusion_images.keys() or "203" not in fusion_frame.keys() or fusion_images["203"] is None:
        return False
    elif "204" not in fusion_images.keys() or "204" not in fusion_frame.keys() or fusion_images["204"] is None:
        return False
    elif not fusion_frame["201"] == fusion_frame["202"] == fusion_frame["203"] == fusion_frame["204"]:
        return False
    else:
        return True


def load_pose(bin_path):
    pose_list = []
    pose_frame = {}
    bin_json = sorted(glob.glob(bin_path+"/*.bin"))
    for i, mes in enumerate(bin_json):
        binFile = open(mes, "rb")
        bytes_context = binFile.read()
        str_context = str(bytes_context, "utf-8")
        json_context = json.loads(str_context)
        pose_frame[json_context['camera']] = json_context
        if (i+1) % 4 == 0:
            pose_list.append(pose_frame.copy())
            pose_frame.clear()
    return pose_list


def demo_offlinedraw(args):
    pose_result = load_pose(args.pose_offline_path)
    face_result = load_face(args.face_offline_path)
    tpid = load_tpid(args.assoc_tpid)
    bin_json = sorted(glob.glob(osp.join(args.track_offline_path, "*.bin")))
    pid_list = []
    fusion_images = {}
    fusion_frame = {}
    for i, mes in enumerate(bin_json):
        binFile = open(mes, "rb")
        bytes_context = binFile.read()
        str_context = str(bytes_context, "utf-8")
        json_context = json.loads(str_context)
        camera = json_context["camera"]
        image = cv2.imread(json_context["image"])
        objects = json_context["objects"]
        frame_id = json_context["frame_id"]
        if objects:
            tlwhs = []
            obj_tids = []
            #[str]
            obj_str_pids = []
            #[int]
            obj_index_pids = []
            for obj in objects:
                tlwhs.append(obj["box_tlwh"])
                obj_tids.append(obj["track_id"])
                if str(obj["track_id"]) not in tpid[camera].keys():
                    obj_str_pids.append("None")
                    obj_index_pids.append(-1)
                else:
                    strname = tpid[camera][str(obj["track_id"])]["name"]
                    if strname not in pid_list:
                        pid_list.append(strname)
                    obj_str_pids.append(strname)
                    obj_index_pids.append(pid_list.index(strname))
            image = vis.plot_trackreid(image, tlwhs, obj_tids, obj_str_pids, obj_index_pids)
        image = vis.plot_pose(image,pose_result[frame_id][camera])
        txtflie = face_result[camera][frame_id]
        all_det_result = analyse_txt( os.path.join(args.face_offline_path , camera , txtflie))
        image = vis.plot_face(image,all_det_result, xywh = True)
        fusion_images[camera] = image
        fusion_frame[camera] = frame_id
        if asset_fusion(fusion_images,fusion_frame):
            fusion_im = vis.polt_vfusion_2(fusion_images)
            save_dir_fusion = osp.join(args.output_path, args.fusion_folder)
            if not osp.isdir(save_dir_fusion):
                os.makedirs(save_dir_fusion)
            cv2.imwrite(
                    osp.join(save_dir_fusion, "{:05d}.jpg".format(frame_id)), fusion_im
                    )
            fusion_images.clear()
            fusion_frame.clear()
    output_video_path = osp.join(args.output_path,args.video_name)
    save_dir_fusion = osp.join(args.output_path, args.fusion_folder)
    cmd_str = 'ffmpeg -f image2 -i {}/%05d.jpg -b 5000k -c:v mpeg4 {}'.format(save_dir_fusion, output_video_path)
    os.system(cmd_str)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--track_offline_path", type=str, default="/mnt/zxu/fairmot-infer/exptemdata/track_kafkames_4", help="kafka mes")
    parser.add_argument("--pose_offline_path", type=str, default="/mnt/zxu/fairmot-infer/exptemdata/pose_kafkabin_4", help="kafka mes")
    parser.add_argument("--face_offline_path", type=str, default="/mnt/zxu/fairmot-infer/exptemdata/face_result_4", help="txt mes")
    parser.add_argument("--assoc_tpid", type=str, default="/mnt/zxu/fairmot-infer/exptemdata/association_4/tid_pid_name.json", help="association of trackid and personid")
    parser.add_argument("--output_path", type=str, default="exptemdata/offline_results_4", help="output path")
    parser.add_argument("--fusion_folder", type=str, default="fusion", help="fusion floder path")
    parser.add_argument("--video_name", type=str, default="fusion.mp4", help="video name")
    parser.add_argument("--draw_pose", action='store_true', default=True, help="draw pose?")
    parser.add_argument("--draw_face", action='store_true', default=True, help="draw face?")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    demo_offlinedraw(args)
