from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid

@dataclass
class Node:
    id: str
    type: str  # 'factory', 'warehouse', 'port'
    location: Dict[str, float]  # {'lat': float, 'lng': float}
    capacity: float
    current_inventory: float = 0
    status: str = 'operational'
    disruption_end_time: Optional[float] = None

@dataclass
class Edge:
    id: str
    source: str
    target: str
    transport_type: str  # 'road', 'sea', 'air'
    base_time: float
    base_cost: float
    current_delay: float = 0
    status: str = 'operational'
    disruption_end_time: Optional[float] = None

@dataclass
class Shipment:
    id: str
    origin: str
    destination: str
    route: List[str]  # List of edge IDs
    quantity: float
    start_time: float
    estimated_arrival: float
    current_position: Dict[str, float]  # {'lat': float, 'lng': float}
    status: str = 'in_transit'

class SupplyChainNetwork:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.shipments: Dict[str, Shipment] = {}
        self._load_initial_data()

    def _load_initial_data(self):
        # Mock data for demonstration
        # Add 3 factories
        self.add_node('F1', 'factory', {'lat': 40.7128, 'lng': -74.0060}, 1000)
        self.add_node('F2', 'factory', {'lat': 34.0522, 'lng': -118.2437}, 1500)
        self.add_node('F3', 'factory', {'lat': 41.8781, 'lng': -87.6298}, 1200)

        # Add 2 warehouses
        self.add_node('W1', 'warehouse', {'lat': 39.9526, 'lng': -75.1652}, 2000)
        self.add_node('W2', 'warehouse', {'lat': 29.7604, 'lng': -95.3698}, 2500)

        # Add routes
        self.add_edge('F1', 'W1', 'road', 24, 1000)
        self.add_edge('F2', 'W2', 'road', 36, 1500)
        self.add_edge('F3', 'W1', 'road', 18, 800)
        self.add_edge('F1', 'W2', 'road', 48, 2000)
        self.add_edge('F2', 'W1', 'air', 6, 5000)

    def add_node(self, id: str, type: str, location: Dict[str, float], capacity: float):
        self.nodes[id] = Node(id=id, type=type, location=location, capacity=capacity)

    def add_edge(self, source: str, target: str, transport_type: str, base_time: float, base_cost: float):
        edge_id = f"{source}-{target}"
        self.edges[edge_id] = Edge(
            id=edge_id,
            source=source,
            target=target,
            transport_type=transport_type,
            base_time=base_time,
            base_cost=base_cost
        )

    def create_shipment(self, origin: str, destination: str, quantity: float, start_time: float) -> str:
        shipment_id = str(uuid.uuid4())
        route = self._calculate_route(origin, destination)
        eta = self._calculate_eta(route, start_time)
        
        self.shipments[shipment_id] = Shipment(
            id=shipment_id,
            origin=origin,
            destination=destination,
            route=route,
            quantity=quantity,
            start_time=start_time,
            estimated_arrival=eta,
            current_position=self.nodes[origin].location.copy()
        )
        return shipment_id

    def disrupt_node(self, node_id: str, duration: float, severity: float = 1.0):
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.status = 'disrupted'
            node.disruption_end_time = duration
            # Update affected shipments
            self._update_affected_shipments()

    def disrupt_edge(self, edge_id: str, duration: float, severity: float = 1.0):
        if edge_id in self.edges:
            edge = self.edges[edge_id]
            edge.status = 'disrupted'
            edge.current_delay = edge.base_time * severity
            edge.disruption_end_time = duration
            # Update affected shipments
            self._update_affected_shipments()

    def apply_rerouting(self, origin: str, destination: str, new_route: List[str]) -> bool:
        # Validate new route
        if not self._validate_route(new_route):
            return False
        
        # Update affected shipments with new route
        for shipment in self.shipments.values():
            if (shipment.origin == origin and 
                shipment.destination == destination and 
                shipment.status == 'in_transit'):
                shipment.route = new_route
                shipment.estimated_arrival = self._calculate_eta(new_route, shipment.start_time)
        
        return True

    def activate_alternate_supplier(self, original_supplier: str, alternate_supplier: str) -> bool:
        if alternate_supplier not in self.nodes or self.nodes[alternate_supplier].type != 'factory':
            return False
        
        # Update shipments to use alternate supplier
        for shipment in self.shipments.values():
            if shipment.origin == original_supplier and shipment.status == 'planned':
                shipment.origin = alternate_supplier
                shipment.route = self._calculate_route(alternate_supplier, shipment.destination)
                shipment.estimated_arrival = self._calculate_eta(shipment.route, shipment.start_time)
        
        return True

    def get_nodes(self) -> List[Dict]:
        return [self._node_to_dict(node) for node in self.nodes.values()]

    def get_edges(self) -> List[Dict]:
        return [self._edge_to_dict(edge) for edge in self.edges.values()]

    def get_active_shipments(self) -> List[Dict]:
        return [self._shipment_to_dict(shipment) 
                for shipment in self.shipments.values() 
                if shipment.status == 'in_transit']

    def get_metrics(self) -> Dict:
        total_delay = sum(s.estimated_arrival - s.start_time 
                         for s in self.shipments.values())
        total_cost = sum(self._calculate_shipment_cost(s) 
                        for s in self.shipments.values())
        return {
            'total_delay': total_delay,
            'total_cost': total_cost,
            'active_shipments': len([s for s in self.shipments.values() 
                                   if s.status == 'in_transit']),
            'disrupted_nodes': len([n for n in self.nodes.values() 
                                  if n.status == 'disrupted']),
            'disrupted_edges': len([e for e in self.edges.values() 
                                  if e.status == 'disrupted'])
        }

    def calculate_disruption_impact(self) -> Dict:
        pre_disruption_metrics = self.get_metrics()
        affected_shipments = len([s for s in self.shipments.values() 
                                if s.status != 'delivered'])
        return {
            'affected_shipments': affected_shipments,
            'delay_impact': pre_disruption_metrics['total_delay'],
            'cost_impact': pre_disruption_metrics['total_cost']
        }

    def _calculate_route(self, origin: str, destination: str) -> List[str]:
        # Simple direct route for demonstration
        return [f"{origin}-{destination}"]

    def _calculate_eta(self, route: List[str], start_time: float) -> float:
        total_time = start_time
        for edge_id in route:
            if edge_id in self.edges:
                edge = self.edges[edge_id]
                total_time += edge.base_time + edge.current_delay
        return total_time

    def _calculate_shipment_cost(self, shipment: Shipment) -> float:
        total_cost = 0
        for edge_id in shipment.route:
            if edge_id in self.edges:
                total_cost += self.edges[edge_id].base_cost
        return total_cost

    def _update_affected_shipments(self):
        for shipment in self.shipments.values():
            if shipment.status == 'in_transit':
                shipment.estimated_arrival = self._calculate_eta(
                    shipment.route, shipment.start_time)

    def _validate_route(self, route: List[str]) -> bool:
        return all(edge_id in self.edges for edge_id in route)

    def _node_to_dict(self, node: Node) -> Dict:
        return {
            'id': node.id,
            'type': node.type,
            'location': node.location,
            'status': node.status,
            'inventory': node.current_inventory
        }

    def _edge_to_dict(self, edge: Edge) -> Dict:
        return {
            'id': edge.id,
            'source': edge.source,
            'target': edge.target,
            'type': edge.transport_type,
            'status': edge.status,
            'delay': edge.current_delay
        }

    def _shipment_to_dict(self, shipment: Shipment) -> Dict:
        return {
            'id': shipment.id,
            'origin': shipment.origin,
            'destination': shipment.destination,
            'status': shipment.status,
            'position': shipment.current_position,
            'eta': shipment.estimated_arrival
        }