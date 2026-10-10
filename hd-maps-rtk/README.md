# HD maps with RTK GNSS

When snow covers the paint, a camera cannot see the lane, but a car that knows exactly
where it is (RTK GNSS, a few centimeters) and has a map of where the lane lines are can
draw them into the camera image anyway.

- `hd-maps_v2.py`: ROS 1 node that takes the Piksi RTK position and heading, converts mapped
  lane-line points to the camera frame, and draws them on the image.
- `hd-map-guidelines.md`: what the map holds (lane lines, signs, rules per lane segment), the
  route (front loop of WMU's Parkview campus) and the 2023 task split.
- `rtk-validation.md`: background on GNSS and RTK accuracy and how it was checked.

Data on Hugging Face (`hd-maps/`): 1,631 front-camera frames (1280x720) from the Parkview loop
and a video of the projected map.

Papers: SAE 2023-01-0051 (<https://doi.org/10.4271/2023-01-0051>) and SAE 2024-01-2044
(<https://doi.org/10.4271/2024-01-2044>).
