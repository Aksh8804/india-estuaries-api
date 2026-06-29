async function getAllEstuaryData(){
  const token = localStorage.getItem("access_token");
  const estuaries = ["Palar","Kollidam","Pulicat"];
  let allPoints = [];

  for(const est of estuaries){

    const [abRes, shRes, colRes, szRes] = await Promise.all([
      fetch(`${API_BASE}/estuaries/${est}/abundance`, {
        headers:{ "Authorization":`Bearer ${token}` }
      }),
      fetch(`${API_BASE}/estuaries/${est}/shape`, {
        headers:{ "Authorization":`Bearer ${token}` }
      }),
      fetch(`${API_BASE}/estuaries/${est}/color`, {
        headers:{ "Authorization":`Bearer ${token}` }
      }),
      fetch(`${API_BASE}/estuaries/${est}/size`, {
        headers:{ "Authorization":`Bearer ${token}` }
      })
    ]);

    const abundance = abRes.ok ? await abRes.json() : { points: [] };
    const shape     = shRes.ok ? await shRes.json() : { points: [] };
    const color     = colRes.ok ? await colRes.json() : { points: [] };
    const size      = szRes.ok ? await szRes.json() : { points: [] };

    abundance.points.forEach(pt=>{

      const shapePt =
        shape.points?.find(s=>s.station_code===pt.station_code) || {};

      const colorPt =
        color.points?.find(s=>s.station_code===pt.station_code) || {};

      const sizePt =
        size.points?.find(s=>s.station_code===pt.station_code) || {};

      allPoints.push({
        ...pt,
        estuary: est,
        shape: shapePt,
        color: colorPt,
        size: sizePt
      });

    });
  }

  return allPoints;
}
