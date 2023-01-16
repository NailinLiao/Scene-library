import matplotlib.pyplot as plt

import pandas as pd

GPSpath = r"C:\Users\NailinLiao\PycharmProjects\Mark_location\data\ins\ins1\gps_ins.txt"
imudata = pd.read_csv(GPSpath)
# imudata = imudata[(imudata['Lattitude'] > 38.87) & (imudata['Lattitude'] < 38.89)]
# plt.scatter(imudata['Lattitude']*111194.926644, imudata['Longitude']*111194.926644558737, s=0.5, c='black')
# plt.scatter(imudata['Longitude'], imudata['Lattitude'], s=0.5, c='black')
plt.plot(imudata['Longitude'], imudata['Lattitude'], c='black')


plt.axis('equal')
plt.show()
