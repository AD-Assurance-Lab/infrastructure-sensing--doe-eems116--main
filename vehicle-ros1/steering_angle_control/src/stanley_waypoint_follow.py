#!/usr/bin/env python3 

import rospy 
import numpy as np 
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Float32
import pymap3d as p3d 
import csv
from pid import PID
import pandas as pd
from roscco.msg import SteeringCommand, ThrottleCommand, ThrottleReport, BrakeCommand
from piksi_rtk_msgs.msg import BaselineHeading, WMUNavSatFix
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
from matplotlib import style 

rospy.init_node("follow_waypoints")

csv_file = '/home/parth/Desktop/soul_gps_v2.csv'

df = pd.read_csv(csv_file, header=None, names=['latitude', 'longitude', 'altitude', 'heading'], index_col=False)

first_pt = rospy.wait_for_message("/piksi_multi_base_station/navsatfix_best_fix", WMUNavSatFix)

print(first_pt)

lat0 = first_pt.latitude 
lon0 = first_pt.longitude 
alt0 = first_pt.altitude 

waypoints = []

for index, row in df.iterrows():

    x_local, y_local, z_local = p3d.geodetic2ned(row['latitude'], row['longitude'], row['altitude'], lat0, lon0, alt0)

    waypoints.append([x_local, y_local, z_local, row['heading']])

waypoints = np.array(waypoints)

x_data = []
y_data = []

class Follower:

    def __init__(self, *args, **kwargs):

        self.topic_name = topic_name 
        self.data_class = data_class 

        # self.pid_heading = PID(P=4.5, I=0.5, D=0.01) niro values 
        self.pid_heading = PID(P=0.1, I=0.0, D=0.0)
        
        self.pid_heading.set_limits(lower=-0.1, upper=0.1)

        heading_msg = rospy.wait_for_message("/piksi/baseline_heading", BaselineHeading)
        self.heading_rad = np.deg2rad(heading_msg.heading/1000)

        self.sub = rospy.Subscriber(self.topic_name, self.data_class, self.follow_cb)
        self.sub_heading = rospy.Subscriber('/piksi/baseline_heading', BaselineHeading, self.heading_cb)
        self.speed_can = rospy.Subscriber('/can_frame_speed', Float32, self.speed_cb )

        self.pub_throttle = rospy.Publisher('/throttle_command', ThrottleCommand, queue_size=10)
        self.pub_brake = rospy.Publisher('/brake_command', BrakeCommand, queue_size=10)
        self.pub_steer = rospy.Publisher('/steering_command', SteeringCommand, queue_size=10)
        self.pub_desired_angle = rospy.Publisher('/steering_angle/desired', Float32, queue_size=10)
        self.pub_heading_error = rospy.Publisher('/heading_error',Float32,queue_size=10)

        self.rate = rospy.Rate(25)

        figure = plt.figure()
        animation = FuncAnimation(figure, self.update, interval=50)
        plt.show()

    def follow_cb(self,msg):

        steering_angle_msg = Float32()
        heading_error_msg = Float32()

        ### Compute NED coords using current lat long and first lat long 

        curr_lat = msg.latitude
        curr_lon = msg.longitude 
        curr_alt = msg.altitude 

        self.x_curr, self.y_curr, z_curr = p3d.geodetic2ned(curr_lat, curr_lon, curr_alt, lat0, lon0, alt0)
        
        ## lookahead distance stuff 

        if self.speed < 0.1: 
            lookahead_distance = 1.0
        else:
            lookahead_distance = 1.5 * self.speed

        ### Compute the crosstrack error at the front axle of the vehicle 

        error_front_axle = self.calc_target_idx(self.x_curr, self.y_curr, self.heading_rad, waypoints[:,0], waypoints[:,1], lookahead_distance)

        # print('error front axle:',error_front_axle)

        k = 0.75

        ## Convert it to angle using the equation from the stanley controller

        ks = 0  # softeneing coefficient 

        if self.speed < 0.1: 
            theta_d = 0.0
            theta_e = 0.0
        else: 
            theta_e = self.normalize_angle(waypoints[self.heading_target_idx,3] - self.heading_rad)
            theta_d = np.arctan2(k * -error_front_axle, ks + self.speed)
            theta_d = np.clip(theta_d, np.deg2rad(-35),np.deg2rad(35))
            # theta_d = np.clip(theta_d, np.deg2rad(-60),np.deg2rad(60))

        # delta = theta_e + theta_d
        # print("heading error:", theta_e)
        delta =  theta_d

        he =self.pid_heading.control(error=theta_e)

        # print("PID Heading",he)

        # print(waypoints[self.heading_target_idx,4] - self.heading_rad)

        ### send it to steering angle message which will inturn publish it to the PID 

        steering_angle_msg.data = delta
        # heading_error_msg.data = he

        self.pub_desired_angle.publish(steering_angle_msg)
        # self.pub_heading_error.publish(heading_error_msg)
        
        print("------------------")
        print(f"steering angle msg: {steering_angle_msg.data}")
        print("------------------")
        self.pub_steer.publish(SteeringCommand(steering_torque=he))

        # print(throttle_msg.throttle_position)


    def normalize_angle(self,angle):

        while angle > np.pi:

            angle -= 2.0 * np.pi

        while angle < -np.pi:
            
            angle += 2.0 * np.pi
        
        return angle
        
    
    def commands(self,val):

        if val < 0:
            throttle = 0.0
            if -1.0 <= val <= 0.0:
                brake = -val
            else:
                brake = 0.8 # full brake
        elif 0.0 <= val <= 1.0:
            throttle = val
            brake = 0.0
        else: # ysat > 1.0
            throttle = 1.0
            brake = 0.0

        return np.clip(throttle, 0.0, 0.2), np.clip(brake, 0.0, 0.2)

  
    def heading_cb(self,msg):

        heading = msg.heading

        self.heading_rad = np.deg2rad(heading/1000)


    def speed_cb(self,msg):

        # brake_msg = BrakeCommand()
        throttle_msg = ThrottleCommand()
        throttle_msg.header.frame_id = 'soul_steer'

        self.speed = msg.data
        ### We can apply throttle / brake from here 

        throttle_msg.throttle_position = 0.09
        
        self.pub_throttle.publish(throttle_msg)
        # self.pub_brake.publish(brake_msg)


    def calc_target_idx(self, x,y, yaw, cx, cy, lookahead_distance):

        fx0 = x
        fy0 = y
        
        fx = x + lookahead_distance * np.cos(yaw)
        fy = y + lookahead_distance * np.sin(yaw)

        dx = [fx - icx for icx in cx]
        dy = [fy - icy for icy in cy]

        dx0 = [fx0 - icx for icx in cx]
        dy0 = [fy0 - icy for icy in cy]

        d = np.hypot(dx, dy)
        d0 = np.hypot(dx0, dy0)

        self.target_idx = np.argmin(d)
        self.heading_target_idx = np.argmin(d0)

        front_axle_vec = [
            -np.cos(yaw + (np.pi / 2)),
            -np.sin(yaw + (np.pi / 2)),
        ]

        self.target_speed = waypoints[self.target_idx,3]

        error_front_axle = np.dot([dx[self.target_idx], dy[self.target_idx]], front_axle_vec)
        
        return error_front_axle
    

    def update(self, frame):
        
        plt.clf()
        plt.plot( waypoints[:, 0], waypoints[:, 1] )

        plt.scatter(self.x_curr, self.y_curr, c = 'orange')
        plt.scatter(waypoints[self.target_idx, 0], waypoints[self.target_idx, 1], c='r')
        plt.xlabel("x (m)")
        plt.ylabel("y (m)")

        plt.grid()


if __name__ == "__main__":

    topic_name = '/piksi_multi_base_station/navsatfix_best_fix'
    data_class =  WMUNavSatFix

    ls = Follower(topic_name, data_class)
    rospy.spin()
