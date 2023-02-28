#!/usr/bin/env python3

#import serial library to read in the serial ports
import serial.tools.list_ports

#get the list of all the ports in the device
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

#print to list of ports to check the port in which the Arduino (Heltec 32) is plugged in
portList = []

for onePort in ports:
    portList.append(str(onePort))
    print(str(onePort))
