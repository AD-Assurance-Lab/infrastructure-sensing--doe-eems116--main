#!/usr/bin/env python3

import rospy
import cantools
import numpy as np
import sys
from pid import *
from std_msgs.msg import Float64, Float32
from roscco.msg import SteeringCommand

class NODE():

    def __init__(self):

        self.received = False

        self.currAngle = 0.0
        self.setpoint = 0.0

        rospy.init_node("steering_angle_control")
        rospy.Subscriber("/can_frame_angle", Float32, self.angle_callback)
        rospy.Subscriber("/steering_angle/desired", Float32, self.desAngle_callback)
        self.pub = rospy.Publisher("/steering_command", SteeringCommand, queue_size=10)
        rospy.Subscriber("/error_front_axle", Float32, self.front_axle_err_cb)
        
        self.rate = rospy.Rate(50)

        self.pid = PID(P=3.0, I=0.5, D=1.5)
        # self.pid = PID(P=3.2, I=0.5, D=0.4)
        self.pid.set_limits( -0.3, 0.3 ) 

        self.run()
        
    def front_axle_err_cb(self,msg):
        
        self.error_front_axle = msg.data
        
        # if abs(self.error_front_axle) < 0.1:
            
        #     self.pid.set_values(P=3.0, I=0.5, D = 0.5)
        
        # else:
            
        #     self.pid.set_values(P=3.0, I=0.5, D = 1.5)
            
    def desAngle_callback(self, msg):
        # angle in radians
        self.setpoint = msg.data
        self.received = True

    def angle_callback(self, msg):

        self.currAngle = msg.data
    
    def heading_cb(self,msg):
        self.received1 = True
        self.heading = msg.data

    def run(self):

        rospy.loginfo("Starting steering controller")

        while not rospy.is_shutdown():

            if self.received:
                
                msg = SteeringCommand()
                msg.header.stamp = rospy.Time.now()

                torque = self.pid.control(self.currAngle - self.setpoint)

                msg.steering_torque = torque

                print("torque",torque)
                
                self.pub.publish(msg)

                self.rate.sleep()

try:
    NODE()
except rospy.ROSInterruptException:
    pass
