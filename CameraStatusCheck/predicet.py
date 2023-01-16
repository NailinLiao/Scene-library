from __future__ import print_function, division

import os

import cv2
from PIL import Image
import torch.utils.data
import torch
import torch.nn.functional as F
import torch.nn
import torchvision
from unet.Models import Unet_dict, NestedUNet, U_Net, R2U_Net, AttU_Net, R2AttU_Net
from multiprocessing import Queue
import time
import queue
import datetime


def predicet_main(model_path, test_image):
    model_Inputs = [U_Net, R2U_Net, AttU_Net, R2AttU_Net, NestedUNet]
    train_on_gpu = torch.cuda.is_available()

    device = torch.device("cuda:0" if train_on_gpu else "cpu")

    data_transform = torchvision.transforms.Compose([
        #  torchvision.transforms.Resize((128,128)),
        #   torchvision.transforms.CenterCrop(96),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])

    def model_unet(model_input, in_channel=3, out_channel=1):
        model_test = model_input(in_channel, out_channel)
        return model_test

    model_test = model_unet(model_Inputs[0], 3, 1)
    model_test.to(device)

    model_test.load_state_dict(torch.load(model_path))

    model_test.eval()

    img = Image.open(test_image)
    s_tb = data_transform(img)
    pred = model_test(s_tb.unsqueeze(0).to(device)).cpu()
    pred = F.sigmoid(pred)
    pred = pred.detach().numpy()
    mask = pred[0][0]
    cv2.imshow('mask1', mask)

    ret, mask = cv2.threshold(mask, 0.1, 255, cv2.THRESH_BINARY)

    cv2.imshow('mask2', mask)
    cv2.waitKey(0)


def multiprocess_predicet(model_path, q: Queue, check_point_list, run_time=60, debug=False):
    model_Inputs = [U_Net, R2U_Net, AttU_Net, R2AttU_Net, NestedUNet]
    train_on_gpu = torch.cuda.is_available()
    train_on_gpu = False

    device = torch.device("cuda:0" if train_on_gpu else "cpu")
    data_transform = torchvision.transforms.Compose([
        #  torchvision.transforms.Resize((128,128)),
        #   torchvision.transforms.CenterCrop(96),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])

    def model_unet(model_input, in_channel=3, out_channel=1):
        model_test = model_input(in_channel, out_channel)
        return model_test

    if debug:
        print('创建模型')
    model_test = model_unet(model_Inputs[0], 3, 1)
    model_test.to(device)
    model_test.load_state_dict(torch.load(model_path))
    model_test.eval()
    if debug:
        print('开始预测')
    start_time = time.time()

    while (time.time() - start_time) < run_time:
        try:
            img = q.get(block=True, timeout=3)
            if debug:
                print('获取图像')
        except queue.Empty:
            print('检测不通过')
            if debug:
                print('队列为空，get失败')
            return False
        s_tb = data_transform(img)
        pred = model_test(s_tb.unsqueeze(0).to(device)).cpu()
        pred = F.sigmoid(pred)
        pred = pred.detach().numpy()
        mask = pred[0][0]
        if debug:
            print('获取预测结果')

        ret, mask = cv2.threshold(mask, 0.1, 255, cv2.THRESH_BINARY)
        hit = 0
        if debug:
            print('关键点检查')

        for check_point in check_point_list:
            y, x = check_point[0], check_point[1]
            if mask[y, x] > 0:
                hit += 1
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        if hit == len(check_point_list):
            print('检测通过')
            if debug:
                # 添加保存检查点图像
                ts = datetime.datetime.now().timestamp()
                file_name = str(ts) + '.png'
                cv2.imwrite(file_name, img)  # 保存图像文件

            return True
    if debug:
        # 添加保存检查点图像
        ts = datetime.datetime.now().timestamp()
        file_name = str(ts) + '.png'
        cv2.imwrite(file_name, img)  # 保存图像文件
    print('检测不通过')
    # 添加保存检查点图像

    return False


def offline_predicet(model_path, img_path_list, check_point_list, debug=None):
    model_Inputs = [U_Net, R2U_Net, AttU_Net, R2AttU_Net, NestedUNet]
    train_on_gpu = torch.cuda.is_available()
    train_on_gpu = False
    hit_statu = False
    device = torch.device("cuda:0" if train_on_gpu else "cpu")

    data_transform = torchvision.transforms.Compose([
        #  torchvision.transforms.Resize((128,128)),
        #   torchvision.transforms.CenterCrop(96),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])

    def model_unet(model_input, in_channel=3, out_channel=1):
        model_test = model_input(in_channel, out_channel)
        return model_test

    model_test = model_unet(model_Inputs[0], 3, 1)
    model_test.to(device)

    model_test.load_state_dict(torch.load(model_path))

    model_test.eval()

    for img_path in img_path_list:
        img = cv2.imread(img_path)
        s_tb = data_transform(img)
        pred = model_test(s_tb.unsqueeze(0).to(device)).cpu()
        pred = F.sigmoid(pred)
        pred = pred.detach().numpy()
        mask = pred[0][0]
        ret, mask = cv2.threshold(mask, 0.1, 255, cv2.THRESH_BINARY)
        hit = 0
        for check_point in check_point_list:
            y, x = check_point[0], check_point[1]
            if mask[y, x] > 0:
                hit += 1
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        if debug != None:
            # 添加保存检查点图像
            save_path = os.path.join(debug, 'debug')
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            ts = datetime.datetime.now().timestamp()
            file_name = os.path.join(save_path, str(ts) + '.png')
            cv2.imwrite(file_name, img)  # 保存图像文件

        if hit == len(check_point_list):
            hit_statu = True
            break

    if hit_statu:
        print(
            '检测通过================================================================================================================')
        # time.sleep(10)
        return True
    else:
        print(
            '检测不通过================================================================================================================')
        # time.sleep(10)
        return False


def QT_predicet(model_path, img_list, check_point_list, debug=None):
    print('1')
    model_Inputs = [U_Net, R2U_Net, AttU_Net, R2AttU_Net, NestedUNet]
    train_on_gpu = torch.cuda.is_available()
    hit_statu = False
    device = torch.device("cuda:0" if train_on_gpu else "cpu")

    data_transform = torchvision.transforms.Compose([
        #  torchvision.transforms.Resize((128,128)),
        #   torchvision.transforms.CenterCrop(96),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])

    def model_unet(model_input, in_channel=3, out_channel=1):
        model_test = model_input(in_channel, out_channel)
        return model_test

    model_test = model_unet(model_Inputs[0], 3, 1)
    model_test.to(device)

    model_test.load_state_dict(torch.load(model_path))
    model_test.eval()

    for img in img_list:
        s_tb = data_transform(img)
        pred = model_test(s_tb.unsqueeze(0).to(device)).cpu()
        pred = F.sigmoid(pred)
        pred = pred.detach().numpy()
        mask = pred[0][0]
        ret, mask = cv2.threshold(mask, 0.1, 255, cv2.THRESH_BINARY)
        hit = 0
        for check_point in check_point_list:
            y, x = check_point[0], check_point[1]
            if mask[y, x] > 0:
                hit += 1
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        if debug:
            # 添加保存检查点图像
            cv2.imshow('ima', img)
            cv2.waitKey(1)
        if hit == len(check_point_list):
            hit_statu = True
            break

    if hit_statu:
        print(
            '检测通过================================================================================================================')
        # time.sleep(10)
        return True
    else:
        print(
            '检测不通过================================================================================================================')
        # time.sleep(10)
        return False


if __name__ == '__main__':
    model_path = r'./model_pth/Unet_epoch_500_batchsize_32.pth'
    test_image = r'C:\Users\NailinLiao\Desktop\train\img\1.png'
    predicet_main(model_path, test_image)
