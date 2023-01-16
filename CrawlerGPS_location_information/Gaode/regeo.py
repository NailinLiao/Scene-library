import traceback

import pandas as pd
import requests


class Regeo():
    ''' 抓路服务 '''

    def __init__(self, df, key_df, regeo_max, save_path):
        self.df = df
        self.key_df = key_df
        self.stop = False
        self.regeo_max = regeo_max
        self.save_path = save_path
        road_columns = ['FrameID', 'Country', 'Provice', 'City', 'District', 'RoadinterDistance', 'RoadinterDirection',
                        'RoadinterFirstName', 'RoadinterSecondName']

        # 'TrafficDescription', 'TrafficExpedite', 'TrafficCongested', 'TrafficBlocked', 'TrafficUnknown'

        poi_columns = ['FrameID', 'POIType', 'POIName', 'POIDistance', 'POIDirection']

        self.road_df = pd.DataFrame(columns=road_columns)
        self.poi_df = pd.DataFrame(columns=poi_columns)

        self.poitype = '收费站|高速收费站|国省道收费站|桥洞收费站|高速服务区|路口名|环岛名|高速路出口|高速路入口|立交桥|桥|城市快速路出口|城市快速路入口|隧道'
        self.radius = '150'

    def controller(self):

        print('正在获取逆编码信息')
        key_list = self.key_df[self.key_df['regeo_count'] < self.regeo_max].index.values.tolist()

        try:
            for i in range(self.df.shape[0]):

                road_url = self.get_road_url(self.df.loc[i, 'coordinate'], key_list[0])

                # print(road_url)

                regeo_info = self.crawler(road_url)
                #
                self.process_info(regeo_info, i)

                try:
                    if int(self.key_df.loc[key_list[0], 'regeo_count']) < self.regeo_max:
                        pass
                    else:
                        del key_list[0]

                    if len(key_list) != 0:

                        self.key_df.loc[key_list[0], 'regeo_count'] += 1
                    else:
                        print('今日逆地理编码抓取次数已用尽')
                        print('最终未处理的文件位置 %s' % self.save_path)
                        self.stop = True
                        break

                except:
                    print('出现错误的元素是%s' % str(road_url))
                    continue
        except Exception as e:
            print(str(e))
            with open('traceback_INFO.txt', 'a+') as f:
                f.writelines(f'{self.save_path}\r\n')
            traceback.print_exc(file=open('traceback_INFO.txt', 'a+'))
        finally:
            self.road_df.set_index('FrameID', inplace=True)
            self.poi_df.set_index('FrameID', inplace=True)
            re_columns = ['POIType', 'POIName', 'POIDistance', 'POIDirection']
            self.poi_df = self.poi_df.reindex(columns=re_columns)
            self.poi_df.to_excel(f'{self.save_path}_poi.xlsx', sheet_name='POI')
            # self.road_df.to_excel(f'{self.save_path}_regeo.xlsx')
            print('逆地理编码调用已完成')
            print('逆地理编码文件已存储')

            return self.key_df, self.road_df, self.stop

    def get_road_url(self, coordinate, key_info):
        '''
        拼接抓路url
        :return:
        '''
        #
        head = 'https://restapi.amap.com/v3/geocode/regeo?output=json&extensions=all&roadlevel=0'
        location = f"location={coordinate}"
        poitype = f"poitype={self.poitype}"
        radius = f"radius={self.radius}"
        key = f"key={key_info}"

        url = f"{head}&{location}&{poitype}&{radius}&{key}"
        # 目前url获取成功，后面的步骤是，读取所有key的列表，通过设定次数上限，每次使用的时候进行记录并判定，保证每次
        # 读取的时候不会因为重复读取不累计次数的情况
        # print(url)
        return url

    def crawler(self, url):

        crawl_data = requests.get(url)

        json_data = crawl_data.json()

        return json_data

    def process_info(self, regeo_info, batch):

        if 'regeocode' in regeo_info:
            road_map = {}
            poi_map = {}

            # print('第%d个数据爬取成功' % batch)

            road_info = regeo_info["regeocode"]

            road_map['FrameID'] = self.df.loc[batch, 'FrameID']

            if 'addressComponent' in road_info:

                addressComponent = road_info['addressComponent']
                # roadinters = road_info['roadinters'][0]

                country = addressComponent.get('country')
                province = addressComponent.get('province')
                city = addressComponent.get('city')
                district = addressComponent.get('district')

                road_map['Country'] = country
                road_map['Provice'] = province
                road_map['City'] = city
                road_map['District'] = district

            if 'roadinters' in road_info:
                roadinters = road_info['roadinters']

                if len(roadinters) != 0:
                    roadinter = roadinters[0]

                    direction = roadinter.get('direction')
                    distance = roadinter.get('distance')
                    first_name = roadinter.get('first_name')
                    second_name = roadinter.get('second_name')

                    road_map['RoadinterDistance'] = distance
                    road_map['RoadinterDirection'] = direction
                    road_map['RoadinterFirstName'] = first_name
                    road_map['RoadinterSecondName'] = second_name

            road_map.update({k: '' for k, v in road_map.items() if isinstance(v, list) and len(v)==0})
            self.road_df = self.road_df.append(pd.DataFrame(road_map, index=[0]), ignore_index=True)

            if 'pois' in road_info:
                pois = road_info['pois']

                if len(pois) != 0:

                    for k in range(len(pois)):
                        pois_info = pois[k]

                        poi_type = pois_info.get('type')
                        poi_name = pois_info.get('name')
                        poi_direction = pois_info.get('direction')
                        poi_distance = pois_info.get('distance')

                        poi_map['FrameID'] = self.df.loc[batch, 'FrameID']
                        poi_map['POIType'] = poi_type
                        poi_map['POIName'] = poi_name
                        poi_map['POIDistance'] = poi_distance
                        poi_map['POIDirection'] = poi_direction

                        self.poi_df = self.poi_df.append(pd.DataFrame(poi_map, index=[0]), ignore_index=True)
        # else:
        #     print('第%d批数据爬取失败' % batch)
