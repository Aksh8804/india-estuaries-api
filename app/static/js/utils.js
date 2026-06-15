function toggleMenu(){
  const menu = document.getElementById("taskMenu");
  menu.style.display = menu.style.display === "none" ? "block" : "none";
}

function formatObj(obj){
  if(!obj) return "No data";

  const keyMap = {
    "lt_1mm": "< 1 mm",
    "mm_1_to_2_5": "1 mm to 2.5 mm",
    "mm_2_5_to_5": "2.5 mm to 5 mm"
  };

  return Object.entries(obj)
    .map(([k,v]) => {
      const formattedKey = keyMap[k] || k;
      return `${formattedKey} : ${v}`;
    })
    .join("<br>");
}

function formatKey(key){
  const keyMap = {
    "lt_1mm": "< 1 mm",
    "mm_1_to_2_5": "1 mm to 2.5 mm",
    "mm_2_5_to_5": "2.5 mm to 5 mm",
    "fiber": "Fiber",
    "fragment": "Fragment",
    "film": "Film",
    "foam": "Foam",
    "pellet": "Pellet"
  };

  return keyMap[key] || key;
}