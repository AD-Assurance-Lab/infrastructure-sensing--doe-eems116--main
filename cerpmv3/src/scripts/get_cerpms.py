#!/usr/bin/env python3

import rospy 
import pandas as pd 
from cerpm_data.msg import cerpm_receiver
from cerpmv3.msg import id
import math

rospy.init_node("save_cerpm_info")

local_map_df = pd.read_csv('/home/parth/catkin_ws/src/cerpmv3/src/scripts/resampled_pts.csv').drop('Unnamed: 0', axis=1)
# local_map_df = pd.read_csv('/home/parth/catkin_ws/src/cerpmv3/src/scripts/resampled_pts.csv', names=['id','right_lat', 'right_lon','right_alt','left_lat', 'left_lon','left_alt','heading'])

print(local_map_df)

cerpm_dict = {}
cerpm_pose = {}

max_iterations_without_new_cerpm = 50

class GET_CERPM:

    num_iterations_without_new_cerpm = 0 
    
    def __init__(self):
        
        rospy.Subscriber("/received_cerpmids", id, self.cerpm_callback)
        
        self.ct_r = 1 # set to 1 default
        self.ct_l = 2 # set to 2 default    

    def cerpm_callback(self,msg):
        
        rospy.loginfo_once("Getting all cerpm data")
        rospy.loginfo(cerpm_dict)
            
        if msg.id not in cerpm_dict.keys():

            if msg.id % 2 == 0:
                print(msg.id)
                cerpm_dict[msg.id] = (f'LEFT_{int(msg.id/2)}')
            else:
                cerpm_dict[msg.id] = ( f'RIGHT_{math.ceil(msg.id/2)}')
            GET_CERPM.num_iterations_without_new_cerpm = 0

        else:
            GET_CERPM.num_iterations_without_new_cerpm +=1 
            
        if GET_CERPM.num_iterations_without_new_cerpm >= max_iterations_without_new_cerpm:
            
            data = list(cerpm_dict.items())
            df = pd.DataFrame(data, columns=['ID', 'CERPM_NAME'])
            
            for i,rows in df.iterrows():
                #left
                if (rows['ID']) % 2 == 0:
                    # print(rows['ID']) 
                    pose_info = local_map_df[local_map_df['left_id'] == int(rows['ID']) ]
                    cerpm_pose[rows['ID']] = (rows['ID'],pose_info['left_lat'].values[0], pose_info['left_lon'].values[0], pose_info['left_alt'].values[0],rows['CERPM_NAME'])
                # right
                else:
                    pose_info = local_map_df[local_map_df['right_id'] == int(rows['ID']) ]
                    cerpm_pose[rows['ID']] = (rows['ID'],pose_info['right_lat'].values[0], pose_info['right_lon'].values[0], pose_info['right_alt'].values[0],rows['CERPM_NAME'])     
                
            new_df = pd.DataFrame.from_dict(cerpm_pose, orient='index',columns=['id','lat','lon','alt','name'])
            new_df.to_csv('/home/parth/catkin_ws/src/cerpmv3/src/scripts/saved_cerps.csv', index=False)
                    
            rospy.signal_shutdown("Maximum iterations reached") 
            
if __name__ == "__main__":

    cp = GET_CERPM()
    rospy.spin()
    
    