# CERPM_ROS_Package
This repository is for a CERPM ROS Package for the 2021 DOE


## 1. Dependencies
The dependincies for this package include
	ROS, pyserial
	
## 2. Workspace installtion
Make sure to source workspace in .bashrc in the home directory (source ~/ws/devel/setup.bash)
	From the home directory
		
		mkdir catkin_ws
		
		cd catkin_ws/ 
		
		mkdir src
		
		cd src/ copy "ROS package > cerpm_data" into > catkin_ws/src/ 
		
		cd catkin_ws/ catkin_make # catkin make workspace for communications
		

## 3. Get the correct port
The initial "path" for the usb connection for the cerpm is set to "dev/ttyUSB0" this maye be differnt for you machine. 

Use the python file get_port.py to see where your source path is for the port. This can also be done using the receiever .py file by uncommenting line 26. Yet running this code could have an error if the path to the port is incorrect. 
	
If the path is different change it in the receiver.py file in line 32.
	
If the path is correct and get an error that mentions the port may be busy or you do not have permission. Please run one or both commands if the first do not work. 
	
		sudo adduser <usename> dialout
		
If this does not work use the following.

		sudo su
		cd /
		cd dev/
		sudo chown <username> <port path>	i.e. port path = ttyUSB0 

## 4. Launching cerpm ROS package
To launch the cerpm make sure the workspace is souced and you should be able to launch in any directory. 
	
In the terminal 

		roslaunch cerpm_data cerpm.launch	# in any directory
		
		roslaunch cerpm.launch			# in the launch file directory for cerpm_data
