#!/usr/bin/env python3

import csv
import can
import cantools
import rospy
import time
import os 

from kia_niro_speed.msg import kia_speed


# from vic_niro_data import vic_info

################################################################
########  This script is meant for live data collection  ########
################################################################


rospy.init_node('Niro_whee_speed_info')

pub = rospy.Publisher('kia_speed', kia_speed, queue_size=10)

# rate = rospy.Rate()

can_bus = can.interface.Bus('can1', bustype='socketcan')  

db = cantools.db.load_file('/home/parth/catkin_ws/src/kia_niro_speed/src/scripts/chassis_kia_niro.dbc')

while not rospy.is_shutdown():

    try: 
        t = time.time()        
        
        message = can_bus.recv()

        if int(message.arbitration_id) == 902:

            wheel = db.decode_message(message.arbitration_id, message.data)

            lr = wheel['LEFT_REAR'] * 0.277774 * 2.237 # conversion from kph to mph
            rr = wheel['RIGHT_REAR'] * 0.277774 * 2.237
            lf = wheel['LEFT_FRONT'] * 0.277774 * 2.237
            rf = wheel['RIGHT_FRONT'] * 0.277774 * 2.237
            speed = (lr + rr + lf + rf)/4

            print(speed)

        time.sleep(1e-4)

    except rospy.ROSInterruptException:
        print("exited")
