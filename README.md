# SafePath

Rover first, then human.

NASA Space Apps Challenge 2026: a layered Mars map and route planner for astronaut
surface exploration in Jezero crater.

Before an astronaut walks to a science target, a small scout rover drives the
route first. The planner computes three routes on real NASA terrain data, checks
the rover's battery and the astronaut's oxygen for the round trip, and repairs
the route with D* Lite when the rover meets an obstacle the orbital map did not show.

## Team

| Member | Role |
|---|---|
| Ali Andaç Erdaş | Route engine, simulation, integration |
| Aras | Map layers and 3D terrain |
| Hilal | Web interface |
| Taha | Research and presentation |
| Batuhan | Research and presentation |

> The live demo link will be added before submission.

## What works today

| Part | Status |
|---|---|
| Terrain grid of the mission area (10 x 10 km, 5 m cells) | Working |
| Three routes: fastest, safest, most efficient | Working |
| Battery and oxygen check for the round trip | Working, with placeholder rover numbers |
| Return trip with a hidden obstacle and D* Lite replanning | Working |
| Six real Perseverance science stops as selectable targets | Working |
| Web interface: 3D Mars globe, 3D terrain, route ledger, astronaut status, tablet view, rover showcase | Working |

## Mission area

A 10 x 10 km square around the western delta of Jezero crater
(18.3856 to 18.5543 N, 77.3212 to 77.4990 E). The base is the Perseverance
landing site, Octavia E. Butler Landing.

## Data layers

| Layer | Source | Resolution | Use |
|---|---|---|---|
| Elevation | USGS Astrogeology, Mars 2020 Terrain Relative Navigation HiRISE DTM Mosaic | 1 m, resampled to 5 m | 3D terrain, slope, routing |
| Optical image | USGS Astrogeology, Mars 2020 Science Investigation CTX Orthomosaic | 5 m | Basemap draped on the terrain |
| Thermal inertia | Edwards and Buz (2021), THEMIS-derived Thermal Inertia of Jezero Crater | 100 m | Ground type: loose sand or firm rock |
| Rover positions | NASA Mars 2020 mission, localized rover stops | per stop | Science stops, validation |

## How the routes are computed

Every 5 m cell has a slope (from elevation) and a ground type (from thermal
inertia). Moves between neighbouring cells get a cost, and D* Lite finds the
cheapest path for each of three profiles:

- **Fastest**: least driving time. The rover slows down on slopes.
- **Safest**: never enters cells steeper than the safe limit (15 degrees).
- **Most efficient**: least battery use. Loose ground costs more energy than firm ground.

Cells steeper than 30 degrees are impassable for every profile.

Example, landing site to a target on the delta top behind the scarp
(`data/processed/routes.json`):

| Route | Distance | Steepest slope | Distance above the safe limit |
|---|---|---|---|
| Fastest | 3621 m | 23.8 deg | 116 m |
| Safest | 4108 m | 11.2 deg | 0 m |
| Most efficient | 3841 m | 19.4 deg | 82 m |

For the six Perseverance stops the three routes are nearly identical, because
Perseverance itself chose places that can be reached over gentle ground.

## Hidden obstacle on the way back

`route/simulate_return.py` drives the rover back to base on the safest route. A
rock field that is not in the orbital data lies on the route. The rover only sees
the part of it within sensor range, and D* Lite repairs the plan each time new
blocked cells appear (`data/processed/return_scenario.json`):

- planned return 4108 m, driven 4241 m, 36 replans
- all 36 repairs together took about 0.13 s; planning again from scratch at the
  first detection took about 0.72 s on the same laptop

The obstacle is placed by us. Its position, size and the sensor range are
scenario choices, not measurements.

## Validation

`pipeline/validate_waypoints.py` compares our grid with the 388 localized stops
of Perseverance inside the mission area (`data/processed/validation.json`):

| Check | Result |
|---|---|
| NASA rover elevation minus our grid | mean -0.01 m, standard deviation 0.18 m, largest 0.86 m |
| Rover tilt recorded by NASA | median 3.6 deg, maximum 20.3 deg |
| Our slope at the same cells | median 3.1 deg, maximum 20.7 deg |

## What is real and what is simulated

| Item | Status |
|---|---|
| Terrain, slope, image, thermal inertia | Real NASA and USGS data |
| Route computation and D* Lite | Real algorithm running on the real data |
| Science stop coordinates and arrival photos | Real Perseverance positions and Navcam frames |
| Air temperature and pressure | Real Jezero measurements (MEDA), four sols |
| Radiation | 328 real Curiosity RAD measurements, 2012 to 2026, but from Gale crater, not Jezero |
| Rover model | The team's own CAD design, drawn larger than life on the map |
| Rover motion and sensing | Simulated |
| Hidden obstacle | Placed by us |
| Rover mass, speed, battery, power use | Placeholders until the rover design is final |
| Thermal inertia to rolling resistance mapping | Placeholder |
| Crew walking speed, EVA duration, reserve | Sourced, but measured for lunar suits |

Times and energy values depend on the placeholder rover numbers and should not be
quoted as results. Distances and slopes come directly from the data.

## Run it

```
python -m venv .venv && .venv/bin/pip install numpy scipy pillow matplotlib pytest
.venv/bin/python pipeline/build_grid.py        # downloads the mission window, about 85 MB
.venv/bin/python -m route.plan_routes
.venv/bin/python -m route.simulate_return
.venv/bin/python pipeline/validate_waypoints.py
.venv/bin/python -m pytest
```

The processed grids and results are already in `data/processed/`, so the route
scripts run without the download.

```
pipeline/   build_grid.py, export_terrain.py, export_web.py, export_rover.py,
            fetch_rad.py, validate_waypoints.py
route/      dstar_lite.py, plan_routes.py, simulate_return.py
tests/      D* Lite checked against Dijkstra, including replanning
data/       processed/ (grids, routes, scenario, validation), layers/ (image, thermal inertia)
web/        index.html, styles.css, app.js, data/, assets/, vendor/ (three.js)
```

## Web interface

A static site in `web/`, no build step. Serve the folder and open it:

```
python -m http.server 8765 --directory web
```

- **Path selector**: a rotating Mars globe, coordinate entry, a flight to Jezero,
  then the 3D terrain with data layers, the three routes and their slope
  profiles. "Send rover" drives the scout out and back, including the hidden
  obstacle and the D* Lite repair on the safest route to the delta top.
- **Astronaut status**: suit telemetry (simulated values, synthesized breathing
  sound) and what the selected route leaves in oxygen and battery.
- **Tablet view**: minimum, average and maximum values along the route, the air
  temperature and pressure Perseverance measured in Jezero, and a real Navcam
  photo Perseverance took at the arrival point. The team's delta-top target has
  no rover photo, so its view is rendered from the terrain data and labelled so.

- **Scout rover**: the team's CAD model on a turntable with its measured dimensions.

Routes are precomputed by the Python engine for seven surveyed targets; a typed
coordinate snaps to the nearest one. `pipeline/export_web.py` builds `web/data`.
The interface is available in English and Turkish.

## Use of AI

AI coding assistants (including Anthropic's Claude) were used to write and review
the code in this repository, to process the data and to search for sources. Team
members decided the concept, checked the outputs and are responsible for the
content. No AI-generated images or video are used. The repository contains no
NASA logos or brand elements.

## References

- USGS Astrogeology Science Center (2020). Mars 2020 Terrain Relative Navigation
  HiRISE DTM Mosaic. https://doi.org/10.5066/P9REJ9JN
- USGS Astrogeology Science Center. Mars 2020 Science Investigation CTX DEM Mosaic
  and Orthomosaic. Public domain.
  https://astrogeology.usgs.gov/search/map/mars_2020_science_investigation_ctx_dem_mosaic
- Edwards, C. S., and Buz, J. (2021). THEMIS-derived Thermal Inertia of Jezero
  Crater, Mars. Zenodo. CC BY 4.0. https://doi.org/10.5281/zenodo.4931348
- NASA/JPL-Caltech. Mars 2020 Perseverance rover waypoints.
  https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json
- Koenig, S., and Likhachev, M. (2002). D* Lite. Proceedings of the AAAI
  Conference on Artificial Intelligence.
- NASA. Perseverance rover components.
  https://science.nasa.gov/mission/mars-2020-perseverance/rover-components/
- NASA. Apollo consumables document (planned walking speed, walk-back reserve).
  https://www.nasa.gov/wp-content/uploads/static/history/alsj/19790073512_1979073512.pdf
- NASA. xEMU testing (8 hour EVA design requirement).
  https://ntrs.nasa.gov/citations/20240004887
- NASA Mars Trek. Viking MDIM 2.1 colour mosaic (globe texture). https://trek.nasa.gov/mars/
- NASA/JPL-Caltech. Mars 2020 raw images, Navcam frames from sols 180, 502, 565,
  652, 736 and 770. https://mars.nasa.gov/mars2020/multimedia/raw-images/
- NASA/JPL-Caltech/CAB. Mars 2020 MEDA weather feed, sols 1130 to 1133.
  https://mars.nasa.gov/rss/api/?feed=weather&category=mars2020&feedtype=json
- NASA. Apollo 11 photograph AS11-40-5903. https://images.nasa.gov/details/as11-40-5903
- MSL RAD reduced data records, PDS Planetary Plasma Interactions node, data set
  MSL-M-RAD-3-RDR-V1.0. https://pds-ppi.igpp.ucla.edu/data/MSL-M-RAD-3-RDR-V1.0/
- MSL RAD surface radiation: Hassler, D. M., et al. (2014). Science 343.
  https://doi.org/10.1126/science.1244797
- Software: NumPy, SciPy, Pillow, Matplotlib, pytest, trimesh, cascadio, three.js (MIT).
- Fonts: Newsreader, IBM Plex Sans, IBM Plex Mono (SIL Open Font License).

## License

Apache License 2.0. See `LICENSE`. Third-party data keeps its own terms, listed above.
