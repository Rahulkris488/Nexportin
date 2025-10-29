from flask import Blueprint, jsonify, request
from models.supply_chain import SupplyChainNetwork
from utils.analytics import calculate_recovery_impact

recovery_bp = Blueprint('recovery', __name__)
network = SupplyChainNetwork()

@recovery_bp.route('/recover', methods=['POST'])
def apply_recovery_strategy():
    """Apply a recovery strategy to mitigate disruption effects"""
    data = request.json
    strategy_type = data.get('type')
    params = data.get('parameters', {})

    if strategy_type == 'reroute':
        success = network.apply_rerouting(
            origin=params.get('origin'),
            destination=params.get('destination'),
            new_route=params.get('new_route')
        )
    elif strategy_type == 'alternate_supplier':
        success = network.activate_alternate_supplier(
            original_supplier=params.get('original'),
            alternate_supplier=params.get('alternate')
        )
    else:
        return jsonify({'error': 'Invalid recovery strategy'}), 400

    if success:
        impact = calculate_recovery_impact(network, strategy_type, params)
        return jsonify({
            'status': 'success',
            'strategy': strategy_type,
            'impact': impact
        })
    else:
        return jsonify({'error': 'Recovery strategy application failed'}), 400