#!/usr/bin/env python3

import rospy 	#imporitng ROS commands
import serial.tools.list_ports	#import serial library to read in the serial ports
import re 
from std_msgs.msg import Header		# importing ROS standard message
from cerpm_data.msg import cerpm_receiver	# importing the custom message

########################################################

# ROS initialize node, set rate, and establish publishing message for CERPM

rospy.init_node('cerpm_lane_info') 

rate = rospy.Rate(100)

cerpm_pub = rospy.Publisher('/cerpm_lane_info', cerpm_receiver, queue_size=10)

#get the list of all the ports in the device
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

#print to list of ports to check the port in which the Arduino (Heltec 32) is plugged in
portList = []

for onePort in ports:
	portList.append(str(onePort))
	# print(str(onePort))

#identify the port for arduino and input here. It should be sth like /dev/ttyUSB0 (For this case, your input would be 0.)
# val = input("select Port: USB")

serialInst.baudrate = 115200
serialInst.port = '/dev/ttyUSB0'

serialInst.open()

print("\nThe cerpm is now working")

#decode data coming in from the serial port
try:
	while not rospy.is_shutdown():
		
		if serialInst.in_waiting:
			packet = serialInst.readline()
			infoString = (packet.decode('utf'))
			list_of_info = infoString.split(',')

			# custom ROS message
			cerpm = cerpm_receiver()
			cerpm.header = Header(stamp=rospy.Time.now(), frame_id="cerpm")
			cerpm.id = list_of_info[0]
			cerpm.latitude = float( list_of_info[1] )
			cerpm.longitude = float( list_of_info[2] )
			cerpm.altitude = float( list_of_info[3] )
			cerpm.receiver_signal_strength = float(list_of_info[4].split('-')[1])
			str = list_of_info[5]
			x = re.findall('[0-9]+',str)
			cerpm.SNR = float(x[0]+'.' +x[1])
			cerpm_pub.publish(cerpm)

	rate.sleep()

except rospy.ROSInterruptException:
	print("Interrupted!")

