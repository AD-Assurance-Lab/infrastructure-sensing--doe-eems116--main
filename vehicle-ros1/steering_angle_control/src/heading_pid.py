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

        rospy.init_node("steering_angle_heading")
        rospy.Subscriber('/heading_error',Float32,self.heading_cb)
        self.pub = rospy.Publisher("/steering_command", SteeringCommand, queue_size=10)

        self.rate = rospy.Rate(50)

        self.run()

    def heading_cb(self,msg):
        self.received1 = True
        self.heading = msg.data

    def run(self):

        rospy.loginfo("Starting heading pid")

        while not rospy.is_shutdown():

            if self.received:
                
                msg = SteeringCommand()
                msg.header.stamp = rospy.Time.now()
                msg.header.frame_id = 'soul_steer'
                msg.steering_torque = self.heading
                self.pub.publish(msg)
                self.rate.sleep()

try:
    NODE()
except rospy.ROSInterruptException:
    pass
