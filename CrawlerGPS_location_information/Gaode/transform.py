import requests


class Transform(object):
    ''' 坐标转换 '''

    def __init__(self, df, key_df, transform_max):
        self.df = df
        self.key_df = key_df
        self.transform_max = transform_max

    def controller(self):
        print('正在转换坐标')

        key_list = self.key_df[self.key_df['transform_count'] < self.transform_max].index.values.tolist()

        try:
            for i in range(self.df.shape[0]):
                # 拼接地址
                road_url = self.get_road_url(self.df.loc[i, 'coordinate'], key_list[0])

                # print(road_url)

                coordinate_json = self.crawler(road_url)
                #
                self.df.loc[i, 'coordinate'] = self.process_info(coordinate_json)

                try:
                    if int(self.key_df.loc[key_list[0], 'transform_count']) < self.transform_max:
                        pass
                    else:
                        del key_list[0]

                    self.key_df.loc[key_list[0], 'transform_count'] += 1

                except:
                    print('出现错误的元素是%s' % str(road_url))
                    continue
        finally:
            # self.key_df.to_excel(self.key_file)
            print('所有坐标转换已完成')
            return self.df, self.key_df

    def get_road_url(self, coordinate, key_info):
        '''
        拼接抓路url
        https://restapi.amap.com/v3/assistant/coordinate/convert?locations=116.481499,39.990475&coordsys=gps&output=json&key=<用户的key>
        :return:
        '''
        #
        head = 'https://restapi.amap.com/v3/assistant/coordinate/convert?coordsys=gps&output=json'
        location = f"locations={coordinate}"
        key = f"key={key_info}"

        url = f"{head}&{location}&{key}"

        return url

    def crawler(self, url):

        crawl_data = requests.get(url)

        json_data = crawl_data.json()

        return json_data

    def process_info(self, coordinate_json):

        road_info = coordinate_json['locations']
        # print(road_info)

        return f"{format(float(road_info.split(',')[0]), '.6f')},{format(float(road_info.split(',')[1]), '.6f')}"