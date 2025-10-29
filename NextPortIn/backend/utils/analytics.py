from typing import Dict, Any
from models.supply_chain import SupplyChainNetwork

def calculate_recovery_impact(
    network: SupplyChainNetwork,
    strategy_type: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate the impact of applying a recovery strategy"""
    pre_recovery_metrics = network.get_metrics()
    
    impact = {
        'cost_savings': 0,
        'time_savings': 0,
        'affected_shipments': 0
    }
    
    if strategy_type == 'reroute':
        # Calculate impact of rerouting
        original_route = _get_original_route(
            network, params['origin'], params['destination'])
        new_route = params['new_route']
        
        original_cost = _calculate_route_cost(network, original_route)
        new_cost = _calculate_route_cost(network, new_route)
        impact['cost_savings'] = original_cost - new_cost
        
        original_time = _calculate_route_time(network, original_route)
        new_time = _calculate_route_time(network, new_route)
        impact['time_savings'] = original_time - new_time
        
    elif strategy_type == 'alternate_supplier':
        # Calculate impact of using alternate supplier
        original_supplier = params['original']
        alternate_supplier = params['alternate']
        
        impact['affected_shipments'] = len([
            s for s in network.shipments.values()
            if s.origin == original_supplier and s.status != 'delivered'
        ])
        
        # Estimate cost difference of using alternate supplier
        impact['cost_savings'] = _estimate_supplier_cost_difference(
            network, original_supplier, alternate_supplier)
    
    return impact

def _get_original_route(
    network: SupplyChainNetwork,
    origin: str,
    destination: str
) -> str:
    """Get the original route between two nodes"""
    return f"{origin}-{destination}"

def _calculate_route_cost(
    network: SupplyChainNetwork,
    route: str
) -> float:
    """Calculate the total cost of a route"""
    if route in network.edges:
        return network.edges[route].base_cost
    return 0

def _calculate_route_time(
    network: SupplyChainNetwork,
    route: str
) -> float:
    """Calculate the total time of a route"""
    if route in network.edges:
        edge = network.edges[route]
        return edge.base_time + edge.current_delay
    return 0

def _estimate_supplier_cost_difference(
    network: SupplyChainNetwork,
    original_supplier: str,
    alternate_supplier: str
) -> float:
    """Estimate the cost difference between two suppliers"""
    # This is a simplified calculation
    original_routes = [
        edge for edge in network.edges.values()
        if edge.source == original_supplier
    ]
    alternate_routes = [
        edge for edge in network.edges.values()
        if edge.source == alternate_supplier
    ]
    
    avg_original_cost = (
        sum(route.base_cost for route in original_routes) / 
        len(original_routes) if original_routes else 0
    )
    avg_alternate_cost = (
        sum(route.base_cost for route in alternate_routes) / 
        len(alternate_routes) if alternate_routes else 0
    )
    
    return avg_original_cost - avg_alternate_cost