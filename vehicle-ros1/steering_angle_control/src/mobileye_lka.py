#!/usr/bin/env python3 

import rospy 
from mobileye_560_660_msgs.msg import * 
import numpy as np 
from visualization_msgs.msg import MarkerArray, Marker
from geometry_msgs.msg import Point
import matplotlib.pyplot as plt 
from std_msgs.msg import Float32
from roscco.msg import ThrottleCommand

rospy.init_node('GrabMobileye')

class Lane:

    def __init__(self):

        self.curr_speed = 0.0
        self.error_front_axle = 0.0 
        self.theta_d = 0.0 
        self.target_speed = 10.5
        
        self.sub1 = rospy.Subscriber('/as_tx/lane_markers',Marker, self.lane_markers_cb)
        self.pub1 = rospy.Publisher('/markers_len2', Marker, queue_size=10)
        self.pub2 = rospy.Publisher('/center_path_pts', Point, queue_size=10)
        self.pub_desired_angle = rospy.Publisher('/steering_angle/desired', Float32, queue_size=10)
        self.speed_can = rospy.Subscriber('/can_frame_speed', Float32, self.speed_cb)
        self.sub_can_angle = rospy.Subscriber('/can_frame_angle', Float32, self.can_angle_cb)
        self.pub_throttle = rospy.Publisher('/throttle_command', ThrottleCommand, queue_size=10)
        self.target_speed_pub = rospy.Publisher('/target_speed_reach', ThrottleCommand, queue_size=10)
        
        self.pub_error_front_axle = rospy.Publisher('/error_front_axle', Float32, queue_size=10)
        
        # self.target_speed_pub = rospy.Publisher('/target_speed_reach', ThrottleCommand, queue_size=10)
        
        self.left = []
        self.right = []
        
        self.ir = 0
        self.il = 0

        self.left_inititialized = False
        self.right_initialized = False
        
        
    def lane_markers_cb(self,msg):

        marker_msg = Marker()
                
        try:
            
            if msg.id == 0 or msg.id == 1:
                
                if msg.id == 1 and len(msg.points) == 62:
                    
                    self.right_initialized = True
                    
                    self.right = msg.points
                    
                elif msg.id == 0 and len(msg.points) == 62:
                    
                    self.left_inititialized = True
                    
                    self.left = msg.points
  
                elif msg.id == 1 and len(msg.points) != 62:   

                    if len(self.right) != 62 and self.right_initialized == False: 

                        ctr = 0.0
                        
                        while self.ir < 62:
                            
                            pt_emp = Point() 
                            pt_emp.x = ctr + 0.5
                            pt_emp.y = -1.7
                            pt_emp.z = 0.0
                            
                            self.right.append(pt_emp)

                            self.ir += 1 
                            ctr += 0.5
                            
                        print('Using default points right points as invalid right lane detected')
                     
                    self.right = self.right
                             
                    pt = Point()
                    
                    pt.x = 0
                    pt.y = 0
                    pt.z = 0
                    self.pub2.publish(pt)
                    
                    print('Using previous right points as invalid right lane detected')
                
                elif msg.id == 0 and len(msg.points) != 62:
                    
                    if len(self.left) != 62 and self.left_inititialized == False:
                        
                        ctl = 0.0
                        
                        while self.il < 62:
                            
                            pt_empl = Point() 
                            pt_empl.x = ctl + 0.5
                            pt_empl.y = +1.7
                            pt_empl.z = 0.0
                            
                            self.left.append(pt_empl)

                            self.il += 1 
                            ctl += 0.5
                            
                        print('Using default left points as invalid left lane detected')
                    
                    self.left = self.left
                    
                    pt = Point()
                    
                    pt.x = 0
                    pt.y = 0
                    pt.z = 0
                    self.pub2.publish(pt)

                    print('Using previous left points as invalid left lane detected')
                    

                for i,(pts_l, pts_r) in enumerate(zip(self.left, self.right)):

                    pt = Point()
                    marker_msg.header.stamp = rospy.Time.now()
                    marker_msg.header.frame_id = 'me_viz'
                    marker_msg.id = 0
                    marker_msg.type = Marker.POINTS

                    marker_msg.scale.x = 0.31
                    marker_msg.scale.y = 0.3
                    marker_msg.scale.z = 0.3

                    marker_msg.color.r = 1.0
                    marker_msg.color.g = 0.0 
                    marker_msg.color.b = 1.0 
                    marker_msg.color.a = 1.0

                    pt.x = (pts_l.x + pts_r.x) / 2.0
                    pt.y = (pts_l.y + pts_r.y) / 2.0
                    pt.z = (pts_l.z + pts_r.z) / 2.0 
                    
                    # ct = 0.64   
                    
                    # ld = int(ct * self.target_speed)

                    if i == 32:
                        
                        line_marker = Marker()
                        line_marker.header.stamp = rospy.Time.now()
                        line_marker.header.frame_id = 'me_viz'
                        line_marker.id = 1
                        line_marker.type = Marker.LINE_STRIP

                        line_marker.scale.x = 0.1  # Thickness of the line
                    
                        line_marker.color.r = 1.0
                        line_marker.color.g = 1.0 
                        line_marker.color.b = 1.0 
                        line_marker.color.a = 1.0

                        p1 = Point()
                        p2 = Point()
                        p1.x = pts_l.x
                        p1.y = pts_l.y
                        p1.z = pts_l.z
                        p2.x = pts_r.x
                        p2.y = pts_r.y
                        p2.z = pts_r.z

                        line_marker.points.append(p1)
                        line_marker.points.append(p2)
                        self.pub1.publish(line_marker)
                        
                        k = 0.75
                        
                        ks = 0
                        
                        self.error_front_axle = self.calc_target_idx(0,0,0,pt.x,pt.y)
                        
                        front_axle_error_msg = Float32()
        
                        front_axle_error_msg.data = -self.error_front_axle
                        
                        self.pub_error_front_axle.publish(front_axle_error_msg)
                        
                        if self.curr_speed < 0.1: 
                            self.theta_d = 0.0
                          
                        else: 
                            self.theta_d = np.arctan2(k * -self.error_front_axle, ks + self.curr_speed)
                            self.theta_d = np.clip(self.theta_d, np.deg2rad(-20),np.deg2rad(20))

                    print('Front Axle Error : ', self.error_front_axle)
                        
                    self.pub2.publish(pt)
                    # use deque here instead of list 
                    
                    marker_msg.points.append(pt)

                    marker_msg.lifetime = rospy.Duration(0.1)
        
            self.pub1.publish(marker_msg)
            
            
            # if msg.id == 0 or msg.id == 1:
                
            #     if msg.id == 0 and len(msg.points) == 62:
            #         self.right = msg.points
            #     elif msg.id == 1 and len(msg.points) == 62:
            #         self.left = msg.points
                    
            #     elif msg.id == 0 and len(msg.points) != 62:
                    
            #         self.right = self.right
                    
            #         pt = Point()
                    
            #         pt.x = 0
            #         pt.y = 0
            #         pt.z = 0
            #         self.pub2.publish(pt)
                    
            #         self.theta_d = self.theta_d
        
            #         raise Exception('Invalid right lane')
                
            #     elif msg.id == 1 and len(msg.points) != 62:
                    
            #         self.left = self.left
                    
            #         pt = Point()
                    
            #         pt.x = 0
            #         pt.y = 0
            #         pt.z = 0
            #         self.pub2.publish(pt)
                    
            #         self.theta_d = self.theta_d
                    
            #         raise Exception('Invalid left lane')

            #     for i,(pts_l, pts_r) in enumerate(zip(self.left, self.right)):

            #         pt = Point()
            #         marker_msg.header.stamp = rospy.Time.now()
            #         marker_msg.header.frame_id = 'me_viz'
            #         marker_msg.id = 0
            #         marker_msg.type = Marker.POINTS

            #         marker_msg.scale.x = 0.31
            #         marker_msg.scale.y = 0.3
            #         marker_msg.scale.z = 0.3

            #         marker_msg.color.r = 1.0
            #         marker_msg.color.g = 0.0 
            #         marker_msg.color.b = 1.0 
            #         marker_msg.color.a = 1.0

            #         pt.x = (pts_l.x + pts_r.x) / 2.0
            #         pt.y = (pts_l.y + pts_r.y) / 2.0
            #         pt.z = (pts_l.z + pts_r.z) / 2.0   


            #         if i == 15:
                        
            #             # print(f'left lane pts x : {pts_l.x}, y : {pts_l.y}, z : {pts_l.z}')
            #             # print(f'right lane pts x : {pts_r.x}, y : {pts_r.y}, z : {pts_r.z}')
            #             # print(f'x : {pt.x}, y : {pt.y}, z : {pt.z}')
                        
            #             line_marker = Marker()
            #             line_marker.header.stamp = rospy.Time.now()
            #             line_marker.header.frame_id = 'me_viz'
            #             line_marker.id = 1
            #             line_marker.type = Marker.LINE_STRIP

            #             line_marker.scale.x = 0.1  # Thickness of the line
                    
            #             line_marker.color.r = 1.0
            #             line_marker.color.g = 1.0 
            #             line_marker.color.b = 1.0 
            #             line_marker.color.a = 1.0

            #             p1 = Point()
            #             p2 = Point()
            #             p1.x = pts_l.x
            #             p1.y = pts_l.y
            #             p1.z = pts_l.z
            #             p2.x = pts_r.x
            #             p2.y = pts_r.y
            #             p2.z = pts_r.z

            #             line_marker.points.append(p1)
            #             line_marker.points.append(p2)
            #             self.pub1.publish(line_marker)
                        
            #             k = 0.75
                        
            #             ks = 0
                        
            #             self.error_front_axle = self.calc_target_idx(0,0,0,pt.x,pt.y)
                        
            #             if self.curr_speed < 0.1: 
            #                 self.theta_d = 0.0
                          
            #             else: 
            #                 self.theta_d = np.arctan2(k * -self.error_front_axle, ks + self.curr_speed)
            #                 self.theta_d = np.clip(self.theta_d, np.deg2rad(-15),np.deg2rad(15))

            #         print('Front Axle Error : ', self.error_front_axle)
                        
            #         self.pub2.publish(pt)
            #         # use deque here instead of list 
        
            #         marker_msg.points.append(pt)

            #         marker_msg.lifetime = rospy.Duration(0.1)
        
            # self.pub1.publish(marker_msg)
            

        except Exception as e:
            print(e)
            
            
    def can_angle_cb(self,msg):
        
        steering_angle_msg = Float32()
        
        steering_angle_msg.data = -self.theta_d
        
        self.pub_desired_angle.publish(steering_angle_msg)
        
     
    def speed_cb(self,msg):
        
        self.curr_speed = float(msg.data)
        
        # throttle_msg = ThrottleCommand()

        self.speed = msg.data
        
        msg1 = ThrottleCommand()
        msg1.header.stamp = rospy.Time.now()
        msg1.throttle_position = self.target_speed
        self.target_speed_pub.publish(msg1)
       
        ### We can apply throttle / brake from here 

        # throttle_msg.throttle_position = 0.13
        
        # self.pub_throttle.publish(throttle_msg)
              
    def calc_target_idx(self, x,y, yaw, cx, cy):
            
        fx = x
        fy = y
        
        dx = fx - cx
        dy = fy - cy 

        front_axle_vec = [
            -np.cos(yaw + (np.pi / 2)),
            -np.sin(yaw + (np.pi / 2)),
        ]

        error_front_axle = np.dot([dx, dy], front_axle_vec)
        
        return error_front_axle


if __name__ == "__main__":

    l = Lane()
    rospy.spin()