# Dublin Air Quality Live Monitor

A live web application displaying telemetry linked to the official Irish Open Data dataset:
- **National Open Data Portal:** [https://data.gov.ie/dataset/sonitus](https://data.gov.ie/dataset/sonitus) (Dataset Title: *Air Quality Monitoring API DCC*)
- **Publisher:** Dublin City Council / Smart Dublin ([https://data.smartdublin.ie/dataset/sonitus](https://data.smartdublin.ie/dataset/sonitus))
- **Live Stream Host:** [https://dublincityairandnoise.ie/](https://dublincityairandnoise.ie/)

## Features
- **Live Station Map:** Interactive Leaflet map displaying active monitoring stations across Dublin.
- **Pollutant Readouts:** Real-time metrics for PM2.5, PM10, NO₂, SO₂, and O₃.
- **Search & Filter:** Search specific monitoring locations across Dublin.
- **Auto-Refresh:** Telemetry polls and updates periodically in the background.

## Deployment
This project is a static web application that can be hosted on any static web server:
1. Push this folder to your repository or upload the static assets directly.
2. Serve `index.html` as the frontend entry point.
