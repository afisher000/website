


function plot_map(mapID, splits) {
    const map = new mapboxgl.Map({
        container: mapID,
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [splits[0].lng, splits[0].lat], // Use the first coordinate as the center
        zoom: 13
    });

    map.on('load', function() {
        map.addLayer({
            id: 'line-plot',
            type: 'line',
            source: {
                type: 'geojson',
                data: {
                    type: 'Feature',
                    properties: {},
                    geometry: {
                        type: 'LineString',
                        coordinates: splits.map(split => [split.lng, split.lat])
                    }
                }
            },
            layout: {
                'line-join': 'round',
                'line-cap': 'round'
            },
            paint: {
                'line-color': '#f00',
                'line-width': 5
            }
        });
    });

}