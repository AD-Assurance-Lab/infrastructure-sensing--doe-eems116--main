# Chip-Enabled Raised Pavement Markers (CERPMs)

A CERPM is an ordinary raised pavement marker (the reflective bump between lanes) with a small
radio inside. Each marker broadcasts its own GPS position, an ID and the speed limit over
LoRa, and a receiver in the car turns the markers it hears into a lane estimate. The idea:
the road tells the car where the lane is, so the car needs less camera processing to find it,
and the method keeps working when snow hides the paint.

The prototypes are off-the-shelf raised pavement markers (Stimsonite C88) milled out to hold a Heltec WiFi LoRa 32
board, programmed in the Arduino IDE. A matching board in the vehicle passes what it hears to
ROS 1 over USB serial.

## What is here

- `ros1/cerpm_data/`: the receiver package. `scripts/LoRaSender_v1.ino` and
  `LoRaReceiver_v1.ino` are the marker and vehicle firmware; `receiver.py` reads the serial
  port and publishes `cerpm_receiver` messages; launch files for collection and testing; a
  short sample bag. Setup notes: `ros1/SETUP.md`. History: Nic Brown (early 2023), Parth
  Kadav (July 2023 and after).
- `ros1/cerpmv3/`: the later package that builds the lane map from received markers and
  shows the markers against the ego vehicle (`get_cerpms.py`, `show_cerpm_map.py`,
  `show_cerpm_egoveh.py`, `rec_and_send.py`).
- `cad/`: the marker housing model used for the prototypes (STL, SketchUp) and renders.
- Recorded drives (two ROS 1 bags, 2.6 GB, with camera) are on Hugging Face; see the
  repository README.

## Papers

- Kadav et al., "Development and Evaluation of Chip-Enabled Raised Pavement Markers for Lane
  Line Detection," 2022 IEEE Sensors. <https://doi.org/10.1109/SENSORS52175.2022.9967036>
- Kadav et al., "Automated Lane Centering: An Off-the-Shelf Computer Vision Product vs.
  Infrastructure-Based Chip-Enabled Raised Pavement Markers," Sensors 24(7), 2327 (2024).
  <https://doi.org/10.3390/s24072327>
