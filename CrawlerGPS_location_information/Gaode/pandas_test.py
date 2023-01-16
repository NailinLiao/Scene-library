import pandas as pd


# road_columns = ['FrameID', 'Country', 'Provice', 'City', 'District', 'RoadinterDistance', 'RoadinterDirection',
#                         'RoadinterFirstName', 'RoadinterSecondName']
# road_df = pd.DataFrame(columns=road_columns)
# road_map = {'FrameID': 0, 'Country': '中国', 'Provice': '北京市', 'City': [], 'District': '通州区', 'RoadinterDistance': '58.3858', 'RoadinterDirection': '东', 'RoadinterFirstName': '马驹桥中学路', 'RoadinterSecondName': '四支路北段'}
# # road_df = road_df.append(pd.DataFrame(road_map, index=[0]), ignore_index=True)
# #
# # print(road_df)
#
# dict1 = {'country': '中国', 'province': '北京市', 'city': [], 'citycode': '010'}
# # for k, v in dict1.items():
# #     if isinstance(v, list) and len(v)==0:
# #         dict1[k] = ''
# #
# # print(dict1)
#
# road_map.update({k: '' for k, v in road_map.items() if isinstance(v, list) and len(v)==0})
# road_df = road_df.append(pd.DataFrame(road_map, index=[0]), ignore_index=True)
# print(road_df)

with open('traceback_INFO.txt', 'a+') as f:
    content = 'bmw'
    f.writelines(f'{content}\r\n')

with open('traceback_INFO.txt', 'a+') as f:
    content = 'bmw1'
    f.writelines(f'{content}\r\n')
