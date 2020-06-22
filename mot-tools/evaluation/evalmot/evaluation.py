import os
import numpy as np
import copy
import motmetrics as mm
mm.lap.default_solver = 'lap'
import argparse

from read import read_results, unzip_objs


class Evaluator(object):

    def __init__(self, data_root, seq_name, data_type):
        self.data_root = data_root
        self.seq_name = seq_name
        self.data_type = data_type

        self.load_annotations()
        self.reset_accumulator()

    def load_annotations(self):
        assert self.data_type == 'mot'
        gt_filename = os.path.join(self.data_root, self.seq_name, 'gt', 'gt.txt')
        if not os.path.exists(gt_filename):
            gt_filename = os.path.join(self.data_root, self.seq_name, 'gt', str(self.seq_name)+'.txt')
        self.gt_frame_dict = read_results(gt_filename, self.data_type, is_gt=True)
        self.gt_ignore_frame_dict = read_results(gt_filename, self.data_type, is_ignore=True)

    def reset_accumulator(self):
        self.acc = mm.MOTAccumulator(auto_id=True)

    def eval_frame(self, frame_id, trk_tlwhs, trk_ids, rtn_events=False):
        # results
        trk_tlwhs = np.copy(trk_tlwhs)
        trk_ids = np.copy(trk_ids)

        # gts
        gt_objs = self.gt_frame_dict.get(frame_id, [])
        gt_tlwhs, gt_ids = unzip_objs(gt_objs)[:2]

        # ignore boxes
        ignore_objs = self.gt_ignore_frame_dict.get(frame_id, [])
        ignore_tlwhs = unzip_objs(ignore_objs)[0]

        # remove ignored results
        keep = np.ones(len(trk_tlwhs), dtype=bool)
        iou_distance = mm.distances.iou_matrix(ignore_tlwhs, trk_tlwhs, max_iou=0.5)
        if len(iou_distance) > 0:
            match_is, match_js = mm.lap.linear_sum_assignment(iou_distance)
            match_is, match_js = map(lambda a: np.asarray(a, dtype=int), [match_is, match_js])
            match_ious = iou_distance[match_is, match_js]

            match_js = np.asarray(match_js, dtype=int)
            match_js = match_js[np.logical_not(np.isnan(match_ious))]
            keep[match_js] = False
            trk_tlwhs = trk_tlwhs[keep]
            trk_ids = trk_ids[keep]
        #match_is, match_js = mm.lap.linear_sum_assignment(iou_distance)
        #match_is, match_js = map(lambda a: np.asarray(a, dtype=int), [match_is, match_js])
        #match_ious = iou_distance[match_is, match_js]

        #match_js = np.asarray(match_js, dtype=int)
        #match_js = match_js[np.logical_not(np.isnan(match_ious))]
        #keep[match_js] = False
        #trk_tlwhs = trk_tlwhs[keep]
        #trk_ids = trk_ids[keep]

        # get distance matrix
        iou_distance = mm.distances.iou_matrix(gt_tlwhs, trk_tlwhs, max_iou=0.5)

        # acc
        self.acc.update(gt_ids, trk_ids, iou_distance)

        if rtn_events and iou_distance.size > 0 and hasattr(self.acc, 'last_mot_events'):
            events = self.acc.last_mot_events  # only supported by https://github.com/longcw/py-motmetrics
        else:
            events = None
        return events

    def eval_file(self, filename, isgt):
        self.reset_accumulator()

        result_frame_dict = read_results(filename, self.data_type, is_gt=isgt)
        # 如果输入的预测文件为gt.txt，此处is_gt需要设置为True，不然不需要考虑的记录也会纳入计算中
        frames = sorted(list(set(self.gt_frame_dict.keys()) | set(result_frame_dict.keys())))
        for frame_id in frames:
            trk_objs = result_frame_dict.get(frame_id, [])
            trk_tlwhs, trk_ids = unzip_objs(trk_objs)[:2]
            self.eval_frame(frame_id, trk_tlwhs, trk_ids, rtn_events=False)

        return self.acc

    @staticmethod
    def get_summary(accs, names, metrics=('mota', 'num_switches', 'idp', 'idr', 'idf1', 'precision', 'recall')):
        names = copy.deepcopy(names)
        if metrics is None:
            metrics = mm.metrics.motchallenge_metrics
        metrics = copy.deepcopy(metrics)

        mh = mm.metrics.create()
        summary = mh.compute_many(
            accs,
            metrics=metrics,
            names=names,
            generate_overall=True
        )

        return summary

    @staticmethod
    def save_summary(summary, filename):
        import pandas as pd
        writer = pd.ExcelWriter(filename)
        summary.to_excel(writer)
        writer.save()


def select_datasets(opt):
    if opt.val_mot15:
        seqs_str = '''KITTI-13
                      KITTI-17
                      ETH-Bahnhof
                      ETH-Sunnyday
                      PETS09-S2L1
                      TUD-Campus
                      TUD-Stadtmitte
                      ADL-Rundle-6
                      ADL-Rundle-8
                      ETH-Pedcross2
                      TUD-Stadtmitte'''
        data_root = os.path.join(opt.data_dir, 'MOT15/images/train')
    if opt.val_mot16:
        seqs_str = '''MOT16-02
                      MOT16-04
                      MOT16-05
                      MOT16-09
                      MOT16-10
                      MOT16-11
                      MOT16-13'''
        data_root = os.path.join(opt.data_dir, 'MOT16/train')
    if opt.val_mot17:
        seqs_str = '''MOT17-02-SDP
                      MOT17-04-SDP
                      MOT17-05-SDP
                      MOT17-09-SDP
                      MOT17-10-SDP
                      MOT17-11-SDP
                      MOT17-13-SDP'''
        data_root = os.path.join(opt.data_dir, 'MOT17/images/train')
    if opt.val_aifw4:
        seqs_str = '''201
                      202
                      203
                      204'''
        data_root = os.path.join(opt.data_dir, 'AIFWMOT4-7500')
    if opt.test_mot15:
        seqs_str = '''ADL-Rundle-1
                      ADL-Rundle-3
                      AVG-TownCentre
                      ETH-Crossing
                      ETH-Jelmoli
                      ETH-Linthescher
                      KITTI-16
                      KITTI-19
                      PETS09-S2L2
                      TUD-Crossing
                      Venice-1'''
        data_root = os.path.join(opt.data_dir, 'MOT15/images/test')
    if opt.test_mot16:
        seqs_str = '''MOT16-01
                      MOT16-03
                      MOT16-06
                      MOT16-07
                      MOT16-08
                      MOT16-12
                      MOT16-14'''
        data_root = os.path.join(opt.data_dir, 'MOT16/test')
    if opt.test_mot17:
        seqs_str = '''MOT17-01-SDP
                      MOT17-03-SDP
                      MOT17-06-SDP
                      MOT17-07-SDP
                      MOT17-08-SDP
                      MOT17-12-SDP
                      MOT17-14-SDP'''
        data_root = os.path.join(opt.data_dir, 'MOT17/images/test')
    if opt.val_mot20:
        seqs_str = '''MOT20-01
                      MOT20-02
                      MOT20-03
                      MOT20-05
                      '''
        data_root = os.path.join(opt.data_dir, 'MOT20/images/train')
    if opt.test_mot20:
        seqs_str = '''MOT20-04
                      MOT20-06
                      MOT20-07
                      MOT20-08
                      '''
        data_root = os.path.join(opt.data_dir, 'MOT20/images/test')
    try:
        seqs = [seq.strip() for seq in seqs_str.split()]
    except:
        print('no dataset is chosen')
    return data_root, seqs


def main(opt):
    print(opt)
    data_root,seqs = select_datasets(opt)
    files = os.listdir(opt.pre_fileroot)
    files = sorted(files)
    # assert len(files) == len(seqs)
    acc = []
    print("="*80)
    print('files:')
    print("="*80)
    for i in range(len(seqs)):
        if files[i].endswith('txt'):
            pdt_path = os.path.join(opt.pre_fileroot, files[i]) 
            evaluator = Evaluator(data_root, seqs[i], 'mot')
            acc.append(evaluator.eval_file(pdt_path, opt.isgt))
            print('gt:', seqs[i], '     pdt:', pdt_path)
            # metrics = mm.metrics.motchallenge_metrics
            # mh = mm.metrics.create()
            # summary = Evaluator.get_summary(acc, seqs[i], metrics)

            # strsummary = mm.io.render_summary(
            #     summary,
            #     formatters=mh.formatters,
            #     namemap=mm.io.motchallenge_metric_names
            # )
            # print(strsummary)

    print("="*80)
    print('summary')
    print("="*80)
    metrics = mm.metrics.motchallenge_metrics
    mh = mm.metrics.create()
    summary = Evaluator.get_summary(acc, seqs, metrics)

    strsummary = mm.io.render_summary(
        summary,
        formatters=mh.formatters,
        namemap=mm.io.motchallenge_metric_names
    )
    print(strsummary)


if __name__ == '__main__':
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', default='/mnt/data', type=str, help='root of dataset')
    parser.add_argument('--val_mot15', action='store_true')
    parser.add_argument('--val_mot16', action='store_true')
    parser.add_argument('--val_mot17', action='store_true')
    parser.add_argument('--val_mot20', action='store_true')
    parser.add_argument('--test_mot15', action='store_true')
    parser.add_argument('--test_mot16', action='store_true')
    parser.add_argument('--test_mot17', action='store_true')
    parser.add_argument('--test_mot20', action='store_true')
    parser.add_argument('--val_aifw4', action='store_true')
    parser.add_argument('--data_type', default='mot')
    parser.add_argument('--pre_fileroot', default='evaluation/aifw4_7500', help='the prediction file')
    parser.add_argument('--isgt', action='store_true', help='if the prediction file is gt file, set this True')
    opt = parser.parse_args()
    main(opt)