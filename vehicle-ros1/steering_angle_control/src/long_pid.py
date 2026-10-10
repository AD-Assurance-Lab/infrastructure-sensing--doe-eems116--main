#!/usr/bin/env python3

import rospy
import cantools
import numpy as np
import sys
from pid import *
from std_msgs.msg import Float64, Float32
from roscco.msg import ThrottleCommand, BrakeCommand


class NODE():

    def __init__(self):

        self.received = False
        self.received1 = False

        self.setpoint = 0 
        self.curr_speed = 0
        self.desired_speed = 0

        rospy.init_node("longitudinal_control")
        self.pub = rospy.Publisher("/throttle_command", ThrottleCommand, queue_size=10)
        self.pub1 = rospy.Publisher("/brake_command", BrakeCommand, queue_size=10)
        rospy.Subscriber('/can_frame_speed', Float32, callback=self.speed_cb)
        rospy.Subscriber('/target_speed_reach', ThrottleCommand, callback=self.tgt_cb)

        self.rate = rospy.Rate(50)

        self.pid = PID(P=0.07, I=0.005, D=0.003) # dt is 1/rate
        self.pid.set_limits(-1.0,1.0)

        self.run()

    def speed_cb(self,msg):

        self.received = True
        self.curr_speed = float(msg.data)

    def tgt_cb(self,msg):
        self.received1 = True
        self.desired_speed = msg.throttle_position
    

    def run(self):

        rospy.loginfo("Starting longitudinal controller")
        
        thr_msg = ThrottleCommand()
        brk_msg = BrakeCommand()

        while not rospy.is_shutdown():

            if self.received and self.received1:
            
                to_speed = self.pid.control(self.desired_speed - self.curr_speed)

                to_speed = np.clip(to_speed, -1.0,1.0)

                thr_msg.header.stamp = rospy.Time.now()
                brk_msg.header.stamp = rospy.Time.now()

                if to_speed < 0:

                    thr_msg.throttle_position = 0.0
                    if -1.0 <= to_speed <=0.0:
                        brk_msg.brake_position = np.clip(-to_speed,0,1)
                    else:
                        brk_msg.brake_position = 0.2
                
                elif 0.0 <= to_speed <= 1.0:
                    thr_msg.throttle_position = np.clip(to_speed,0,0.5)
                    brk_msg.brake_position = 0.0
                
                else:
                    brk_msg.brake_position = 0.0 
                    thr_msg.throttle_position = 0.3

                self.pub.publish(thr_msg)
                self.pub1.publish(brk_msg)

                print(f'To speed: {to_speed}')

            self.rate.sleep()
try:
    NODE()
except rospy.ROSInterruptException:
    pass
