#!/usr/bin/env python3

import rospy 
import serial.tools.list_ports		
from cerpmv3.msg import id	
    
class RecSend:
    
    def __init__(self):
        
        rospy.init_node('PublishTxInfo')
        
        self.ports = serial.tools.list_ports.comports()
        self.serialInst = serial.Serial()
        
        self.id_pub = rospy.Publisher('/received_cerpmids', id, queue_size=10)
        
        self.portList = []
        self.saved_ids = []
        
        for onePort in self.ports:
            self.portList.append(str(onePort))
        
        if self.portList:
            print("Available ports : ", self.portList)
            print('Connecting to port : ' f'{self.portList[0]}')
        else:
            rospy.loginfo('No ports detected')    
            
        self.serialInst.baudrate = 115200
        self.serialInst.port = '/dev/ttyUSB0'
        
        self.serialInst.open()
        
        self.rate = rospy.Rate(20)
        
        self.publish()

    def publish(self):
        
        i = 0
        
        msg = id()
        
        while not rospy.is_shutdown():
            
            packet = self.serialInst.readline()
            
            # remove the last line from the packet which is just '----------'
            if len(packet) >= 90:
                continue
            
            # reads in the cerpmid's
            else:
                rospy.loginfo(f'Rx is now receiving : {i} CERMPs')
                infoString = packet.decode('utf')
                list_of_info = infoString.split(',')
                # print(list_of_info)
                if int(list_of_info[0]) not in self.saved_ids:
                    self.saved_ids.append(int(list_of_info[0]))
                    i += 1 

            msg.header.stamp = rospy.Time.now()
            msg.id = int(list_of_info[0])
            self.id_pub.publish(msg)
            self.rate.sleep()
            
        
ls = RecSend()
