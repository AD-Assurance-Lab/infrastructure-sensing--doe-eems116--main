#!/usr/bin/env python3 

import rospy 
import numpy as np 
from cerpmv3.msg import id
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
from piksi_rtk_msgs.msg import WMUNavSatFix
import pymap3d as p3d
from scipy.interpolate import interp1d
import pandas as pd

cerpm_dict = {}
cerpm_dict.clear()

cerpm_df = pd.read_csv('saved_cerps.csv')

for row,column in cerpm_df.iterrows():

    cerpm_dict[column.id] = [column.lat, column.lon, column.alt] 
    
rospy.init_node('CERPM_REAL_TIME')

class CERPMS:

    def __init__(self):

        self.rt_pts = sorted([])
        self.lft_pts = sorted([])
        self.gps_points = sorted([])

        self.ini_pose = rospy.wait_for_message('/piksi_multi_base_station/navsatfix_best_fix', WMUNavSatFix) 
        self.lat0 = self.ini_pose.latitude
        self.lon0 = self.ini_pose.longitude
        self.alt0 = self.ini_pose.altitude
        
        msg = rospy.wait_for_message('/received_cerpmids', id)
        
        if msg: 
            print('in msg')
            rospy.Subscriber('/received_cerpmids', id, self.cerpm_cb)
            rospy.Subscriber('/piksi_multi_base_station/navsatfix_best_fix', WMUNavSatFix, self.gps_cb)
            figure = plt.figure()
            animation = FuncAnimation(figure, self.update, interval=20)
            plt.show()

    def cerpm_cb(self, msg):
        
        latitude = cerpm_dict[msg.id][0]
        longitude = cerpm_dict[msg.id][1]
        altitude = cerpm_dict[msg.id][2]
        
        if msg.id % 2 == 1:
            
            x_local, y_local, z_local = p3d.geodetic2ned(latitude, longitude, altitude, self.lat0, self.lon0, self.alt0)
            if [x_local,y_local, z_local] not in self.rt_pts:
                self.rt_pts.append([x_local, y_local, z_local])
        
        elif msg.id % 2 == 0:
            
            x_local, y_local, z_local = p3d.geodetic2ned(latitude, longitude, altitude, self.lat0, self.lon0, self.alt0)
            if [x_local,y_local, z_local] not in self.rt_pts:
                self.lft_pts.append([x_local, y_local, z_local])
            

    def gps_cb(self,msg):
        
        self.x_curr, self.y_curr, self.z_curr = p3d.geodetic2ned(msg.latitude, msg.longitude, msg.altitude, self.lat0, self.lon0, self.alt0)
        
        # self.gps_points.append([self.x_curr, self.y_curr])

    def update(self,frame):

        try:

            right_pts_arr = np.array(self.rt_pts)
            left_pts_arr = np.array(self.lft_pts)
            # gps_points_arr = np.array(self.gps_points)
            
            plt.clf()
            plt.scatter(right_pts_arr[:, 1], right_pts_arr[:, 0], c='orange')
            plt.scatter(left_pts_arr[:, 1], left_pts_arr[:, 0], c='blue')
            plt.scatter(self.y_curr, self.x_curr, c='green')
            plt.grid(True)
            plt.xlabel('x')
            plt.ylabel('y')

        except Exception as e:
            pass
            

if __name__ == "__main__":

    cp = CERPMS()

    rospy.spin()

