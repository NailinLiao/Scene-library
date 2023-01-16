import cv2
from multiprocessing import Queue
import os
img_path = r'C:\Users\NailinLiao\PycharmProjects\CameraStatusCheck\save_path\test\camera2\camera2_7255.png'


def gety_mouse_location():
    # 设置鼠标回调函数
    def mouse_callback(event, x, y, flags, userdata):
        print(y, x)

    # mouse_callback(1, 100, 200, 2, 'aaa')
    # 创建窗口
    cv2.namedWindow("mouse", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("mouse", 640, 640)
    # 设置鼠标回调
    cv2.setMouseCallback("mouse", mouse_callback, "123")
    # 显示窗口和背景
    img = cv2.imread(img_path)
    while True:
        cv2.imshow("mouse", img)
        key = cv2.waitKey(1)
        if key & 0xFF == 27:
            break
    cv2.destroyAllWindows()


