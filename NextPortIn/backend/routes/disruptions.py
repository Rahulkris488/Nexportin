from flask import Blueprint, jsonify, request
from models.supply_chain import SupplyChainNetwork

disruptions_bp = Blueprint('disruptions', __name__)
network = SupplyChainNetwork()

@disruptions_bp.route('/disrupt', methods=['POST'])
def inject_disruption():
    """Inject a disruption into the supply chain network"""
    data = request.json
    disruption_type = data.get('type')
    target_id = data.get('target_id')
    duration = data.get('duration')
    severity = data.get('severity', 1.0)

    if disruption_type == 'node':
        network.disrupt_node(target_id, duration, severity)
    elif disruption_type == 'edge':
        network.disrupt_edge(target_id, duration, severity)
    else:
        return jsonify({'error': 'Invalid disruption type'}), 400

    return jsonify({
        'status': 'success',
        'disruption': {
            'type': disruption_type,
            'target': target_id,
            'duration': duration,
            'impact': network.calculate_disruption_impact()
        }
    })