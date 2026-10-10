#!/usr/bin/env python3

import rospy 
import serial.tools.list_ports	
from std_msgs.msg import Header		
from cerpm_data.msg import cerpm_receiver	

#get the list of all the ports in the device
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

#print to list of ports to check the port in which the Arduino (Heltec 32) is plugged in
portList = []

for onePort in ports:
	portList.append(str(onePort))
	# print(str(onePort))

serialInst.baudrate = 115200
serialInst.port = '/dev/ttyUSB0'

serialInst.open()

print("The cerpm is now working")


i = 0
while i < 2:
    packet = serialInst.readline()
    
    infoString = packet.decode('utf')
    
    list_of_info = infoString.split(',')
    print(list_of_info[0])
    
    z = int(list_of_info[0])
    
    i += 1 