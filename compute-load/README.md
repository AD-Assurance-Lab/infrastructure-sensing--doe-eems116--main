# Measuring sensing and compute energy

The project's payoff is measured in energy: how much less power the vehicle draws when
infrastructure supplies the perception. The tests ran on the lab's Dynojet chassis
dynamometer with a power analyzer on the computing and sensor supply.

- `dyno-test-plan.md`: the test plan (location, dates, test summary, vehicle and technology
  background, data collection process).
- `prelim-compute-load-setup.png`, `six-camera-layout.svg`: the measurement setup and the
  six-camera baseline layout.

Data on Hugging Face (`compute-load/`): `dyno-2024-01/` (Fluke 430-II power analyzer logs as
CSV and TXT, the raw `.fpqo` files, and state-of-charge over the UDDS cycle for the baseline
and offloaded cases), `dyno-2023/` (20 mph, 40 mph and UDDS collection), `prelim/` (compute
load with and without a CNN running).

Paper: Brown et al., IEEE ITSC 2023, <https://doi.org/10.1109/ITSC57777.2023.10422013>.
