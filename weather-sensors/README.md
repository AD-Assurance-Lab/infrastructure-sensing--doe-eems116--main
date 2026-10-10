# Weather and sensor performance (with NCAR)

Recordings made with NCAR to see how each sensor holds up in bad weather, so the vehicle can
switch off sensors that stop helping and save their energy.

Data on Hugging Face (`weather-ncar/`): ROS 1 bags with the Ouster OS-1 lidar (point clouds and
IMU), Piksi RTK GNSS, the Delphi ESR radar and the Mobileye camera: two clear-weather runs
(51 s and 84 s) and one in rain (121 s), plus a short ESR lane recording.

- `ouster-setup-notes.md`: links used to set up the Ouster driver.

Paper: Masterson et al., SAE 2024-01-2044, <https://doi.org/10.4271/2024-01-2044>.
