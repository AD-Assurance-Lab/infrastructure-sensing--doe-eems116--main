# Infrastructure-enabled energy efficient autonomous vehicles (DOE EEMS116)

Code, CAD, documents and data from a U.S. Department of Energy Vehicle Technologies Office
project at Western Michigan University, October 2021 to December 2024 (award DE-EE0009657,
project ID EEMS116, $2.5M). Partners: Oak Ridge National Laboratory, the National Center for
Atmospheric Research (NCAR) and DriveU.auto. PI: Zachary D. Asher.

**The idea.** A self-driving car spends a lot of energy on its own sensing and computing:
cameras, lidar and the processors that interpret them. If the road itself supplies
high-quality information (where the lanes are, what the weather is doing, a precise map),
the car can carry fewer sensors and run less computation. The project built and tested four
ways for the infrastructure to do that, put them on a test vehicle, and measured the energy
saved on a chassis dynamometer and on the road.

The project is finished and not being continued; everything a future researcher might want
is released here. Most code is ROS 1 (Melodic) and is kept as it ran.

| Folder | What it is |
|---|---|
| `cerpm/` | **Chip-Enabled Raised Pavement Markers**: lane markers that radio their position to the car. Firmware, ROS 1 receiver and lane-map packages, marker CAD |
| `radar-retroreflectors/` | **Van Atta radar retroreflectors**: passive printed-circuit tiles that show up brightly to a car's radar, marking the lane for radar instead of cameras. KiCad designs and Gerbers for 111° and 119° beamwidth versions |
| `hd-maps-rtk/` | **HD maps with RTK GNSS**: projecting surveyed lane lines into the camera image from centimeter-level position, for roads where snow hides the paint |
| `weather-sensors/` | **Weather data with NCAR**: lidar, radar and camera recordings in clear and rain conditions, to decide when to trust which sensor |
| `compute-load/` | **Measuring the energy**: chassis dynamometer test plan and setup for the compute load reduction tests |
| `vehicle-ros1/` | Vehicle control and CAN code for the Kia test vehicles (Stanley waypoint following, Mobileye lane keeping) |
| `docs/` | The 2025 DOE Annual Merit Review presentation, a one-page project summary, publicity graphics |

The fourth technology, offloading camera processing to a cloud computer over the cellular
network with DriveU.auto, is described in the AMR presentation; its software and system images
are DriveU's and are not released.

## Data

All recordings (ROS 1 bags, camera frames, power analyzer logs; 37 GB) are on Hugging Face:
<https://huggingface.co/datasets/AD-Assurance-Lab/infrastructure-sensing-doe-eems116>

    hf download AD-Assurance-Lab/infrastructure-sensing-doe-eems116 --repo-type dataset --local-dir ./data

## Publications

1. Sharma, Ekti, Fanas Rojas, Brown, Pesin, Wang, Huff, LaClair, Asher, Meyer. "Development and Evaluation of
   Chip-Enabled Raised Pavement Markers for Lane Line Detection." 2022 IEEE Sensors.
   <https://doi.org/10.1109/SENSORS52175.2022.9967036>
2. Sharma, Fanas Rojas, Ekti, Wang, Asher, Meyer. "Vehicle Lateral Offset Estimation Using
   Infrastructure Information for Reduced Compute Load." SAE Technical Paper 2023-01-0800.
   <https://doi.org/10.4271/2023-01-0800>
3. Carow, Kadav, Patil, Fanas Rojas, Asher. "Projecting Lane Lines from Proxy High-Definition Maps for Automated Vehicle Perception in
   Road-Occluded Scenarios." SAE Technical Paper 2023-01-0051.
   <https://doi.org/10.4271/2023-01-0051>
4. Brown, Motallebiaraghi, Fanas Rojas, Ayantayo, Meyer, Asher, Ekti, Wang, Goberville,
   Feinberg. "Evaluation of Autonomous Vehicle Sensing and Compute Load on a Chassis
   Dynamometer." 2023 IEEE ITSC. <https://doi.org/10.1109/ITSC57777.2023.10422013>
5. Kadav, Sharma, Fanas Rojas, Patil, Wang, Ekti, Meyer, Asher. "Automated Lane Centering: An
   Off-the-Shelf Computer Vision Product vs. Infrastructure-Based Chip-Enabled Raised
   Pavement Markers." Sensors 24(7), 2327 (2024). <https://doi.org/10.3390/s24072327>
6. Brown, Patil, Sharma, Kadav, Fanas Rojas, Hong, Liao, Ekti, Wang, Meyer, Asher. "Real World
   Use Case Evaluation of Radar Retro-reflectors for Autonomous Vehicle Lane Detection
   Applications." SAE Technical Paper 2024-01-2042. <https://doi.org/10.4271/2024-01-2042>
7. Masterson, Patil, Brown, Asher, Fanas Rojas, Siems-Anderson, Walker, Rabinowitz. "Engineering
   Requirements that Address Real World Hazards from Using High-Definition Maps, GNSS, and
   Weather Sensors in Autonomous Vehicles." SAE Technical Paper 2024-01-2044.
   <https://doi.org/10.4271/2024-01-2044>
8. Patil, Fanas Rojas, Kadav, Sharma, Masterson, Wang, Ekti, Liao, Brown, Asher. "Assessing
   Resilience in Lane Detection Methods: Infrastructure-Based Sensors and Traditional
   Approaches for Autonomous Vehicles." SAE Technical Paper 2024-01-2039.
   <https://doi.org/10.4271/2024-01-2039>
9. Sharma et al. "AEPF: Attention-Enabled Point Fusion for 3D Object Detection." Sensors
   24(17), 5841 (2024). <https://doi.org/10.3390/s24175841>

## License and acknowledgment

Code: Apache-2.0 (`LICENSE`). Documents, CAD and data: CC BY 4.0. See `NOTICE`.

This material is based upon work supported by the U.S. Department of Energy's Office of
Energy Efficiency and Renewable Energy (EERE) under the Vehicle Technologies Office award
number DE-EE0009657.

This repository was `CERPM_ROS_Package` until 2026-10-09; it now also holds the rest of the
project, and `ORNL-CERPM` points here.
