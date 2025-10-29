# Dynamic Recovery Supply Chain Simulator

A Flask-based web application for simulating and visualizing supply chain networks, allowing users to inject disruptions and explore recovery strategies with real-time impact updates.

## Features

- Interactive supply chain network visualization using Mapbox GL JS
- Real-time simulation of shipments and disruptions
- Discrete-event simulation engine for accurate time-based events
- Recovery strategy analysis and impact assessment
- Interactive analytics dashboard with D3.js visualizations

## Requirements

- Python 3.8+
- Flask and Flask-CORS
- SimPy for discrete-event simulation
- Pandas and NumPy for data analysis
- D3.js for visualization
- Mapbox GL JS for map visualization

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd dynamic-recovery-supply-chain-simulator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install flask flask-cors simpy pandas numpy python-dotenv
```

4. Set up Mapbox access token:
Create a `.env` file in the project root and add your Mapbox access token:
```
MAPBOX_ACCESS_TOKEN=your_token_here
```

## Project Structure

```
backend/
├── app.py                 # Main Flask application entry
├── routes/
│   ├── simulation.py      # Simulation endpoints
│   ├── disruptions.py     # Disruption management
│   └── recovery.py        # Recovery strategy endpoints
├── models/
│   ├── supply_chain.py    # Supply chain network model
│   └── event_engine.py    # Discrete-event simulation engine
├── utils/
│   ├── data_loader.py     # Data loading utilities
│   └── analytics.py       # Analytics calculations
├── static/
│   ├── js/
│   │   ├── simulation.js  # Simulation frontend logic
│   │   ├── map.js        # Map visualization
│   │   ├── analytics.js  # Analytics charts
│   │   └── ui.js         # UI interactions
│   └── css/
│       └── style.css     # Application styles
└── templates/
    ├── index.html        # Main dashboard
    ├── map.html         # Map view
    └── analytics.html    # Analytics dashboard
```

## Usage

1. Start the Flask application:
```bash
python backend/app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Use the dashboard to:
   - Start/pause/reset the simulation
   - Inject disruptions (e.g., close a port, reduce supplier output)
   - Apply recovery strategies
   - View real-time analytics and impact assessments

## Example Workflow

1. **Start Simulation**
   - Click "Start Simulation" to begin
   - Observe shipments moving on the map

2. **Inject Disruption**
   - Click "Inject Disruption"
   - Select disruption type (e.g., "Highway X closed")
   - Set duration and severity
   - Submit to see impact

3. **Apply Recovery**
   - Click "Apply Recovery Strategy"
   - Choose strategy (e.g., "Reroute via Y")
   - View updated metrics and costs

## Development

### Adding New Features

1. **New Disruption Types**
   - Add disruption logic in `models/supply_chain.py`
   - Update the UI in `templates/index.html`
   - Add corresponding endpoint in `routes/disruptions.py`

2. **Custom Recovery Strategies**
   - Implement strategy in `models/supply_chain.py`
   - Add UI components in `templates/index.html`
   - Create endpoint in `routes/recovery.py`

### Testing

Run the simulation with example scenarios:
```python
python -m unittest tests/test_simulation.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.