from OpticalFlow.JitterCheck_Main import *

imput_video = r''
out_put_video = r''
# 读取输入视频
cap = cv2.VideoCapture(imput_video)
# 得到帧数
n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(n_frames)
# 获取视频流的宽度和高度
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 获取每秒帧数(fps)
fps = cap.get(cv2.CAP_PROP_FPS)

# 定义输出视频的编解码器
fourcc = cv2.VideoWriter_fourcc(*'MJPG')

# 设置输出视频
out = cv2.VideoWriter(out_put_video, fourcc, fps, (2 * w, h))

# 读第一帧
_, prev = cap.read()

# 将帧转换为灰度
prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

# 预定义转换numpy矩阵
transforms = np.zeros((n_frames - 1, 3), np.float32)

for i in range(n_frames - 2):
    # 检测前一帧的特征点
    prev_pts = cv2.goodFeaturesToTrack(prev_gray,
                                       maxCorners=200,
                                       qualityLevel=0.01,
                                       minDistance=30,
                                       blockSize=3)

    # 读下一帧
    success, curr = cap.read()
    if not success:
        break

    # 转换为灰度图
    curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)

    # 计算光流(即轨迹特征点)
    curr_pts, status, err = cv2.calcOpticalFlowPyrLK(
        prev_gray, curr_gray, prev_pts, None)

    # 检查完整性
    assert prev_pts.shape == curr_pts.shape

    # 只过滤有效点
    idx = np.where(status == 1)[0]
    prev_pts = prev_pts[idx]
    curr_pts = curr_pts[idx]

    # 找到变换矩阵
    # 只适用于OpenCV-3或更少的版本吗
    # m = cv2.estimateRigidTransform(prev_pts, curr_pts, fullAffine=False)
    m, inlier = cv2.estimateAffine2D(prev_pts, curr_pts)

    # 提取traslation
    dx = m[0, 2]
    dy = m[1, 2]

    # 提取旋转角
    da = np.arctan2(m[1, 0], m[0, 0])

    # 存储转换
    transforms[i] = [dx, dy, da]

    # 移到下一帧
    prev_gray = curr_gray

    print("Frame: " + str(i) + "/" + str(n_frames) +
          " -  Tracked points : " + str(len(prev_pts)))

# 使用累积变换和计算轨迹
trajectory = np.cumsum(transforms, axis=0)

# 创建变量来存储平滑的轨迹
smoothed_trajectory = smooth(trajectory)

# 计算smoothed_trajectory与trajectory的差值
difference = smoothed_trajectory - trajectory

# 计算更新的转换数组
transforms_smooth = transforms + difference

# 将视频流重置为第一帧
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# 写入n_frames-1转换后的帧
for i in range(n_frames - 2):
    # 读下一帧
    success, frame = cap.read()
    if not success:
        break

    # 从新的转换数组中提取转换
    dx = transforms_smooth[i, 0]
    dy = transforms_smooth[i, 1]
    da = transforms_smooth[i, 2]

    # 根据新的值重构变换矩阵
    m = np.zeros((2, 3), np.float32)
    m[0, 0] = np.cos(da)
    m[0, 1] = -np.sin(da)
    m[1, 0] = np.sin(da)
    m[1, 1] = np.cos(da)
    m[0, 2] = dx
    m[1, 2] = dy

    # 应用仿射包装到给定的框架
    frame_stabilized = cv2.warpAffine(frame, m, (w, h))

    # Fix border artifacts
    frame_stabilized = fixBorder(frame_stabilized)

    # 将框架写入文件
    frame_out = cv2.hconcat([frame, frame_stabilized])

    # 如果图像太大，调整它的大小。
    if (frame_out.shape[1] > 1920):
        frame_out = cv2.resize(
            frame_out, (frame_out.shape[1] / 2, frame_out.shape[0] / 2))

    # cv2.imshow("Before and After", frame_out)
    # cv2.waitKey(10)
    out.write(frame_out)

# 发布视频
cap.release()
out.release()
# 关闭窗口
cv2.destroyAllWindows()
