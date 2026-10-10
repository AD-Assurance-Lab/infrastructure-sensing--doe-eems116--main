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


resampled_df = pd.read_csv('resampled_pts.csv').drop('Unnamed: 0',axis=1)

right_pts = []
left_pts = []

for row,column in resampled_df.iterrows():
    
    right_pts.append([column['right_lat'], column['right_lon']])
    left_pts.append([column['left_lat'], column['left_lon']])

right_pts = np.array(right_pts)
left_pts = np.array(left_pts)

# for pt in right_pts:
#     idxs = resampled_df[(resampled_df['right_lat'] == pt[0]) & (resampled_df['right_lon'] == pt[1])]
#     print(idxs['right_id'].item())


# exit()


rospy.init_node('CERPM_REAL_TIME')

class CERPMS:

    def __init__(self):

        self.rt_pts = sorted([])
        self.lft_pts = sorted([])
        self.gps_points = sorted([])

        self.ini_pose = rospy.wait_for_message('/piksi_multi_base_station/navsatfix_best_fix', WMUNavSatFix) 
        # self.lat0 = self.ini_pose.latitude
        # self.lon0 = self.ini_pose.longitude
        # self.alt0 = self.ini_pose.altitude
        
        if self.ini_pose: 
            print('in msg')
            rospy.Subscriber('/piksi_multi_base_station/navsatfix_best_fix', WMUNavSatFix, self.gps_cb)
            figure = plt.figure()
            animation = FuncAnimation(figure, self.update, interval=20)
            plt.show()

    def gps_cb(self,msg):
        
        # self.x_curr, self.y_curr, self.z_curr = p3d.geodetic2ned(msg.latitude, msg.longitude, msg.altitude, self.lat0, self.lon0, self.alt0)
        self.x_curr = msg.latitude
        self.y_curr = msg.longitude

    def update(self,frame):

        try:
            
            plt.clf()
            plt.scatter(right_pts[:,1], right_pts[:,0], c='orange', s=7)
            plt.scatter(left_pts[:,1], left_pts[:,0], c='blue', s=7)
            
            # Remove if does not work, experimnental
            #-------------------------------------------------------------------#
            for pt in right_pts:
                idxs = resampled_df[(resampled_df['right_lat'] == pt[0]) & (resampled_df['right_lon'] == pt[1])]
                plt.text(pt[1], pt[0], str(idxs['right_id'].item()))
                # print(idxs['right_id'].item())

            for pt in left_pts:
                idxs = resampled_df[(resampled_df['left_lat'] == pt[0]) & (resampled_df['left_lon'] == pt[1])]
                plt.text(pt[1], pt[0], str(idxs['left_id'].item()))
                # print(idxs['left_id'].item())
            #-------------------------------------------------------------------#
            
            plt.scatter(self.y_curr, self.x_curr, c='green',s=7)
            plt.grid(True)
            
            zoom_window_size = 0.0001  # Adjust this value as needed
            
            # Set the limits for the zoom window
            plt.xlim(self.y_curr - zoom_window_size, self.y_curr + zoom_window_size)
            plt.ylim(self.x_curr - zoom_window_size, self.x_curr + zoom_window_size)
            
            plt.xlabel('x')
            plt.ylabel('y')

        except Exception as e:
            pass
            

if __name__ == "__main__":

    cp = CERPMS()

    rospy.spin()

