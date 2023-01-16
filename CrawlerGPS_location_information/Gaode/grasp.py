import pandas as pd
import requests
import traceback


class Grasp():
    ''' 抓路服务 '''

    def __init__(self, df, key_df, grasp_max, save_path):
        self.df = df
        self.key_df = key_df
        self.grasp_max = grasp_max
        self.save_path = save_path
        self.stop = False
        self.save_df = pd.DataFrame(columns=['FrameID', 'RoadName', 'RoadLevel', 'MaxSpeed'])

    def controller(self):

        print('正在抓路')
        key_list = self.key_df[self.key_df['grasp_count'] < self.grasp_max].index.values.tolist()

        try:
            for i in range(self.df.shape[0] // 3):
                # 每三个一组就行zip。然后传送到地址拼接处进行处理
                road_url = self.get_road_url(list(zip(self.df.loc[3 * i, 'info_need'], self.df.loc[3 * i + 1, 'info_need'],
                                            self.df.loc[3 * i + 2, 'info_need'])), key_list[0])

                # print(road_url)

                grasp_info = self.crawler(road_url)

                self.process_info(grasp_info, i)

                try:
                    if int(self.key_df.loc[key_list[0], 'grasp_count']) < self.grasp_max:
                        pass
                    else:
                        del key_list[0]

                    if len(key_list) != 0:

                        self.key_df.loc[key_list[0], 'grasp_count'] += 1
                    else:
                        print('今日抓路次数已用尽')
                        print('最终未处理的文件位置 %s' % self.save_path)
                        self.stop = True
                        break
                except:
                    print('出现错误的元素是%s' % str(road_url))
                    continue

        finally:
            self.save_df.set_index('FrameID', inplace=True)
            # self.save_df.to_excel(f'{self.save_path}_grasp.xlsx')
            print('抓路调用已完成')
            print('抓路文件已存储')

            return self.key_df, self.save_df, self.stop

    def get_road_url(self, zip_info, key_info):
        '''
        拼接抓路url
        :return:
        '''
        #
        head = 'https://restapi.amap.com/v3/autograsp?carid=7e9c123456'
        location = 'locations=%s' % '|'.join(zip_info[0])   # error
        datetime = 'time=%s' % ','.join(zip_info[1])
        direction = 'direction=%s' % ','.join(zip_info[2])
        speed = 'speed=%s' % ','.join(zip_info[3])
        tail = 'extensions=all&output=json'
        key = 'key=%s' % key_info

        url = f"{head}&{location}&{datetime}&{direction}&{speed}&{tail}&{key}"
        # 目前url获取成功，后面的步骤是，读取所有key的列表，通过设定次数上限，每次使用的时候进行记录并判定，保证每次
        # 读取的时候不会因为重复读取不累计次数的情况
        # print(url)
        return url

    def crawler(self, url):

        crawl_data = requests.get(url)

        json_data = crawl_data.json()

        return json_data

    def process_info(self, grasp_info, batch):

        if 'roads' in grasp_info:

            # print('第%d批数据爬取成功' % batch)

            roads_info = grasp_info["roads"]

            for k in range(len(roads_info)):
                road_info = roads_info[k]
                roadname = road_info.get('roadname')

                if type(roadname) == list and len(roadname) == 0:
                    roadname = ''

                roadlevel = road_info.get('roadlevel')
                maxspeed = road_info.get('maxspeed')

                try:
                    # print('第%d个数据, roadname: %s roadlevel: %s maxspeed: %s' % (k, roadname, roadlevel, maxspeed))
                    self.save_df = self.save_df.append(pd.DataFrame({'FrameID': self.df.loc[(3*batch+k), 'FrameID'],
                                                                     'RoadName': roadname, 'RoadLevel': roadlevel,
                                                                     'MaxSpeed': maxspeed}, index=[0]), ignore_index=True)
                    # print(self.save_df)
                except Exception as e:
                    print(str(e))
                    # 以下两步都是输出错误的具体位置的
                    with open('traceback_INFO.txt', 'a+') as f:
                        f.writelines(f'{self.save_path}\r\n')
                    traceback.print_exc(file=open('traceback_INFO.txt', 'a+'))

                # print(self.save_df)

        # else:
        #     print('第%d批数据爬取失败' % batch)
