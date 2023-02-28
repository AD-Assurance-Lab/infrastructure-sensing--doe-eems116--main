#!/usr/bin/env python3

import rospy 	#imporitng ROS commands
import time
import csv

from cerpm_data.msg import cerpm_receiver	# importing the custom message

########################################################

rospy.init_node('get_cerpm_lane_info') 

rate = rospy.Rate(100)

cerpm_info = []

def callback(msg):

    t = time.time()

    id = msg.id
    lat = msg.latitude
    long = msg.longitude
    rssi = msg.receiver_signal_strength 
    snr = msg.SNR

    cerpm_info.append([ t, id, lat, long, rssi, snr ])

    print("\nTime:", t, "\nCERPM_id:", id, "\nLatitude:", lat, "\nLongitude:", long, "\nRSSI:", rssi, "\nSNR:", snr)

    rate.sleep()

def main():
    
    cerpm_info = rospy.Subscriber('/cerpm_lane_info', cerpm_receiver, callback)

    rospy.spin()

try:
    main()
    
except rospy.ROSInterruptException:
    print("exited")

# file = open('cerpm_lane_info.csv', 'a+')  # Uncomment if you want to append to the existing csv file
file = open('cerpm_lane_info.csv', 'w') # Uncomment if you want to overwrite the existing file created

with file:
        write = csv.writer(file)
        write.writerow(["time", "cerpm_id", "lat", "long", "RSSI", "SNR"]) 
        write.writerows(cerpm_info) 
        