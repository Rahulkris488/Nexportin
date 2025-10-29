document.addEventListener('DOMContentLoaded', () => {
    // Initialize map
    mapboxgl.accessToken = 'YOUR_MAPBOX_ACCESS_TOKEN'; // Replace with actual token
    const map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/light-v10',
        center: [-95.7129, 37.0902], // Center of US
        zoom: 4
    });

    // Add navigation controls
    map.addControl(new mapboxgl.NavigationControl());

    // Load supply chain data
    let networkData = null;
    let shipmentMarkers = [];

    async function loadNetworkData() {
        try {
            const response = await fetch('/api/map');
            networkData = await response.json();
            updateMap();
        } catch (error) {
            console.error('Failed to load network data:', error);
        }
    }

    function updateMap() {
        if (!networkData) return;

        // Clear existing layers
        if (map.getLayer('routes')) map.removeLayer('routes');
        if (map.getLayer('nodes')) map.removeLayer('nodes');
        if (map.getSource('routes')) map.removeSource('routes');
        if (map.getSource('nodes')) map.removeSource('nodes');

        // Remove existing shipment markers
        shipmentMarkers.forEach(marker => marker.remove());
        shipmentMarkers = [];

        // Add routes
        map.addSource('routes', {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: networkData.edges.map(edge => ({
                    type: 'Feature',
                    geometry: {
                        type: 'LineString',
                        coordinates: [
                            [networkData.nodes[edge.source].location.lng, 
                             networkData.nodes[edge.source].location.lat],
                            [networkData.nodes[edge.target].location.lng, 
                             networkData.nodes[edge.target].location.lat]
                        ]
                    },
                    properties: {
                        id: edge.id,
                        status: edge.status,
                        type: edge.transport_type
                    }
                }))
            }
        });

        map.addLayer({
            id: 'routes',
            type: 'line',
            source: 'routes',
            layout: {
                'line-join': 'round',
                'line-cap': 'round'
            },
            paint: {
                'line-color': [
                    'match',
                    ['get', 'status'],
                    'disrupted', '#e74c3c',
                    '#3498db'
                ],
                'line-width': 2,
                'line-opacity': [
                    'match',
                    ['get', 'status'],
                    'disrupted', 0.8,
                    0.6
                ]
            }
        });

        // Add nodes
        map.addSource('nodes', {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: networkData.nodes.map(node => ({
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: [node.location.lng, node.location.lat]
                    },
                    properties: {
                        id: node.id,
                        type: node.type,
                        status: node.status
                    }
                }))
            }
        });

        map.addLayer({
            id: 'nodes',
            type: 'circle',
            source: 'nodes',
            paint: {
                'circle-radius': 8,
                'circle-color': [
                    'match',
                    ['get', 'type'],
                    'factory', '#2ecc71',
                    'warehouse', '#e67e22',
                    '#95a5a6'
                ],
                'circle-opacity': [
                    'match',
                    ['get', 'status'],
                    'disrupted', 0.6,
                    1
                ],
                'circle-stroke-width': 2,
                'circle-stroke-color': '#fff'
            }
        });

        // Add shipment markers
        networkData.shipments.forEach(shipment => {
            const el = document.createElement('div');
            el.className = 'shipment-marker';
            el.style.backgroundColor = '#3498db';
            el.style.width = '12px';
            el.style.height = '12px';
            el.style.borderRadius = '50%';
            el.style.border = '2px solid white';

            const marker = new mapboxgl.Marker(el)
                .setLngLat([shipment.position.lng, shipment.position.lat])
                .addTo(map);

            shipmentMarkers.push(marker);
        });

        // Add node click handlers
        map.on('click', 'nodes', (e) => {
            const features = map.queryRenderedFeatures(e.point, {
                layers: ['nodes']
            });

            if (!features.length) return;

            const node = features[0].properties;
            const nodeDetails = networkData.nodes.find(n => n.id === node.id);

            document.getElementById('nodeDetails').innerHTML = `
                <h4>${node.id}</h4>
                <p>Type: ${node.type}</p>
                <p>Status: ${node.status}</p>
                <p>Inventory: ${nodeDetails.inventory}</p>
            `;
        });

        // Change cursor on node hover
        map.on('mouseenter', 'nodes', () => {
            map.getCanvas().style.cursor = 'pointer';
        });

        map.on('mouseleave', 'nodes', () => {
            map.getCanvas().style.cursor = '';
        });
    }

    // Layer visibility controls
    document.getElementById('showFactories').addEventListener('change', (e) => {
        map.setLayoutProperty('nodes', 'visibility', e.target.checked ? 'visible' : 'none');
    });

    document.getElementById('showWarehouses').addEventListener('change', (e) => {
        map.setLayoutProperty('nodes', 'visibility', e.target.checked ? 'visible' : 'none');
    });

    document.getElementById('showRoutes').addEventListener('change', (e) => {
        map.setLayoutProperty('routes', 'visibility', e.target.checked ? 'visible' : 'none');
    });

    document.getElementById('showShipments').addEventListener('change', (e) => {
        shipmentMarkers.forEach(marker => {
            marker.getElement().style.display = e.target.checked ? 'block' : 'none';
        });
    });

    // Load initial data
    map.on('load', loadNetworkData);

    // Refresh data periodically
    setInterval(loadNetworkData, 5000);
});