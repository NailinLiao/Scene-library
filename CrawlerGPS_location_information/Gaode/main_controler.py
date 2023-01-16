# 1. 数据有效性判断与取点

    # 1.1 判断文件中的GPS是否发生变化，如果没有变化则文件数据有误，json结果为空

    # 1.2 取点，每秒只保留一帧，每24帧取一个

# 2. 爬取信息

    # 2.1 抓路服务，返回道路等级描述（语义级，如高速公路）、道路名称、道路最高限速

    # 2.2 地址：省份、城市、区县；返回特定POI信息（搜索半径150m）
            # 特定POI：收费站、高速收费站、国省道收费站、桥洞收费站、高速服务区、路口名、环岛名、高速路出口、高速路入口、
            # 立交桥、桥、城市快速路出口、城市快速路入口、隧道

        # POI信息包含：名称、类型、POI中心点到请求坐标的距离、方向

        # 返回道路交叉口列表信息：交叉路口到请求坐标的距离、方位、第一条道路名称、第二条道路名称。


# 3. 信息存储

import time
import os
import traceback

import pandas as pd
import requests

from grasp import Grasp
from regeo import Regeo
from transform import Transform


class Crawl_controller(object):

    def __init__(self, gps_file, key_file):
        self.gps_file = gps_file
        self.key_file = key_file
        self.stop = False
        # 从绝对路径中找到文件名称 xxx.xlsx
        self.base_name = os.path.basename(self.gps_file)
        # 从文件名称中获取时间，并将时间转为utc时间
        self.name_time = str.split(self.base_name, '_')[0]
        # 用来记录抓路和逆编码服务的调用词输，存储在key文件中
        self.grasp = 'grasp_count'
        self.regeo = 'regeo_count'
        self.transform = 'transform_count'
        # 设定调用的最大次数
        self.grasp_max = 300000
        self.regeo_max = 900000
        self.transform_max = 3000000

    def key_process(self):
        '''
        读取key文件，并进行预处理
        :return:  key_df
        '''
        # 1. 读取key文件
        key_df = pd.read_excel(self.key_file)
        key_df.set_index('key', inplace=True)

        if self.grasp not in key_df.columns:
            key_df[self.grasp] = 0
        if self.regeo not in key_df.columns:
            key_df[self.regeo] = 0
        if self.transform not in key_df.columns:
            key_df[self.transform] = 0

        return key_df

    def gps_process(self, key_df):
        # 1. 从文件中获取需要的数据，当前帧数，经纬度，方向，速度
        data = pd.read_excel(self.gps_file, sheet_name='Gps')

        #  1.1 对坐标进行保留6位小数，然后组合为一个坐标字段，用逗号相隔
        data['Longitude'] = data['Longitude'].apply(lambda x: format(x, '.6f'))
        data['Latitude'] = data['Latitude'].apply(lambda x: format(x, '.6f'))
        data['coordinate'] = data['Longitude'].str.cat(data['Latitude'], sep=',')

        columns = ['FrameID', 'coordinate', 'Speed', 'Course']
        data = data[columns].drop_duplicates(subset=['coordinate', 'Speed', 'Course'], keep='first')
        data.reset_index(inplace=True, drop=True)
        # print(data.head(10))

        # TODO 要解开注释
        # 1.2 坐标转换 gps->高德
        transform_server = Transform(data, key_df, self.transform_max)
        data, key_df = transform_server.controller()
        # print(data.head(10))
        # print(key_df.head(10))
        try:
            # 2. 从文件名称中获取时间，并将时间转为utc时间
            data['time'] = data['FrameID'].apply(self.time_transfor)
            # print(data.head(10))

            # 3. 将需要的信息都整理好
            data['info_need'] = data.apply(lambda x: self.get_info_need(x['coordinate'], x['time'], x['Course'], x['Speed']), axis=1)
        except Exception as e:
            print(f'{self.gps_file}为空')

        return data, key_df

    def time_transfor(self, Frame_ID):
        '''
        将北京时间转换为utc时间
        :param Frame_ID: 当前的帧数，要将其转化为秒，加在utc上
        :return: utc时间
        '''
        continue_time = int(Frame_ID) // 25

        return int(time.mktime(time.strptime(str(self.name_time), "%Y-%m-%d-%H-%M-%S")) + continue_time)

    def get_info_need(self, coordinate, time, course, speed):

        return [f"{coordinate}", str(time), str(course), str(speed)]

    def process(self, save_path):
        '''
        用来执行
        :return:
        '''
        # 0. save_path
        save_path = f"{save_path}/{self.base_name.split('.')[0]}"
        # 1. 读取key文件并处理
        key_df = self.key_process()
        # 1. 初步处理数据
        data, key_df = self.gps_process(key_df)

        # 2.1 抓路服务调用
        grasp_server = Grasp(data, key_df, self.grasp_max, save_path)
        key_df, grasp_df, grasp_stop = grasp_server.controller()
        # print(key_df.head(10))

        # 2.2 逆地理编码
        regeo_server = Regeo(data, key_df, self.regeo_max, save_path)
        key_df, regeo_df, regeo_stop = regeo_server.controller()
        # print(key_df.head(10))

        # 3. 将grap_df与regeo_df拼接
        if grasp_stop or regeo_stop:
            self.stop = True

        else:
            df_double = pd.merge(regeo_df, grasp_df, on='FrameID', how='left')
            columns = ['Country', 'Provice', 'City', 'District', 'RoadinterDistance', 'RoadinterDirection',
                        'RoadinterFirstName', 'RoadinterSecondName', 'RoadName', 'RoadLevel', 'MaxSpeed']
            df_double = df_double.reindex(columns=columns)
            df_double.to_excel(f'{save_path}_road.xlsx', sheet_name='Road')
            print('道路信息已合并存储')

        try:
            key_df.to_excel(self.key_file)
            print('key文件已存储')
        except Exception as e:
            print(str(e))
            traceback.print_exc(file=open('traceback_INFO.txt', 'a+'))

        return self.stop