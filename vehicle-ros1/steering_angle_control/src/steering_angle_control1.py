#!/usr/bin/env python3

import rospy
import cantools
import numpy as np
import sys
from pid import *
from roscco.msg import EnableDisable

from std_msgs.msg import Float64, Float32
from roscco.msg import SteeringCommand

class NODE():

    def __init__(self):

        self.received = False

        self.currAngle = 0.0
        self.setpoint = 0.0

        rospy.init_node("steering_angle_control")

        self.pub_enable_disable = rospy.Publisher('/enable_disable', EnableDisable, queue_size=10)
        rospy.Subscriber("/can_frame_angle", Float32, self.angle_callback)
        rospy.Subscriber("/steering_angle/desired", Float32, self.desAngle_callback)
        self.pub = rospy.Publisher("/steering_command", SteeringCommand, queue_size=10)

        self.rate = rospy.Rate(50)

        self.pid = PID(P=2.0, I=0.5, D=0.1) # dt is 1/rate
        self.pid.set_limits( -0.2, 0.2 )

        self.run()

    def desAngle_callback(self, msg):
        # angle in radians
        self.setpoint = msg.data
        self.received = True

    def angle_callback(self, msg):

        self.currAngle = msg.data

    def run(self):

        rospy.loginfo("Starting steering controller")

        enab_disab_msg = EnableDisable()

        enab_disab_msg.enable_control = 'true'

        self.pub_enable_disable.publish(enab_disab_msg)

        while not rospy.is_shutdown():

            if self.received:
                
                msg = SteeringCommand()
                msg.header.stamp = rospy.Time.now()

                torque = self.pid.control(self.currAngle - self.setpoint)

                msg.steering_torque = torque

                print(self.currAngle - self.setpoint)
                
                self.pub.publish(msg)

                self.rate.sleep()

try:
    NODE()
except rospy.ROSInterruptException:
    pass
