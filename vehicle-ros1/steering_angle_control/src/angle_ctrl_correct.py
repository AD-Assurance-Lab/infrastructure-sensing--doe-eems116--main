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

        self.rate = rospy.Rate(10)

        # self.pid = PID(P=4.0, I=0.5, D=0.07) # dt is 1/rate for stanley works well
        self.pid = PID(P=1.5, I=0.1, D=0.05)
        # self.pid.set_limits( -0.4, 0.4 ) for cermps works well
        self.pid.set_limits( -0.3, 0.3) 

        self.run()

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
                
                if abs(torque) > 0.15:

                    msg.steering_torque = -torque

                    print("torque",torque)
                
                    self.pub.publish(msg)
                
                else:
                    
                    pass

                self.rate.sleep()

try:
    NODE()
except rospy.ROSInterruptException:
    pass
