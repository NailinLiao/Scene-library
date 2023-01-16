import pandas as pd
import numpy as np
from math import sin, asin, cos, radians, fabs, sqrt
import os

place_centre = [38.8785637, 117.2704798]
door_center = [38.882579, 117.2704748]


def get_distance_hav(lat0, lng0, lat1, lng1):
    '''
    获取经纬度间的距离，单位km
    '''
    EARTH_RADIUS = 6371.137  # 地球平均半径大约6371km

    def hav(theta):
        s = sin(theta / 2)
        return s * s

    # 用haversine公式计算球面两点间的距离
    # 经纬度转换成弧度
    lat0 = radians(lat0)
    lat1 = radians(lat1)
    lng0 = radians(lng0)
    lng1 = radians(lng1)
    dlng = fabs(lng0 - lng1)
    dlat = fabs(lat0 - lat1)
    h = hav(dlat) + cos(lat0) * cos(lat1) * hav(dlng)
    distance = 2 * EARTH_RADIUS * asin(sqrt(h))  # km
    return distance


def mask_open_road(gps_ins_file_path, place_scope=0.5, door_scope=0.008):
    '''
    获取该gps文件中的厂外数据节点

    :return:【开始帧，结束帧】，如果为   [None, None] 则该批数据均在场内

    '''
    imudata = pd.read_csv(gps_ins_file_path)
    out_place_scope = []
    in_door_scope = []
    for UTCTimeStamp, Lattitude, Longitude in zip(imudata['UTCTimeStamp'], imudata['Lattitude'],
                                                  imudata['Longitude']):
        print(UTCTimeStamp, Lattitude, Longitude)
        if get_distance_hav(Lattitude, Longitude, place_centre[0],
                            place_centre[1]) > place_scope:
            out_place_scope.append(int(UTCTimeStamp))
        if get_distance_hav(Lattitude, Longitude, door_center[0],
                            door_center[1]) < door_scope:
            in_door_scope.append(int(UTCTimeStamp))

    out_place_scope = np.array(out_place_scope)
    in_door_scope = np.array(in_door_scope)
    if len(in_door_scope) == 0 and len(out_place_scope) != 0:
        return [out_place_scope.min(), out_place_scope.max()]
    elif len(in_door_scope) != 0 and len(out_place_scope) != 0:
        return [min(in_door_scope.min(), out_place_scope.min()), max(in_door_scope.max(), out_place_scope.max())]
    elif len(in_door_scope) == 0 and len(out_place_scope) == 0:
        return [None, None]


# [1670809295320000000, 1670812624500000000]
# [1670809295320000000, 1670812624500000000]

def test():
    gps_ins_file_path = r'C:\Users\NailinLiao\PycharmProjects\Mark_location\data\ins\ins1\gps_ins.txt'
    print(mask_open_road(gps_ins_file_path))


def listdir(path, list_name=[]):  # 传入存储的list
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if not 'record' in file_path and not 'lidar' in file_path and not 'radar' in file_path and not 'ailed' in file_path:
            if os.path.isdir(file_path):
                listdir(file_path, list_name)
            else:
                print(file_path)
                list_name.append(file_path)
    return list_name


def nas_check():
    nas_base_path = r'Z:\数据组\数采车'
    # nas_base_path = r'Z:\数据组\数采车\20221121_IMU_Lidar(Failed)\20221121_112718_output\ins\ins1'
    file_list = listdir(nas_base_path)
    gps_ins_file_list = []
    ret_dict = {'name': [],
                'fram': [], }
    for file in file_list:
        if 'gps_ins.txt' in file and 'output' in file:
            gps_ins_file_list.append(file)
    for gps_file in gps_ins_file_list:
        try:
            ret_dict['name'].append(str(gps_file).split('\\')[-4])
            print(gps_file)

            ret_dict['fram'].append(mask_open_road(gps_file))

            print(str(gps_file).split('\\')[-4], "       :      ", mask_open_road(gps_file))
        except:
            print('ERRO:',gps_file)
    DataFrame = pd.DataFrame(ret_dict)
    DataFrame.to_csv('./ret/sult.csv')


if __name__ == '__main__':
    nas_check()
