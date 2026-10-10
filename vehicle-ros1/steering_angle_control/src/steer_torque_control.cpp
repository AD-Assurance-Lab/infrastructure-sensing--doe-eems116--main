#include <ros/ros.h>
#include <std_msgs/Float32.h>
#include <roscco/SteeringCommand.h>

float currAngle = 0.0;
float setpoint = 0.0;
bool received = false;
int cr = 20;

ros::Publisher pub;

void setpoint_callback(const std_msgs::Float32::ConstPtr& msg)
{
    setpoint = msg->data;
    received = true;
}

void kia_callback(const std_msgs::Float32::ConstPtr& msg)
{
    currAngle = msg->data;
}

void run()
{

    ROS_INFO("Starting steer torque controller");
    ros::Rate rate(cr);

    while (ros::ok())
    {
        if ( received )
        {
            roscco::SteeringCommand steer_msg;

            steer_msg.steering_torque = 0.3;

            pub.publish( steer_msg );

        }

        ros::spinOnce();
        rate.sleep();
    }
}

int main(int argc, char **argv)
{

    ros::init(argc, argv, "steer_torque_control_node");
    ros::NodeHandle nh;

    ros::param::get("~controller_rate", cr);
    
    ros::Subscriber kia_sub = nh.subscribe("/kia/steer_angle", 1000, kia_callback);
    ros::Subscriber set_sub = nh.subscribe("/steering_angle/desired", 1000, setpoint_callback);

    pub = nh.advertise<std_msgs::Float32>("/steering_command", 1000);

    run();

    return 0;
}