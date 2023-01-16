from __future__ import print_function, division
import datetime
import os
import time
from multiprocessing import Queue
from predicet import multiprocess_predicet, offline_predicet
from multiprocessing import Process
from vlc_toos import test_multiprocessing_put
from get_train_data import off_line_predicer_data

# 流媒体读取图像
# 摄像头定点切割256图像
# 锚点设定
# 锚点检查

# 创建拉去视频流进程
# 创建检查进程

config_camera = {
    'camera1': {
        'url': 'rtsp://192.168.5.36/chan1/main/av_stream',
        'test_path': r'C:\Users\NailinLiao\PycharmProjects\CameraStatusCheck\save_path\test\camera1',
        'center_cut': [970, 791],
        'check_point': [[230, 17], [162, 43], [71, 77], [34, 90]],  # [ [checke_pont x,y] X4 ]
    },
    'camera2': {
        'url': 'rtsp://192.168.5.36/chan2/main/av_stream',
        'test_path': r'C:\Users\NailinLiao\PycharmProjects\CameraStatusCheck\save_path\test\camera2',
        'center_cut': [961, 844],
        'check_point': [[213, 10], [133, 42], [68, 67], [24, 58]],  # [ [checke_pont x,y] X4 ]
    },
    'camera3': {
        'url': 'rtsp://192.168.5.36/chan3/main/av_stream',
        'test_path': r'C:\Users\NailinLiao\PycharmProjects\CameraStatusCheck\save_path\test\camera3',
        'center_cut': [909, 888],
        'check_point': [[242, 50], [179, 72], [114, 96], [43, 123]],  # [ [checke_pont x,y] X4 ]
    },
}


def main():
    from vlc_toos import get_frame
    for key in config_camera:
        print('当前进行 ' + key + ' 检查')
        url = config_camera[key]['url']
        center_cut = config_camera[key]['center_cut']
        check_point = config_camera[key]['check_point']
        q = Queue()
        model_path = r'./model_pth/Unet_epoch_500_batchsize_32.pth'

        put_precess = Process(target=get_frame, args=(q, url, center_cut))
        predicet_precess = Process(target=multiprocess_predicet, args=(model_path, q, check_point))

        put_precess.start()
        predicet_precess.start()
        predicet_precess.join()
        put_precess.kill()
        # put_precess.join()
        print(key + ' 检查结束')
        # predicet_precess.close()
        # put_precess.close()


def test():
    from vlc_toos import test_multiprocessing_put
    base_path = r'C:\Users\NailinLiao\PycharmProjects\CameraStatusCheck\save_path\small_img'
    model_path = r'./model_pth/Unet_epoch_500_batchsize_32.pth'
    check_point = [[230, 17], [162, 43], [71, 77], [34, 90]]
    q = Queue()
    # process=multiprocessing.Process(target=card,args=("你好",),kwargs={"name":wu,"age"=18})#arges要是一个元祖形式
    put_precess = Process(target=test_multiprocessing_put, args=(q, base_path))
    predicet_precess = Process(target=multiprocess_predicet, args=(model_path, q, check_point))

    put_precess.start()
    predicet_precess.start()
    predicet_precess.join()
    put_precess.join()
    predicet_precess.close()
    put_precess.close()


def test_demo():
    for key in config_camera:
        print('当前进行 ' + key + ' 检查')
        test_path = config_camera[key]['test_path']
        # center_cut = config_camera[key]['center_cut']
        check_point = config_camera[key]['check_point']
        q = Queue()
        model_path = r'./model_pth/Unet_epoch_500_batchsize_32.pth'
        put_precess = Process(target=test_multiprocessing_put, args=(q, test_path))
        predicet_precess = Process(target=multiprocess_predicet, args=(model_path, q, check_point))

        put_precess.start()
        predicet_precess.start()
        predicet_precess.join()
        put_precess.kill()
        # put_precess.join()
        print(key + ' 检查结束')
        # predicet_precess.close()
        # put_precess.close()


def offline_main():
    start = time.time()
    vidio_base_path = r'C:\Users\NailinLiao\Desktop\20221226_144329\record'
    model_path = r'./model_pth/Unet_epoch_500_batchsize_32.pth'
    ts = datetime.datetime.now().timestamp()
    save_run_tima = os.path.join('exp', str(ts))
    result = {}
    for key in config_camera:
        print('当前进行 ' + key + ' 检查')
        camere_vidiu_path = os.path.join(vidio_base_path, key)
        video_list = os.listdir(camere_vidiu_path)
        center_cut = config_camera[key]['center_cut']
        check_point = config_camera[key]['check_point']
        for video in video_list:
            if 'mp4' in video:
                video_path = os.path.join(camere_vidiu_path, video)
                img_list = off_line_predicer_data(video_path, save_run_tima, center_cut, size=256)
                statu = offline_predicet(model_path, img_list, check_point, debug=save_run_tima)
                if statu:
                    result[key] = '检测通过'
                else:
                    result[key] = '检测不通过'

    print(result)
    print('耗时:', time.time() - start)

def QT_offline_main():
    start = time.time()
    vidio_base_path = r'C:\Users\NailinLiao\Desktop\20221226_144329\record'
    model_path = r'./model_pth/Unet_epoch_500_batchsize_32.pth'
    ts = datetime.datetime.now().timestamp()
    save_run_tima = os.path.join('exp', str(ts))
    result = {}
    for key in config_camera:
        print('当前进行 ' + key + ' 检查')
        camere_vidiu_path = os.path.join(vidio_base_path, key)
        video_list = os.listdir(camere_vidiu_path)
        center_cut = config_camera[key]['center_cut']
        check_point = config_camera[key]['check_point']
        for video in video_list:
            if 'mp4' in video:
                video_path = os.path.join(camere_vidiu_path, video)
                img_list = off_line_predicer_data(video_path, save_run_tima, center_cut, size=256)
                statu = offline_predicet(model_path, img_list, check_point, debug=save_run_tima)
                if statu:
                    result[key] = '检测通过'
                else:
                    result[key] = '检测不通过'

    print(result)
    print('耗时:', time.time() - start)


if __name__ == '__main__':
    offline_main()
