export const config = {
  runtime: 'edge',
};

export default async function handler(req) {
  try {
    const upstream = await fetch('https://dublincityairandnoise.ie/assets/php/get-monitors.php', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; DublinAirQualityMonitor/1.0)',
        'Accept': 'application/json, text/plain, */*'
      },
      next: { revalidate: 60 } // Cache at Edge for 60 seconds
    });

    if (!upstream.ok) {
      return new Response(JSON.stringify({ error: 'Upstream feed unavailable' }), {
        status: 502,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const data = await upstream.json();

    return new Response(JSON.stringify({
      status: 'success',
      source: 'Dublin City Council / Sonitus Systems',
      data_gov_ie_url: 'https://data.gov.ie/dataset/sonitus',
      smart_dublin_url: 'https://data.smartdublin.ie/dataset/sonitus',
      portal_url: 'https://dublincityairandnoise.ie/',
      total_monitors: Array.isArray(data) ? data.length : 0,
      data: data
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 's-maxage=60, stale-while-revalidate=120',
        'Access-Control-Allow-Origin': '*'
      }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
