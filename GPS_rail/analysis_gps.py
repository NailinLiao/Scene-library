from math import sin, asin, cos, radians, fabs, sqrt

EARTH_RADIUS = 6371.137  # 地球平均半径大约6371km





def get_distance_hav(lat0, lng0, lat1, lng1):
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


if __name__ == "__main__":
    # place_centre = [117.2704798, 38.8785637]
    # door_center = [117.2704748, 38.882579]
    result = get_distance_hav(38.8785637, 117.2704798, 38.882579, 117.2704748)
    print(result)
    print("距离：{:.3}km".format(result))
