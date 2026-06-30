console.log("main loaded");
// =========================
// GLOBAL CHART SETTINGS
// =========================

Chart.defaults.font.family = "Arial";
Chart.defaults.font.size = 13;
Chart.defaults.color = "#333";


// =========================
// LAYER CHANGE
// =========================

document.getElementById("layerSelect")
.addEventListener("change", function(){

  document.getElementById("chartDownloadBtns").style.display = "none";

  const layer = this.value;
  const typeSelect = document.getElementById("typeSelect");
  const mapChartType = document.getElementById("mapChartType");

  typeSelect.innerHTML = `<option value="">-- Choose --</option>`;
  typeSelect.disabled = true;

  mapChartType.value = "";
  mapChartType.disabled = true;

  let keys = [];

  if(layer === "abundance"){

    mapChartType.disabled = false;

    markers.clearLayers();
    pieMarkers.clearLayers();

    drawCharts();

    document.getElementById("chartContainer").style.display = "block";
    return;
  }

  if(layer === "size"){
    keys = SIZE_KEYS;
  }
  else if(layer === "shape"){
    keys = SHAPE_KEYS;
  }
  else if(layer === "color"){
    keys = COLOR_KEYS;
  }

  typeSelect.disabled = false;

  keys.forEach(k => {
    const option = document.createElement("option");
    option.value = k;
    option.textContent = formatKey(k);
    typeSelect.appendChild(option);
  });

  drawCharts();

  document.getElementById("chartContainer").style.display = "block";
});


// =========================
// MEDIUM CHANGE
// =========================

document.getElementById("mediumSelect")
.addEventListener("change", function(){

  const layerSelect = document.getElementById("layerSelect");
  const typeSelect = document.getElementById("typeSelect");

  if(this.value){
    layerSelect.disabled = false;
  }
  else{
    layerSelect.disabled = true;
  }

  typeSelect.value = "";
  typeSelect.disabled = true;

  if(barChart){
    barChart.destroy();
  }

  if(pieChart){
    pieChart.destroy();
  }

  document.getElementById("chartDownloadBtns").style.display = "none";
});


// =========================
// MAP CHART TYPE CHANGE
// =========================

document.getElementById("mapChartType")
.addEventListener("change", function(){

  const type = this.value;
  const medium = document.getElementById("mediumSelect").value;

  if(!type || !medium){
    alert("Please select Medium first");
    return;
  }

  markers.clearLayers();
  pieMarkers.clearLayers();

  removeMapLegend();

  if(type === "pie"){
    drawAbundanceMapPie();
  }
  else if(type === "bar"){
    drawAbundanceMapBar();
  }
});


// =========================
// MICROPLASTIC TYPE CHANGE
// =========================

document.getElementById("typeSelect")
.addEventListener("change", drawTypeChart);

// =========================
// INITIAL PAGE SETUP
// =========================

window.addEventListener("load", () => {

  document.getElementById("chartContainer").style.display = "none";

  document.getElementById("chartDownloadBtns").style.display = "none";

});

document.getElementById("estuarySelect")
.addEventListener("change", async function(){

  currentEstuary = this.value;

  document.getElementById("categorySelect").disabled =
    !currentEstuary;

  document.getElementById("mediumSelect").disabled = true;
  document.getElementById("layerSelect").disabled = true;
  document.getElementById("typeSelect").disabled = true;

  document.getElementById("categorySelect").value = "";
  document.getElementById("mediumSelect").value = "";
  document.getElementById("layerSelect").value = "";
  document.getElementById("typeSelect").value = "";

  markers.clearLayers();
  pieMarkers.clearLayers();

  if(barChart) barChart.destroy();
  if(pieChart) pieChart.destroy();

  currentPoints = [];
});

document.getElementById("categorySelect")
.addEventListener("change", async function(){

  const category = this.value;

  document.getElementById("taskResult").innerHTML = "";
  document.getElementById("dynamicPanel").innerHTML = "";

  //markers.clearLayers();
  //pieMarkers.clearLayers();

  if(category === "microplastic"){

    document.getElementById("mediumSelect").disabled = false;
    document.getElementById("layerSelect").disabled = true;
    document.getElementById("typeSelect").disabled = true;

    return;
  }

  if(category === "others"){

    document.getElementById("mediumSelect").disabled = true;
    document.getElementById("layerSelect").disabled = true;
    document.getElementById("typeSelect").disabled = true;

    const token = localStorage.getItem("access_token");

    const res = await fetch(
      `${API_BASE}/estuaries/${currentEstuary}/water-quality`,
      {
        headers:{
          "Authorization": `Bearer ${token}`
        }
      }
    );

	const data = await res.json();

	markers.clearLayers();

	data.points.forEach(pt => {

    	const popup = `
        	<b>${pt.station_code}</b><br><br>

        	Temperature(°C): ${pt.temperature_c}<br>
        	pH: ${pt.ph}<br>
        	Salinity(psu): ${pt.salinity_psu}<br>
        	Dissolved Oxygen(mg/L): ${pt.dissolved_oxygen_mg_l}<br>
        	ORP(mV): ${pt.orp_mv}<br>
        	EC(µS/cm): ${pt.ec_us_cm}<br>
        	TDS(ppt): ${pt.tds_ppt}
    	`;

    	L.marker([pt.latitude, pt.longitude])
        	.bindPopup(popup)
        	.addTo(markers);
	});

	if(markers.getLayers().length){
    	map.fitBounds(
        	L.featureGroup(markers.getLayers()).getBounds(),
        	{padding:[40,40]}
    	);
	}
  }
});
