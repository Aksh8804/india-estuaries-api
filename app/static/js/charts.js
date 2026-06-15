function drawCharts(){

  const layer = document.getElementById("layerSelect").value;
  const medium = document.getElementById("mediumSelect").value;

  if(!currentEstuary || !medium || !layer || currentPoints.length === 0){
    return;
  }

  document.getElementById("chartContainer").style.display="block";

  if(barChart) barChart.destroy();
  if(pieChart) pieChart.destroy();

  markers.clearLayers(); 
  pieMarkers.clearLayers();

if(layer === "abundance"){
  drawAbundance();
  
}

  else if(layer === "size"){
    drawStacked("size", SIZE_KEYS);
    drawMapPieCharts("size", SIZE_KEYS);
  }

  else if(layer === "shape"){
    drawStacked("shape", SHAPE_KEYS);
    drawMapPieCharts("shape", SHAPE_KEYS);
  }

  else if(layer === "color"){
    drawStacked("color", COLOR_KEYS);
    drawMapPieCharts("color", COLOR_KEYS);
  }
document.getElementById("chartDownloadBtns").style.display = "flex";
}
function drawAbundance(){

  const medium = document.getElementById("mediumSelect").value;

  const barCtx = document.getElementById("barCanvas").getContext("2d");
  const pieCtx = document.getElementById("pieCanvas").getContext("2d");

  const values = currentPoints.map(p => p[`${medium}_abundance`] || 0);
  const labels = currentPoints.map(p => p.station_code);

  // ===== BAR CHART =====
  barChart = new Chart(barCtx,{
    type:"bar",
    data:{
      labels: labels,
      datasets:[{
        label: "Abundance",
        data: values,
        backgroundColor: CHART_COLORS.slice(0, values.length)
      }]
    },
    options:{
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        title:{
          display:true,
          text: medium.toUpperCase() + " Abundance by Station"
        },
        legend:{
          position:"right",
          labels:{
            generateLabels(chart){
              const data = chart.data;
              return data.labels.map((label, i) => ({
                text: `${label} (${data.datasets[0].data[i]})`,
                fillStyle: data.datasets[0].backgroundColor[i],
                hidden: false,
                index: i
              }));
            }
          }
        }
      },
      scales:{
        y:{
          beginAtZero:true,
          title:{
            display:true,
            text:"Abundance"
          }
        }
      }
    }
  });

  // ===== PIE CHART =====
  pieChart = new Chart(pieCtx,{
    type:"pie",
    data:{
      labels: labels,
      datasets:[{
        data: values,
        backgroundColor: CHART_COLORS.slice(0, values.length)
      }]
    },
    options:{
      responsive:true,
      plugins:{
        title:{
          display:true,
          text:"Distribution Across Stations"
        },
        legend:{
          position:"right",
          labels:{
            generateLabels(chart){
              const data = chart.data;
              return data.labels.map((label, i) => ({
                text: `${label} (${data.datasets[0].data[i]})`,
                fillStyle: data.datasets[0].backgroundColor[i],
                hidden: false,
                index: i
              }));
            }
          }
        }
      }
    }
  });
}

// ===== Pie Chart on map =====

function drawMapPieCharts(type, keys){

  const medium = document.getElementById("mediumSelect").value;

  pieMarkers.clearLayers();

  currentPoints.forEach(pt => {

    const values = keys.map(k => (pt[type]?.[medium]?.[k] || 0));

    const total = values.reduce((a,b)=>a+b,0);
    if(total === 0) return;

    const canvas = document.createElement("canvas");
    canvas.width = 60;
    canvas.height = 60;

    new Chart(canvas,{
      type:"pie",
      data:{
        labels: keys.map(k=>formatKey(k)),
        datasets:[{
          data: values,
          backgroundColor: CHART_COLORS
        }]
      },
      options:{
        responsive:false,
        plugins:{
          legend:{display:false}
        }
      }
    });

    const icon = L.divIcon({
      html: canvas,
      className:"",
      iconSize:[60,60]
    });

    const marker = L.marker([pt.latitude, pt.longitude],{icon});

    pieMarkers.addLayer(marker);

  });

addMapLegend(keys);

}

// ===== Abundance Pie Chart on Map =====
function drawAbundanceMapPie(){

  const medium = document.getElementById("mediumSelect").value;

  pieMarkers.clearLayers();

  const values = currentPoints.map(p => p[`${medium}_abundance`] || 0);

  const total = values.reduce((a,b)=>a+b,0);
  if(total === 0) return;

  currentPoints.forEach((pt,i)=>{

    const canvas = document.createElement("canvas");
    canvas.width = 60;
    canvas.height = 60;

    const stationValue = values[i];
    const others = total - stationValue;

    new Chart(canvas,{
      type:"pie",
      data:{
        labels:["Station","Others"],
        datasets:[{
          data:[stationValue, others],
          backgroundColor:["#FF8C00","#D3D3D3"]
        }]
      },
      options:{
        responsive:false,
        plugins:{
          legend:{display:false}
        }
      }
    });

    const icon = L.divIcon({
      html: canvas,
      className:"",
      iconSize:[60,60]
    });

    const marker = L.marker([pt.latitude, pt.longitude],{icon});

    pieMarkers.addLayer(marker);

  });

}

function drawTypeChart(){

  const layer = document.getElementById("layerSelect").value;
  const medium = document.getElementById("mediumSelect").value;
  const type = document.getElementById("typeSelect").value;

  if(!layer || !medium || !type) return;

  // Show bottom chart container
  document.getElementById("chartContainer").style.display = "block";

  // Clear previous markers
  markers.clearLayers();
  pieMarkers.clearLayers();

  currentPoints.forEach(pt => {

    const value = pt[layer]?.[medium]?.[type] || 0;

    const canvas = document.createElement("canvas");
    canvas.width = 50;
    canvas.height = 80;

    // ✅ VALUE LABEL PLUGIN
    const valueLabelPlugin = {
      id: 'valueLabel',
      afterDatasetsDraw(chart){
        const {ctx} = chart;
        ctx.save();

        chart.data.datasets.forEach((dataset, i) => {
          const meta = chart.getDatasetMeta(i);

          meta.data.forEach((bar, index) => {
            if(!bar.x || !bar.y) return;

            const val = dataset.data[index] ?? 0;

            const centerY = bar.y + (bar.base - bar.y) / 2;

const barHeight = bar.base - bar.y;

ctx.fillStyle = "#000";
ctx.font = "bold 10px Arial";
ctx.textAlign = "center";
ctx.textBaseline = "middle";

ctx.fillText(
  (Number(val) || 0).toFixed(2),
  bar.x,
  centerY
);
          });
        });

        ctx.restore();
      }
    };

    // ✅ CHART
    new Chart(canvas,{
      type:"bar",
      data:{
        labels:[""],
        datasets:[{
          data:[value],
          backgroundColor:"#FF8C00"
        }]
      },
      options:{
        responsive:false,
        plugins:{
          legend:{display:false},
          tooltip:{enabled:false}
        },
        scales:{
          x:{display:false},
          y:{
            beginAtZero:true,
            ticks:{display:false},
            grid:{display:false}
          }
        }
      },
      plugins:[valueLabelPlugin] // ✅ correct placement
    });

    // ✅ ADD TO MAP
    const icon = L.divIcon({
      html: canvas,
      className:"",
      iconSize:[50,80]
    });

    const marker = L.marker([pt.latitude, pt.longitude], {icon})
      .bindPopup(`
  <b>${pt.station_code}</b><br>
  Abundance: ${(Number(value) || 0).toFixed(2)}
`);

    markers.addLayer(marker);

  }); // ✅ forEach CLOSED

} // ✅ function CLOSED

function drawTypeMap(type, layer, medium){

  markers.clearLayers();
  pieMarkers.clearLayers();

  currentPoints.forEach(pt=>{

    const value = pt[layer]?.[medium]?.[type] || 0;

    const marker = L.marker([pt.latitude, pt.longitude])
      .bindPopup(`
        <b>${pt.station_code}</b><br>
        ${formatKey(type)}: ${value}
      `);

    markers.addLayer(marker);

  });

}
document.getElementById("typeSelect")
.addEventListener("change", drawTypeChart);



function drawStacked(type, keys){

  const medium = document.getElementById("mediumSelect").value;

  const barCtx = document.getElementById("barCanvas").getContext("2d");
  const pieCtx = document.getElementById("pieCanvas").getContext("2d");

  // ===== STACKED BAR =====
  barChart = new Chart(barCtx,{
    type:"bar",
    data:{
      labels: currentPoints.map(p=>p.station_code),
      datasets: keys.map((k, index) => ({
        label: formatKey(k),
        data: currentPoints.map(p =>
          (p[type]?.[medium]?.[k] || 0)
        ),
        backgroundColor: CHART_COLORS[index % CHART_COLORS.length]
      }))
    },
    options:{
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        title:{
          display:true,
          text: `${type.toUpperCase()} (${medium.toUpperCase()})`
        },
        legend:{
          position:"right",
          labels:{
            generateLabels(chart){
              return chart.data.datasets.map((ds, i)=>{
                
                const total = ds.data.reduce((a,b)=>a+b,0);

                return {
                  text: `${ds.label} (${total})`,
                  fillStyle: ds.backgroundColor,
                  hidden: !chart.isDatasetVisible(i),
                  datasetIndex: i
                };
              });
            }
          }
        }
      },
      scales:{
        x:{ stacked:true },
        y:{ stacked:true, beginAtZero:true }
      }
    }
  });

  // ===== PIE (TOTAL DISTRIBUTION) =====
  const totals = {};
  keys.forEach(k => totals[k] = 0);

  currentPoints.forEach(p=>{
    keys.forEach(k=>{
      totals[k] += (p[type]?.[medium]?.[k] || 0);
    });
  });

  pieChart = new Chart(pieCtx,{
    type:"pie",
    data:{
      labels: keys.map(k => formatKey(k)),
      datasets:[{
        data: keys.map(k=>totals[k]),
        backgroundColor: CHART_COLORS.slice(0, keys.length)
      }]
    },
    options:{
      responsive:true,
      plugins:{
        title:{
          display:true,
          text:`Total ${type.toUpperCase()} Distribution`
        },
        legend:{
          position:"right",
          labels:{
            generateLabels(chart){
              const data = chart.data;
              return data.labels.map((label, i) => ({
                text: `${label} (${data.datasets[0].data[i]})`,
                fillStyle: data.datasets[0].backgroundColor[i],
                hidden: false,
                index: i
              }));
            }
          }
        }
      }
    }
  });
}



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

  // ✅ remove legend first
  removeMapLegend();

  if(type === "pie"){
    drawAbundanceMapPie();   // legend will come
  }

  else if(type === "bar"){
    drawAbundanceMapBar();   // no legend
  }

});


function drawAbundanceMapBar(){

  removeMapLegend();

  const medium = document.getElementById("mediumSelect").value;

  currentPoints.forEach(pt => {

    const value = pt[`${medium}_abundance`] || 0;

    const canvas = document.createElement("canvas");
    canvas.width = 50;
    canvas.height = 80;

    new Chart(canvas,{
      type:"bar",
      data:{
        labels:[""],
        datasets:[{
          data:[value],
          backgroundColor:"#FF8C00"
        }]
      },
      options:{
        responsive:false,
        plugins:{
          legend:{display:false},
          tooltip:{enabled:false}
        },
        scales:{
          x:{display:false},
          y:{
            beginAtZero:true,
            ticks:{display:false},
            grid:{display:false}
          }
        }
      },

      plugins: [{
  id: 'valueLabel',
  afterDatasetsDraw(chart){
    const {ctx, chartArea:{top, bottom}} = chart;
    ctx.save();

    chart.data.datasets.forEach((dataset, i) => {
      const meta = chart.getDatasetMeta(i);

      meta.data.forEach((bar, index) => {

        const value = dataset.data[index] ?? 0;

        let yPos;
        const barHeight = bar.base - bar.y;

        // small bar → show above
        if(barHeight < 12){
          yPos = bar.y - 6;
        } else {
          // normal bar → center
          yPos = bar.y + barHeight / 2;
        }

        // keep inside canvas
        yPos = Math.max(top + 10, Math.min(bottom - 10, yPos));

        ctx.fillStyle = "#000";
        ctx.font = "bold 10px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        ctx.fillText(
          (Number(value) || 0).toFixed(2),
          bar.x,
          yPos
        );

      });
    });

    ctx.restore();
  }
}]
    });

    const icon = L.divIcon({
      html: canvas,
      className:"",
      iconSize:[50,80]
    });

    const marker = L.marker([pt.latitude, pt.longitude],{icon})
      .bindPopup(`
        <b>${pt.station_code}</b><br>
        Abundance: ${(Number(value) || 0).toFixed(2)}
      `);

    markers.addLayer(marker);

  });
}



// ===== DOWNLOAD BAR CHART =====
function downloadBarChart(){

  if(!barChart){
    alert("Generate chart first");
    return;
  }

  const originalCanvas = document.getElementById("barCanvas");

  const tempCanvas = document.createElement("canvas");
  tempCanvas.width = originalCanvas.width;
  tempCanvas.height = originalCanvas.height;

  const ctx = tempCanvas.getContext("2d");

  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);

  ctx.drawImage(originalCanvas, 0, 0);

  const link = document.createElement("a");
  link.download = `${currentEstuary}_bar_chart.png`;
  link.href = tempCanvas.toDataURL("image/png");

  link.click();
}

// ===== DOWNLOAD PIE CHART =====
function downloadPieChart(){

  if(!pieChart){
    alert("Generate chart first");
    return;
  }

  const originalCanvas = document.getElementById("pieCanvas");

  const tempCanvas = document.createElement("canvas");
  tempCanvas.width = originalCanvas.width;
  tempCanvas.height = originalCanvas.height;

  const ctx = tempCanvas.getContext("2d");

  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);

  ctx.drawImage(originalCanvas, 0, 0);

  const link = document.createElement("a");
  link.download = `${currentEstuary}_pie_chart.png`;
  link.href = tempCanvas.toDataURL("image/png");

  link.click();
}

async function downloadChartsPDF(){

  if(!barChart && !pieChart){
    alert("Generate charts first");
    return;
  }

  const { jsPDF } = window.jspdf;

  const pdf = new jsPDF("p", "mm", "a4");

  let yPosition = 10;

  // ===== TITLE =====
  pdf.setFontSize(16);
  pdf.text("Estuary Microplastic Analysis", 10, yPosition);

  yPosition += 10;

  // ===== BAR CHART =====
  if(barChart){
    const barCanvas = document.getElementById("barCanvas");

    const barImg = barCanvas.toDataURL("image/png");

    pdf.setFontSize(12);
    pdf.text("Bar Chart", 10, yPosition);

    yPosition += 5;

    pdf.addImage(barImg, "PNG", 10, yPosition, 180, 80);

    yPosition += 90;
  }

  // ===== NEW PAGE IF NEEDED =====
  if(yPosition > 200){
    pdf.addPage();
    yPosition = 10;
  }

  // ===== PIE CHART =====
  if(pieChart){
    const pieCanvas = document.getElementById("pieCanvas");

    const pieImg = pieCanvas.toDataURL("image/png");

    pdf.setFontSize(12);
    pdf.text("Pie Chart", 10, yPosition);

    yPosition += 5;

    pdf.addImage(pieImg, "PNG", 10, yPosition, 150, 150);
  }

  // ===== SAVE =====
  pdf.save(`${currentEstuary}_charts.pdf`);
}


window.drawAbundance = drawAbundance;
window.drawStacked = drawStacked;
window.drawMapPieCharts = drawMapPieCharts;
window.drawAbundanceMapPie = drawAbundanceMapPie;
window.drawTypeChart = drawTypeChart;
window.drawTypeMap = drawTypeMap;