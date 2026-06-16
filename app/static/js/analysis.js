// =========================
// ANALYSIS MENU
// =========================

document.getElementById("analysisType")
.addEventListener("change", function(){

  const value = this.value;

  const sub = document.getElementById("analysisSubOptions");
  const panel = document.getElementById("dynamicPanel");

  sub.innerHTML = "";
  panel.innerHTML = "";

  if(value === "highest"){
    showHighestOptions();
  }
  else if(value === "lowest"){
    showLowestOptions();
  }
  else if(value === "state"){
    window.location.href = "/static/state_ranks.html";
  }
  else if(value === "estuary"){
    window.location.href = "/static/estuary_ranks.html";
  }
});


// =========================
// HIGHEST OPTIONS
// =========================

function showHighestOptions(){

  const sub = document.getElementById("analysisSubOptions");
  const panel = document.getElementById("dynamicPanel");

  panel.innerHTML = "";

  sub.innerHTML = `
    <label>Select Category:</label>
    <select id="highestCategory">
      <option value="">-- Choose --</option>
      <option value="microplastic">Microplastics</option>
      <option value="others">Others</option>
    </select>
  `;

  document
    .getElementById("highestCategory")
    .addEventListener("change", function(){

      if(this.value === "microplastic"){

        sub.innerHTML = `
          <label>Select Category:</label>
          <select id="highestCategory">
            <option value="microplastic" selected>Microplastics</option>
          </select>

          <br><br>

          <label>Select Medium:</label>
          <select id="highestMedium">
            <option value="">-- Choose --</option>
            <option value="water">Water</option>
            <option value="sediment">Sediment</option>
          </select>
        `;

        document
          .getElementById("highestMedium")
          .addEventListener("change", function(){

            if(this.value){
              showHighestMicroplastic(this.value);
            }
          });
      }

      else if(this.value === "others"){
        showHighestPanel();
      }
    });
}


// =========================
// LOWEST OPTIONS
// =========================

function showLowestOptions(){

  const sub = document.getElementById("analysisSubOptions");
  const panel = document.getElementById("dynamicPanel");

  panel.innerHTML = "";

  sub.innerHTML = `
    <label>Select Category:</label>
    <select id="lowestCategory">
      <option value="">-- Choose --</option>
      <option value="microplastic">Microplastics</option>
      <option value="others">Others</option>
    </select>
  `;

  document
    .getElementById("lowestCategory")
    .addEventListener("change", function(){

      if(this.value === "microplastic"){

        sub.innerHTML = `
          <label>Select Category:</label>
          <select id="lowestCategory">
            <option value="microplastic" selected>Microplastics</option>
          </select>

          <br><br>

          <label>Select Medium:</label>
          <select id="lowestMedium">
            <option value="">-- Choose --</option>
            <option value="water">Water</option>
            <option value="sediment">Sediment</option>
          </select>
        `;

        document
          .getElementById("lowestMedium")
          .addEventListener("change", function(){

            if(this.value){
              showLowestMicroplastic(this.value);
            }
          });
      }

      else if(this.value === "others"){
        showLowestPanel();
      }
    });
}


// =========================
// HIGHEST MICROPLASTIC
// =========================

async function showHighestMicroplastic(medium){

  const panel = document.getElementById("dynamicPanel");

  panel.innerHTML = "Loading...";

  const allPoints = await getAllEstuaryData();

  let highest = {
    abundance:{value:0, station:null, estuary:null},
    color:{key:null, value:0, station:null, estuary:null},
    size:{key:null, value:0, station:null, estuary:null},
    shape:{key:null, value:0, station:null, estuary:null}
  };

  allPoints.forEach(p=>{

    const ab = p[`${medium}_abundance`] || 0;

    if(ab > highest.abundance.value){
      highest.abundance = {
        value:ab,
        station:p.station_code,
        estuary:p.estuary
      };
    }

    for(const [k,v] of Object.entries(p.color?.[medium] || {})){
      if(v > highest.color.value){
        highest.color = {
          key:k,
          value:v,
          station:p.station_code,
          estuary:p.estuary
        };
      }
    }

    for(const [k,v] of Object.entries(p.size?.[medium] || {})){
      if(v > highest.size.value){
        highest.size = {
          key:k,
          value:v,
          station:p.station_code,
          estuary:p.estuary
        };
      }
    }

    for(const [k,v] of Object.entries(p.shape?.[medium] || {})){
      if(v > highest.shape.value){
        highest.shape = {
          key:k,
          value:v,
          station:p.station_code,
          estuary:p.estuary
        };
      }
    }
  });

  panel.innerHTML = `
    <h3>Highest Microplastics (${medium.toUpperCase()})</h3>

    <b>Abundance:</b>
    ${highest.abundance.value}
    at ${highest.abundance.station}
    (${highest.abundance.estuary})<br>

    <b>Color:</b>
    ${highest.color.key}
    (${highest.color.value})
    at ${highest.color.station}
    (${highest.color.estuary})<br>

    <b>Size:</b>
    ${formatKey(highest.size.key)}
    (${highest.size.value})
    at ${highest.size.station}
    (${highest.size.estuary})<br>

    <b>Shape:</b>
    ${highest.shape.key}
    (${highest.shape.value})
    at ${highest.shape.station}
    (${highest.shape.estuary})
  `;
}


// =========================
// LOWEST MICROPLASTIC
// =========================

async function showLowestMicroplastic(medium){

  const panel = document.getElementById("dynamicPanel");

  panel.innerHTML = "Loading...";

  const allPoints = await getAllEstuaryData();

  let lowest = {
    abundance:{value:Infinity, station:null, estuary:null},
    color:{key:null, value:Infinity, station:null, estuary:null},
    size:{key:null, value:Infinity, station:null, estuary:null},
    shape:{key:null, value:Infinity, station:null, estuary:null}
  };

  allPoints.forEach(p=>{

    const ab = p[`${medium}_abundance`] || 0;

    if(ab < lowest.abundance.value){
      lowest.abundance = {
        value:ab,
        station:p.station_code,
        estuary:p.estuary
      };
    }

    for(const [k,v] of Object.entries(p.color?.[medium] || {})){
      if(v < lowest.color.value){
        lowest.color = {
          key:k,
          value:v,
          station:p.station_code,
          estuary:p.estuary
        };
      }
    }

    for(const [k,v] of Object.entries(p.size?.[medium] || {})){
      if(v < lowest.size.value){
        lowest.size = {
          key:k,
          value:v,
          station:p.station_code,
          estuary:p.estuary
        };
      }
    }

    for(const [k,v] of Object.entries(p.shape?.[medium] || {})){
      if(v < lowest.shape.value){
        lowest.shape = {
          key:k,
          value:v,
          station:p.station_code,
          estuary:p.estuary
        };
      }
    }
  });

  panel.innerHTML = `
    <h3>Lowest Microplastics (${medium.toUpperCase()})</h3>

    <b>Abundance:</b>
    ${lowest.abundance.value}
    at ${lowest.abundance.station}
    (${lowest.abundance.estuary})<br>

    <b>Color:</b>
    ${lowest.color.key}
    (${lowest.color.value})
    at ${lowest.color.station}
    (${lowest.color.estuary})<br>

    <b>Size:</b>
    ${formatKey(lowest.size.key)}
    (${lowest.size.value})
    at ${lowest.size.station}
    (${lowest.size.estuary})<br>

    <b>Shape:</b>
    ${lowest.shape.key}
    (${lowest.shape.value})
    at ${lowest.shape.station}
    (${lowest.shape.estuary})
  `;
}

// =========================
// HIGHEST WATER QUALITY
// =========================

async function showHighestPanel(){

  const panel = document.getElementById("dynamicPanel");
  panel.innerHTML = "Loading...";

  const token = localStorage.getItem("access_token");
  const estuaries = ["Palar","Kollidam","Pulicat"];

  let allPoints = [];

  for(const est of estuaries){

    const res = await fetch(
      `${API_BASE}/estuaries/${est}/water-quality`,
      {
        headers:{
          Authorization:`Bearer ${token}`
        }
      }
    );

    if(!res.ok) continue;

    const data = await res.json();

    if(data.points){
      data.points.forEach(p=>{
        allPoints.push({
          ...p,
          estuary: est
        });
      });
    }
  }

  if(allPoints.length === 0){
    panel.innerHTML = "No water quality data found.";
    return;
  }

  const highestTemp =
    allPoints.reduce((a,b)=>
      (b.temperature_c || 0) >
      (a.temperature_c || 0) ? b : a
    );

  const highestPH =
    allPoints.reduce((a,b)=>
      (b.ph || 0) >
      (a.ph || 0) ? b : a
    );

  const highestSalinity =
    allPoints.reduce((a,b)=>
      (b.salinity_psu || 0) >
      (a.salinity_psu || 0) ? b : a
    );

  const highestDO =
    allPoints.reduce((a,b)=>
      (b.dissolved_oxygen_mg_l || 0) >
      (a.dissolved_oxygen_mg_l || 0) ? b : a
    );

  panel.innerHTML = `
    <h3>Highest Water Quality Values</h3>

    <b>Temperature:</b>
    ${highestTemp.temperature_c}
    at ${highestTemp.station_code}
    (${highestTemp.estuary})<br>

    <b>pH:</b>
    ${highestPH.ph}
    at ${highestPH.station_code}
    (${highestPH.estuary})<br>

    <b>Salinity:</b>
    ${highestSalinity.salinity_psu}
    at ${highestSalinity.station_code}
    (${highestSalinity.estuary})<br>

    <b>Dissolved Oxygen:</b>
    ${highestDO.dissolved_oxygen_mg_l}
    at ${highestDO.station_code}
    (${highestDO.estuary})
  `;
}


// =========================
// LOWEST WATER QUALITY
// =========================

async function showLowestPanel(){

  const panel = document.getElementById("dynamicPanel");
  panel.innerHTML = "Loading...";

  const token = localStorage.getItem("access_token");
  const estuaries = ["Palar","Kollidam","Pulicat"];

  let allPoints = [];

  for(const est of estuaries){

    const res = await fetch(
      `${API_BASE}/estuaries/${est}/water-quality`,
      {
        headers:{
          Authorization:`Bearer ${token}`
        }
      }
    );

    if(!res.ok) continue;

    const data = await res.json();

    if(data.points){
      data.points.forEach(p=>{
        allPoints.push({
          ...p,
          estuary: est
        });
      });
    }
  }

  if(allPoints.length === 0){
    panel.innerHTML = "No water quality data found.";
    return;
  }

  const lowestTemp =
    allPoints.reduce((a,b)=>
      (b.temperature_c || 0) <
      (a.temperature_c || 0) ? b : a
    );

  const lowestPH =
    allPoints.reduce((a,b)=>
      (b.ph || 0) <
      (a.ph || 0) ? b : a
    );

  const lowestSalinity =
    allPoints.reduce((a,b)=>
      (b.salinity_psu || 0) <
      (a.salinity_psu || 0) ? b : a
    );

  const lowestDO =
    allPoints.reduce((a,b)=>
      (b.dissolved_oxygen_mg_l || 0) <
      (a.dissolved_oxygen_mg_l || 0) ? b : a
    );

  panel.innerHTML = `
    <h3>Lowest Water Quality Values</h3>

    <b>Temperature:</b>
    ${lowestTemp.temperature_c}
    at ${lowestTemp.station_code}
    (${lowestTemp.estuary})<br>

    <b>pH:</b>
    ${lowestPH.ph}
    at ${lowestPH.station_code}
    (${lowestPH.estuary})<br>

    <b>Salinity:</b>
    ${lowestSalinity.salinity_psu}
    at ${lowestSalinity.station_code}
    (${lowestSalinity.estuary})<br>

    <b>Dissolved Oxygen:</b>
    ${lowestDO.dissolved_oxygen_mg_l}
    at ${lowestDO.station_code}
    (${lowestDO.estuary})
  `;
}