const map = L.map("map").setView([12.8, 80.2], 7);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap"
}).addTo(map);
// ===== MAP LEGEND =====
let mapLegend = null;

function addMapLegend(keys){

  // remove old legend
  if(mapLegend){
    map.removeControl(mapLegend);
  }

  mapLegend = L.control({ position: "bottomleft" });

  mapLegend.onAdd = function(){
    const div = L.DomUtil.create("div", "map-legend");

    div.style.background = "white";
    div.style.padding = "10px";
    div.style.border = "1px solid #ccc";
    div.style.borderRadius = "6px";
    div.style.fontSize = "12px";
    div.style.lineHeight = "18px";

    keys.forEach((k,i)=>{
      div.innerHTML += `
        <div style="display:flex; align-items:center; margin-bottom:4px;">
          <span style="
            width:14px;
            height:14px;
            background:${CHART_COLORS[i]};
            display:inline-block;
            margin-right:6px;
          "></span>
          ${formatKey(k)}
        </div>
      `;
    });

    return div;
  };

  mapLegend.addTo(map);
}


function removeMapLegend(){
  if(mapLegend){
    map.removeControl(mapLegend);
    mapLegend = null;
  }
}

const markers = L.layerGroup().addTo(map);
const pieMarkers = L.layerGroup().addTo(map);

window.map = map;
window.markers = markers;
window.pieMarkers = pieMarkers;
window.addMapLegend = addMapLegend;
window.removeMapLegend = removeMapLegend;
