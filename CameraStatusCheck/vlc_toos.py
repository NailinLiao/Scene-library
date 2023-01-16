# 拉取rtsp流
import os

import cv2
import time
import traceback
from multiprocessing import Queue


def delay_time(rtsp_url):
    """
    获取拉取到第一帧数据的时间
    :return:
    """
    start_time = time.time()
    cap = cv2.VideoCapture(rtsp_url)
    if cap.isOpened():
        success, frame = cap.read()
        cost_time = time.time() - start_time
        print(f"拉取到第一帧数据用时：{cost_time}秒")
        return cost_time
    else:
        print("拉取流地址失败")


def pull_rtsp(rtsp_url, run_time=60, save_file=""):
    """
    拉取视频流
    :param run_time: 拉取的时长，单位秒。默认为60秒
    :param save_file: 保存的文件名不带尾缀，格式为avi,默认空时，不保存拉取 视频流
    :return:
    """
    videoWrite = False
    cap = cv2.VideoCapture(rtsp_url)
    # 获取视频分辨率
    if save_file:
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        # 获取视频帧率
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        print(f"视频流的分辨率{size}, FPS:{fps}")
        # 设置视频格式
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # 调用VideoWrite（）函数
        videoWrite = cv2.VideoWriter(f"{save_file}.avi", fourcc, fps, size)

    # 运行指定的时长
    start_time = time.time()
    while (time.time() - start_time) < run_time:
        if cap.isOpened():
            try:
                success, frame = cap.read()
                if not videoWrite is False:
                    videoWrite.write(frame)
                cv2.imshow("frame", frame)
                cv2.waitKey(1)
            # 获取视频流异常后重新拉取
            except Exception as e:
                print(traceback.format_exc())
                cap = cv2.VideoCapture(rtsp_url)
                time.sleep(1)
        else:
            print("拉取流地址失败")
    print("拉取结束，退出程序")


def get_frame(q: Queue, url, cut_cent, extractionRate=30, run_time=60, cut_size=256, debug=False):
    cap = cv2.VideoCapture(rtsp_url)
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    # 获取视频帧率
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"视频流的分辨率{size}, FPS:{fps}")
    start_time = time.time()
    index = 0

    cut_point = [int(cut_cent[0] - (size / 2)), int(cut_cent[1] - (size / 2))]
    while (time.time() - start_time) < run_time:
        # time.sleep(1)
        if cap.isOpened():
            try:
                success, frame = cap.read()
                if debug:
                    cv2.imshow('img', frame)
                    cv2.waitKey(1)
                frame = frame[cut_point[1]:cut_point[1] + cut_size, cut_point[0]:cut_point[0] + cut_size]
                index += 1
                # if index % extractionRate == 0:
                q.put(frame)
            except Exception as e:
                print(traceback.format_exc())
                cap = cv2.VideoCapture(rtsp_url)
        else:
            print("拉取流地址失败")
    print(url, "拉取结束")
    return None


def test_multiprocessing_put(q: Queue, img_base_path, run_time=20):
    start_time = time.time()
    img_list = os.listdir(img_base_path)
    index = 0
    while (time.time() - start_time) < run_time:
        if index < len(img_list):
            img_file = os.path.join(img_base_path, img_list[index])
            img = cv2.imread(img_file)
            q.put(img)
            # time.sleep(1)
            index += 1
            # print('放入图像', img_file)


if __name__ == "__main__":
    rtsp_url = r"rtsp://192.168.5.36/chan3/main/av_stream"
    delay_time(rtsp_url)
    file_name = "video"
    pull_rtsp(rtsp_url, run_time=60, save_file=file_name)
