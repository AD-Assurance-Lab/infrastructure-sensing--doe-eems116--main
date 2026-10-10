# Vehicle control and CAN packages (ROS 1)

Code that drove the project's test vehicles (a Kia Niro and a Kia Soul, both with the
PolySync drive-by-wire kit) during the CERPM and lane-centering experiments. ROS 1 Melodic.
The vehicles and kits have since gone to UC Berkeley; the code is kept as the record of how
the lane-centering comparison in Kadav et al. (2024) was run.

- `steering_angle_control/`: lateral and longitudinal control. Stanley waypoint following
  on RTK GNSS (`stanley_waypoint_follow*.py`), lane keeping from the Mobileye
  (`mobileye_lka.py`, `angle_ctrl_mobileye.py`), PID steering, heading and speed loops, the
  CERPM waypoint files used on the test route, and the Kia Niro chassis DBC. Depends on
  PolySync `roscco` and `ethz_piksi_ros`.
- `kia_niro_speed/`: reads wheel speed from the Kia Niro CAN bus with the chassis DBC and
  publishes it.
