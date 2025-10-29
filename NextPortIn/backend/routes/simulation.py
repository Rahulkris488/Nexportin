from flask import Blueprint, jsonify, request
from models.supply_chain import SupplyChainNetwork
from models.event_engine import EventEngine

simulation_bp = Blueprint('simulation', __name__)
network = SupplyChainNetwork()
event_engine = EventEngine(network)

@simulation_bp.route('/map', methods=['GET'])
def get_supply_chain_map():
    """Return the current state of the supply chain network"""
    return jsonify({
        'nodes': network.get_nodes(),
        'edges': network.get_edges(),
        'shipments': network.get_active_shipments()
    })

@simulation_bp.route('/simulate', methods=['POST'])
def run_simulation():
    """Run simulation for specified time steps"""
    steps = request.json.get('steps', 1)
    event_engine.run(steps)
    return jsonify({
        'status': 'success',
        'current_time': event_engine.current_time,
        'metrics': network.get_metrics()
    })