# Van Atta radar retroreflectors

A Van Atta array is a flat antenna board that sends a radar signal straight back toward
where it came from, so it appears as a strong, steady target to a car's radar from a wide
range of angles. Placed along a lane, the tiles let the radar, which already works in rain,
snow and darkness, find the lane edge without a camera.

- `kicad/111_degree_beamwidth/`, `kicad/119_degree_beamwidth/`: two array designs (KiCad
  project, PCB, and `production/` Gerbers and drill files ready to order). The
  `array_1p8_*` and `array_1p7_*` Gerbers at each level are the array layers by themselves.
- `kicad/VanAtta_111_deg/`: the first version of the 111° design.

Recordings on Hugging Face (`radar-retroreflectors/`). 2024-01-31: four runs past the tiles with
the car's Aptiv ESR radar tracks and raw radar-bus frames, an Ouster OS1-64 lidar, a camera and
vehicle data (17 GB). 2024-04-25: twelve short runs plus a 25-minute drive of the DOE
demonstration route, and 2024-06-08: fourteen short runs, both with only a second radar's target
lists (most likely a smartmicro UMRR-96, inferred from the project's sensor list). The radar's
own documentation is in the WMU EcoCAR sensors repository.

Paper: Brown et al., SAE 2024-01-2042, <https://doi.org/10.4271/2024-01-2042>.
