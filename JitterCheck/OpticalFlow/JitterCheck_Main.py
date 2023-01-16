import numpy as np
import cv2
import os

# 尺寸越大，视频越稳定，但对突然平移的反应越小
SMOOTHING_RADIUS = 50


def movingAverage(curve, radius):
    window_size = 2 * radius + 1
    # 定义过滤器
    f = np.ones(window_size) / window_size
    # 为边界添加填充
    curve_pad = np.lib.pad(curve, (radius, radius), 'edge')
    # 应用卷积
    curve_smoothed = np.convolve(curve_pad, f, mode='same')
    # 删除填充
    curve_smoothed = curve_smoothed[radius:-radius]
    # 返回平滑曲线
    return curve_smoothed


def smooth(trajectory):
    smoothed_trajectory = np.copy(trajectory)
    # 过滤x, y和角度曲线
    for i in range(3):
        smoothed_trajectory[:, i] = movingAverage(
            trajectory[:, i], radius=SMOOTHING_RADIUS)

    return smoothed_trajectory


def fixBorder(frame):
    s = frame.shape
    # 在不移动中心的情况下，将图像缩放4%
    T = cv2.getRotationMatrix2D((s[1] / 2, s[0] / 2), 0, 1.04)
    frame = cv2.warpAffine(frame, T, (s[1], s[0]))
    return frame


def get_transformation_matrix(prev_gray_1, prev_gray_2):
    prev_pts = cv2.goodFeaturesToTrack(prev_gray_1,
                                       maxCorners=200,
                                       qualityLevel=0.01,
                                       minDistance=30,
                                       blockSize=3)
    curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray_1, prev_gray_2, prev_pts, None)
    assert prev_pts.shape == curr_pts.shape
    # 只过滤有效点
    idx = np.where(status == 1)[0]
    prev_pts = prev_pts[idx]
    curr_pts = curr_pts[idx]

    # 找到变换矩阵
    m, inlier = cv2.estimateAffine2D(prev_pts, curr_pts)

    # 提取traslation
    dx = m[0, 2]
    dy = m[1, 2]
    # 提取旋转角
    da = np.arctan2(m[1, 0], m[0, 0])

    # 存储转换
    return [float(dx), float(dy), da]


def get_img_file_list(imput_path):
    if not os.path.isdir(imput_path):
        return None
    file_list = [file_name for file_name in os.listdir(imput_path) if 'jpg' in file_name or 'png' in file_name]
    file_list.sort()
    return [os.path.join(imput_path, file_name) for file_name in file_list]


def data_filtrate(data_array, Jitter_range=50, step=30):
    ret = []
    for index, data in enumerate(data_array):
        if abs(data) > Jitter_range:
            ret.append(index)
    ret_end = []
    start, end = ret[0], ret[0]
    for i in ret:
        if i < end + step:
            end = i
        else:
            ret_end.append([start, end])
            start = i
            end = start
    ret_end.append([start, end])

    return ret_end


def JitterCheck_frame(imput_path, Jitter_range):
    frame_list = get_img_file_list(imput_path)
    transforms = np.zeros((len(frame_list), 3), np.float32)
    prev_gray_1 = cv2.imread(frame_list[0], cv2.IMREAD_GRAYSCALE)
    for index, img in enumerate(frame_list):
        prev_gray_2 = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        transformation_matrix = get_transformation_matrix(prev_gray_1, prev_gray_2)
        transforms[index] = transformation_matrix
        prev_gray_1 = prev_gray_2
        print("Frame: " + str(index) + "/" + str(len(frame_list)))
    trajectory = np.cumsum(transforms, axis=0)
    # 创建变量来存储平滑的轨迹
    smoothed_trajectory = smooth(trajectory)

    # 计算smoothed_trajectory与trajectory的差值
    difference = smoothed_trajectory - trajectory

    # 计算更新的转换数组
    transforms_smooth = transforms + difference
    fram_index = data_filtrate(transforms_smooth[:, 1], Jitter_range=Jitter_range)
    return fram_index


def JitterCheck_frame_2_transforms(imput_path):
    frame_list = get_img_file_list(imput_path)
    transforms = np.zeros((len(frame_list), 3), np.float32)
    prev_gray_1 = cv2.imread(frame_list[0], cv2.IMREAD_GRAYSCALE)
    for index, img in enumerate(frame_list):
        prev_gray_2 = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        transformation_matrix = get_transformation_matrix(prev_gray_1, prev_gray_2)
        transforms[index] = transformation_matrix
        prev_gray_1 = prev_gray_2
        print("Frame: " + str(index) + "/" + str(len(frame_list)))
    return transforms


def JitterCheck_Video(imput_path, Jitter_range):
    if not 'mp4' in imput_path:
        return None
    cap = cv2.VideoCapture(imput_path)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    _, prev = cap.read()

    # 将帧转换为灰度
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    transforms = np.zeros((n_frames - 1, 3), np.float32)
    for i in range(n_frames - 2):
        success, curr = cap.read()
        if not success:
            break
        transforms[i] = get_transformation_matrix(prev_gray, curr)
        prev_gray = curr
        print("Frame: " + str(i) + "/" + str(n_frames))
    trajectory = np.cumsum(transforms, axis=0)
    # 创建变量来存储平滑的轨迹
    smoothed_trajectory = smooth(trajectory)

    # 计算smoothed_trajectory与trajectory的差值
    difference = smoothed_trajectory - trajectory

    # 计算更新的转换数组
    transforms_smooth = transforms + difference
    fram_index = data_filtrate(transforms_smooth[:, 1], Jitter_range=Jitter_range)
    return fram_index


def JitterCheck_Video_2_transforms(imput_path):
    if not 'mp4' in imput_path:
        return None
    cap = cv2.VideoCapture(imput_path)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    _, prev = cap.read()

    # 将帧转换为灰度
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    transforms = np.zeros((n_frames - 1, 3), np.float32)
    for i in range(n_frames - 2):
        success, curr = cap.read()
        if not success:
            break
        transforms[i] = get_transformation_matrix(prev_gray, curr)
        prev_gray = curr
        print("Frame: " + str(i) + "/" + str(n_frames))

    return transforms


def JitterCheck_Main(imput_path, Jitter_range):
    if os.path.isdir(imput_path):
        transforms = JitterCheck_frame_2_transforms(imput_path)
    else:
        transforms = JitterCheck_Video_2_transforms(imput_path)
    trajectory = np.cumsum(transforms, axis=0)
    # 创建变量来存储平滑的轨迹
    smoothed_trajectory = smooth(trajectory)

    # 计算smoothed_trajectory与trajectory的差值
    difference = smoothed_trajectory - trajectory

    # 计算更新的转换数组
    transforms_smooth = transforms + difference
    fram_index = data_filtrate(transforms_smooth[:, 1], Jitter_range=Jitter_range)
    return fram_index


def test():
    data_ = np.array([1, 2, 10, 50, 100, 200, 210, 220])


if __name__ == '__main__':
    path = r'C:\Users\NailinLiao\Desktop\record\camera\camera1'
    JitterCheck_frame(path, 10)
    # test()
