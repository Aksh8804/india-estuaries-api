
/* ================= LOAD ESTUARY ================= */
document.getElementById("estuarySelect")
.addEventListener("change", loadEstuary);
async function loadEstuary(){
  currentEstuary = this.value;
document.getElementById("categorySelect").disabled = false;
document.getElementById("mediumSelect").disabled = true;
document.getElementById("layerSelect").disabled = true;
document.getElementById("mediumSelect").value = "";
document.getElementById("layerSelect").value = "";
if(barChart) barChart.destroy();
if(pieChart) pieChart.destroy();
document.getElementById("chartDownloadBtns").style.display = "none";
  if(!currentEstuary) return;
  markers.clearLayers();
  pieMarkers.clearLayers();
  currentPoints = [];
  try{
    const [abRes, shRes, colRes, szRes] = await Promise.all([
  fetch(`${API_BASE}/estuaries/${currentEstuary}/abundance`, {
    headers: { "Authorization": `Bearer ${token}` }
  }),
  fetch(`${API_BASE}/estuaries/${currentEstuary}/shape`, {
    headers: { "Authorization": `Bearer ${token}` }
  }),
  fetch(`${API_BASE}/estuaries/${currentEstuary}/color`, {
    headers: { "Authorization": `Bearer ${token}` }
  }),
  fetch(`${API_BASE}/estuaries/${currentEstuary}/size`, {
    headers: { "Authorization": `Bearer ${token}` }
  })
]);
    const abundance = abRes.ok ? await abRes.json() : { points: [] };
    const shape     = shRes.ok ? await shRes.json() : { points: [] };
    const color     = colRes.ok ? await colRes.json() : { points: [] };
    const size      = szRes.ok ? await szRes.json() : { points: [] };
    if(!abundance.points || abundance.points.length === 0) {
    alert("No data available for this estuary.");
    return;
    }
    COLOR_KEYS = color.points?.length
      ? Object.keys(color.points[0].water)
      : [];
    currentPoints = abundance.points.map(pt => {
      const shapePt = shape.points?.find(s => s.station_code === pt.station_code) || {};
      const colorPt = color.points?.find(s => s.station_code === pt.station_code) || {};
      const sizePt  = size.points?.find(s => s.station_code === pt.station_code) || {};
      return {
        ...pt,
        shape: shapePt,
        color: colorPt,
        size: sizePt
      };
    });







// CATEGORY → MEDIUM CONTROL
document.getElementById("categorySelect")
.addEventListener("change", function(){

  const category = this.value;

  const medium = document.getElementById("mediumSelect");
  const layer = document.getElementById("layerSelect");
  const type = document.getElementById("typeSelect");
  const mapChart = document.getElementById("mapChartType");

  // RESET EVERYTHING
  medium.value = "";
  layer.value = "";
  type.value = "";
  mapChart.value = "";

  medium.disabled = true;
  layer.disabled = true;
  type.disabled = true;
  mapChart.disabled = true;

  if(category === "microplastic"){
    medium.disabled = false;   // ✅ enable only for microplastic
  }

});



    /* ===== MARKERS ===== */
    currentPoints.forEach(pt => {
      const popup = `
        <div style="max-height:300px; overflow-y:auto; font-size:13px;">
          <b>${pt.station_code}</b><br><br>
          <b>Abundance</b><br>
          Water: ${pt.water_abundance}<br>
          Sediment: ${pt.sediment_abundance}<br><br>
          <b>Size (Water)</b><br>
          ${formatObj(pt.size?.water)}<br><br>
          <b>Size (Sediment)</b><br>
          ${formatObj(pt.size?.sediment)}<br><br>
          <b>Shape (Water)</b><br>
          ${formatObj(pt.shape?.water)}<br><br>
          <b>Shape (Sediment)</b><br>
          ${formatObj(pt.shape?.sediment)}<br><br>
          <b>Color (Water)</b><br>
          ${formatObj(pt.color?.water)}<br><br>
          <b>Color (Sediment)</b><br>
          ${formatObj(pt.color?.sediment)}
        </div>
      `;
      const marker = L.marker([pt.latitude, pt.longitude])
        .bindPopup(popup, { maxWidth: 350 });
      markers.addLayer(marker);  // 
    });

// ===== AUTO ZOOM TO ESTUARY =====
if(markers.getLayers().length > 0){
  const group = L.featureGroup(markers.getLayers());
  map.fitBounds(group.getBounds(), { padding: [40, 40] });
}

  }catch(err){
    console.error(err);
    alert("Error loading data");
  }
}

window.loadEstuary = loadEstuary;