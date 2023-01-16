from OpticalFlow.JitterCheck_Main import *
from TargetDetection.JitterCheck_Main import *


def JitterCheck_Main(imput_path, Jitter_range, Tartget=False):
    if Tartget:
        if os.path.isdir(imput_path):
            transforms = JitterCheck_frame_2_transforms(imput_path)
        else:
            transforms = JitterCheck_Video_2_transforms(imput_path)
    else:
        transforms = JitterCheck_Video_2_transforms_by_target(imput_path)

    trajectory = np.cumsum(transforms, axis=0)
    # 创建变量来存储平滑的轨迹
    smoothed_trajectory = smooth(trajectory)

    # 计算smoothed_trajectory与trajectory的差值
    difference = smoothed_trajectory - trajectory

    # 计算更新的转换数组
    transforms_smooth = transforms + difference
    fram_index = data_filtrate(transforms_smooth[:, 1], Jitter_range=Jitter_range)
    return fram_index
