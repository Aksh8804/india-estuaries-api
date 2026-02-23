document.addEventListener("DOMContentLoaded", function () {
    const map = L.map('map').setView([20.0, 78.0], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18
    }).addTo(map);

    const estuarySelect = document.getElementById("estuarySelect");

    estuarySelect.addEventListener("change", async function () {
        const estuaryName = this.value;
        if (!estuaryName) return;

        console.log(`Fetching: /estuary-data/${estuaryName}`);

        try {
            const response = await fetch(`/estuary-data/${estuaryName}`);
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const points = await response.json();
            console.log("API response:", points);

            map.eachLayer(layer => {
                if (layer instanceof L.Marker) map.removeLayer(layer);
            });

            points.forEach(p => {
                L.marker([p.latitude, p.longitude])
                    .addTo(map)
                    .bindPopup(
                        `<b>${p.station_code}</b><br>
                        Water: ${p.water_abundance}<br>
                        Sediment: ${p.sediment_abundance}<br>
                        Date: ${p.sample_date}`
                    );
            });
        } catch (err) {
            console.error("Fetch error:", err);
        }
    });
});
