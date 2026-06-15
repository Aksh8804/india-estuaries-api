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