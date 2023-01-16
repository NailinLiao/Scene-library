import os
import cv2
import numpy as np
import random

channel = {
    'record': ['camera1', 'camera2', 'camera3', 'camera5', 'camera7', 'camera9', 'camera11', 'camera12', 'camera13',
               'camera14', 'camera15', 'camera16'],
    'ins': ['ins1/gps_ins.txt', 'ins1/imu_data.txt', 'ins1/imu_ins.txt', 'ins1/imu_raw.txt'],
}

camera_cut_location = {
    'camera1': [970, 791],
    'camera2': [961, 844],
    'camera3': [909, 888],
}


def mp4_2_png(video, save_path, tar_num=1000, step=2):
    if os.path.exists(save_path):
        pass
    else:
        os.makedirs(save_path)
    recode_name = str(video).split('\\')[-2]
    cap = cv2.VideoCapture(video)
    frame_index = 7200
    # step = step * 30

    for i in range(0, tar_num):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if ret:
            frame_index += step
            png_path = os.path.join(save_path, recode_name + '_' + str(frame_index) + '.png')
            cv2.imwrite(png_path, frame)  # 保存图像文件


def frame_2_smallSize(img_path, save_path, cut_cent=None, size=256):
    if os.path.exists(save_path):
        pass
    else:
        os.makedirs(save_path)
    img = cv2.imread(img_path)
    img_name = str(img_path).split('\\')[-1]
    save_path = os.path.join(save_path, img_name)
    if cut_cent:
        pass
    else:
        img_size = img.shape  # (1080, 1920, 3)
        cut_cent = [random.randint(int(img_size[1] / 4), int(img_size[1] * 3 / 4)),
                    random.randint(int(img_size[0] / 2), img_size[0] - 128)]
        print(cut_cent)
    cut_point = [int(cut_cent[0] - (size / 2)), int(cut_cent[1] - (size / 2))]
    img = img[cut_point[1]:cut_point[1] + size, cut_point[0]:cut_point[0] + size]
    cv2.imwrite(save_path, img)  # 保存图像文件


def frame_2_smallSize_test():
    img_path = r'C:\Users\NailinLiao\PycharmProjects\CameraStatusCheck\ret\camera1_300.png'
    save_path = r'./small_test'
    frame_2_smallSize(img_path, save_path, cut_cent=None, size=256)


def main():
    record_base_path = r'C:\Users\NailinLiao\Desktop\download_2022-12-21_15-36-34\record'
    save_frame_path = r'./save_path/frame'
    save_smallSize_path = r'./save_path/small_img'
    tar_num = 500
    video_list = []
    for record in channel['record'][:3]:
        record_base = os.path.join(record_base_path, record)
        file_list = os.listdir(record_base)
        for file_name in file_list:
            if 'mp4' in file_name:
                mp4_file = os.path.join(record_base, file_name)
                video_list.append(mp4_file)

    for video in video_list:
        mp4_2_png(video, save_frame_path, tar_num=tar_num, step=1)

    frame_list = os.listdir(save_frame_path)
    for frame in frame_list:
        camera = str(str(frame).split('\\')[-1]).split('_')[0]
        cut_cent = camera_cut_location[camera]
        img_path = os.path.join(save_frame_path, frame)
        frame_2_smallSize(img_path, save_smallSize_path, cut_cent=cut_cent, size=256)


def off_line_predicer_data(video, save_path, cut_cent, size=256):
    print(os.path.split(video))
    recode_name = str(video).split('\\')[-2]
    print(recode_name)
    careme_save_path = os.path.join(save_path, recode_name)
    if not os.path.exists(careme_save_path):
        os.makedirs(careme_save_path)
    cut_point = [int(cut_cent[0] - (size / 2)), int(cut_cent[1] - (size / 2))]
    cap = cv2.VideoCapture(video)

    ret, frame = cap.read()
    frame_index = 0
    img_list = []
    while ret:
        ret, frame = cap.read()
        if ret:
            frame_index += 1
            png_path = os.path.join(careme_save_path, str(frame_index) + '.png')
            frame = frame[cut_point[1]:cut_point[1] + size, cut_point[0]:cut_point[0] + size]

            cv2.imwrite(png_path, frame)  # 保存图像文件
            img_list.append(png_path)
    return img_list


def QT_predicer_data(video, save_path, cut_cent, size=256):

    cut_point = [int(cut_cent[0] - (size / 2)), int(cut_cent[1] - (size / 2))]
    cap = cv2.VideoCapture(video)
    ret, frame = cap.read()
    frame_index = 0
    img_list = []
    while ret:
        ret, frame = cap.read()
        if ret:
            frame_index += 1
            frame = frame[cut_point[1]:cut_point[1] + size, cut_point[0]:cut_point[0] + size]
            img_list.append(frame)
    return img_list


if __name__ == '__main__':
    main()
