import numpy as np
import cv2


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


# 尺寸越大，视频越稳定，但对突然平移的反应越小
SMOOTHING_RADIUS = 50

# 读取输入视频
# cap = cv2.VideoCapture('v1.mp4')
cap = cv2.VideoCapture(0)

# # 得到帧数
# n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


# 获取视频流的宽度和高度
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 获取每秒帧数(fps)
fps = cap.get(cv2.CAP_PROP_FPS)

# 预定义转换numpy矩阵
# transforms = np.zeros((n_frames - 1, 3), np.float32)

prev_gray = []

k = 0

# 准备存储
transforms = np.zeros((30, 3), np.float32)

while cap.isOpened():
    # 避免内存泄露，清空列表，重新计算
    if len(prev_gray) >= 29:
        prev_gray = []
        k = 0

    print(k)

    # 读取一帧
    success, curr = cap.read()

    # 是否还有下一帧，关闭
    if not success:
        break

    # 转换为灰度图
    curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)

    # 为了计算帧差，要把前几帧放入列表中
    prev_gray.append(curr_gray)

    if len(prev_gray) >= 2:
        # 检测前一帧的特征点
        prev_pts = cv2.goodFeaturesToTrack(prev_gray[k - 1],
                                           maxCorners=200,
                                           qualityLevel=0.01,
                                           minDistance=30,
                                           blockSize=3)
        # 计算光流(即轨迹特征点) 前一张 当前张 前一张特征
        curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray[k - 1], curr_gray, prev_pts, None)

        # 检查完整性
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
        transforms[k] = [dx, dy, da]

        # cv2.imshow("B", curr_gray)
        # cv2.waitKey(1)
    k += 1

    if len(prev_gray) >= 3:
        # 使用累积变换和计算轨迹
        trajectory = np.cumsum(transforms, axis=0)

        # 创建变量来存储平滑的轨迹
        smoothed_trajectory = smooth(trajectory)

        # 计算smoothed_trajectory与trajectory的差值
        difference = smoothed_trajectory - trajectory

        # 计算更新的转换数组
        transforms_smooth = transforms + difference

        # 从新的转换数组中提取转换
        dx = transforms_smooth[k, 0]
        dy = transforms_smooth[k, 1]
        da = transforms_smooth[k, 2]

        # 根据新的值重构变换矩阵
        m = np.zeros((2, 3), np.float32)
        m[0, 0] = np.cos(da)
        m[0, 1] = -np.sin(da)
        m[1, 0] = np.sin(da)
        m[1, 1] = np.cos(da)
        m[0, 2] = dx
        m[1, 2] = dy

        # 应用仿射包装到给定的框架
        frame_stabilized = cv2.warpAffine(curr, m, (w, h))

        # Fix border artifacts
        frame_stabilized = fixBorder(frame_stabilized)
        cv2.imshow("B", frame_stabilized)
        cv2.waitKey(1)
