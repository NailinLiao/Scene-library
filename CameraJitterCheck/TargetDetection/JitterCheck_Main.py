import numpy as np
import cv2
from Yolov5_StrongSORT_OSNet.track import parse_opt, run
import os
import pandas as pd


def tracking(source):
    opt = parse_opt()
    # opt.source = r'C:\Users\NailinLiao\Desktop\record\camera1\1670808811066666690.mp4'
    opt.source = source

    # ################################################################################
    # run(**vars(opt))
    # ################################################################################

    file_name = os.path.split(source)[-1]
    txt_file_path = os.path.join('./Yolov5_StrongSORT_OSNet/runs/track/exp/tracks/',
                                 str(file_name).split('.')[0] + '.txt')
    DataFrame = pd.read_csv(txt_file_path, sep='\s+', header=None,
                            names=['frame_idx', 'track_id', 'bbox_left', 'bbox_top',
                                   'bbox_w', 'bbox_h', 'a', 'b', 'c', 'd'])
    return DataFrame


def bbox_to_center(trackingResult_DataFrame):
    trackingResult_DataFrame['center_x'] = np.array(trackingResult_DataFrame['bbox_left']) + np.array(
        trackingResult_DataFrame['bbox_w']) / 2
    trackingResult_DataFrame['center_y'] = np.array(trackingResult_DataFrame['bbox_h']) + np.array(
        trackingResult_DataFrame['bbox_h']) / 2
    return trackingResult_DataFrame


# def transforms_fram(trackingResult_DataFrame: pd.DataFrame):
#     transforms = np.zeros((len(trackingResult_DataFrame) - 1, 3), np.float32)
#     start = trackingResult_DataFrame[trackingResult_DataFrame['frame_idx'] == 1]
#     start_id_list = list(start['track_id'])
#     ponit = [list(z) for z in zip(start['center_x'], start['center_y'])]
#     # print(ret)
#     for key, DataFrame in trackingResult_DataFrame.groupby('frame_idx'):
#         hit_point = []
#         for i, ir in DataFrame.iterrows():
#             if ir['track_id'] in start_id_list:
#                 hit_point.append([ir['center_x'], ir['center_y']])
#         # 计算两个向量的扭曲程度
#         ponit = np.array(ponit)
#         hit_point = np.array(hit_point)
#         # assert ponit.shape == hit_point.shape
#         if len(ponit) > 3 and ponit.shape == hit_point.shape:
#             m, inlier = cv2.estimateAffine2D(ponit, hit_point)
#             dx = m[0, 2]
#             dy = m[1, 2]
#             # 提取旋转角
#             da = np.arctan2(m[1, 0], m[0, 0])
#             # 存储转换
#             transforms[int(key)] = [float(dx), float(dy), da]
#         start_id_list = list(DataFrame['track_id'])
#         ponit = [list(z) for z in zip(DataFrame['center_x'], DataFrame['center_y'])]
#
#     return transforms

def transforms_fram(trackingResult_DataFrame: pd.DataFrame):
    transforms = np.zeros((len(trackingResult_DataFrame) - 1, 3), np.float32)
    start_DataFrame = trackingResult_DataFrame[trackingResult_DataFrame['frame_idx'] == 1]

    for key, DataFrame in trackingResult_DataFrame.groupby('frame_idx'):
        start_point = []
        hit_point = []

        for i, ir in DataFrame.iterrows():
            for index, start_ir in start_DataFrame.iterrows():
                if ir['track_id'] == start_ir['track_id']:
                    hit_point.append([ir['center_x'], ir['center_y']])
                    start_point.append([start_ir['center_x'], start_ir['center_y']])
            ponit = np.array(start_point)
            end_point = np.array(hit_point)
            if len(ponit) > 3:
                m, inlier = cv2.estimateAffine2D(ponit, end_point)
                dx = m[0, 2]
                dy = m[1, 2]
                # 提取旋转角
                da = np.arctan2(m[1, 0], m[0, 0])
                # 存储转换
                transforms[int(key)] = [float(dx), float(dy), da]
        start_DataFrame = DataFrame


    return transforms


def JitterCheck_Video_2_transforms_by_target(source):
    # 设置参数
    # 目标跟踪

    # source = r'C:\Users\NailinLiao\PycharmProjects\CameraJitterCheck\Data_set\camera2\1670812712066666690.mp4'
    trackingResult = tracking(source)
    trackingResult = bbox_to_center(trackingResult)
    transforms = transforms_fram(trackingResult)
    return transforms
    # 筛选目标
    # 多目标计算


if __name__ == '__main__':
    source = r'C:\Users\NailinLiao\PycharmProjects\JitterCheck\Data_set\camera2\1670812712066666690.mp4'
    transforms = JitterCheck_Video_2_transforms_by_target(source)
    print(transforms)