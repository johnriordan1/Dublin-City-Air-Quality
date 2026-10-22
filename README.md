# Dublin Air & Noise Quality Live Monitor

A live web application displaying telemetry linked to the official Irish Open Data dataset:
- **National Open Data Portal:** [https://data.gov.ie/dataset/sonitus](https://data.gov.ie/dataset/sonitus) (Dataset Title: *Noise and Air Quality Monitoring API DCC*)
- **Publisher:** Dublin City Council / Smart Dublin ([https://data.smartdublin.ie/dataset/sonitus](https://data.smartdublin.ie/dataset/sonitus))
- **Live Stream Host:** [https://dublincityairandnoise.ie/](https://dublincityairandnoise.ie/)

## Features
- **Live Station Map:** Interactive Leaflet map displaying active monitoring stations across Dublin.
- **Pollutant Readouts:** Real-time metrics for PM2.5, PM10, NO₂, SO₂, O₃, and acoustic noise (LAeq sound level).
- **Search & Filter:** Filter stations by Air Quality, Noise, or search specific locations.
- **Auto-Refresh:** Telemetry polls and updates periodically in the background.

## Deployment to Vercel
This project is configured out-of-the-box for Vercel:
1. Push this folder to a GitHub repository (or deploy via Vercel CLI with `vercel`).
2. Vercel automatically deploys:
   - `index.html` as the static frontend.
   - `api/monitors.js` as a serverless Edge function with 60-second caching, bypassing browser CORS issues.
