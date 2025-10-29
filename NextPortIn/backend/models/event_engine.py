import simpy
from typing import Dict, List
from models.supply_chain import SupplyChainNetwork, Shipment

class EventEngine:
    def __init__(self, network: SupplyChainNetwork):
        self.env = simpy.Environment()
        self.network = network
        self.current_time = 0
        self.active_processes: Dict[str, simpy.Process] = {}

    def run(self, steps: int = 1):
        """Run the simulation for a specified number of time steps"""
        target_time = self.current_time + steps
        
        # Create processes for active shipments
        for shipment in self.network.shipments.values():
            if (shipment.status == 'in_transit' and 
                shipment.id not in self.active_processes):
                self.active_processes[shipment.id] = self.env.process(
                    self._simulate_shipment(shipment))

        # Run simulation until target time
        self.env.run(until=target_time)
        self.current_time = target_time
        
        # Update network state
        self._update_network_state()

    def _simulate_shipment(self, shipment: Shipment):
        """Simulate the movement of a shipment through the network"""
        route = shipment.route
        current_edge_idx = 0

        while current_edge_idx < len(route):
            edge_id = route[current_edge_idx]
            edge = self.network.edges[edge_id]
            
            # Calculate travel time including current delays
            travel_time = edge.base_time + edge.current_delay
            
            # Wait for travel time
            yield self.env.timeout(travel_time)
            
            # Update shipment position
            if current_edge_idx < len(route) - 1:
                next_edge = self.network.edges[route[current_edge_idx + 1]]
                shipment.current_position = self.network.nodes[next_edge.source].location
            else:
                # Final destination reached
                shipment.current_position = self.network.nodes[edge.target].location
                shipment.status = 'delivered'
                
            current_edge_idx += 1

    def _update_network_state(self):
        """Update the state of the network based on current simulation time"""
        # Update node disruptions
        for node in self.network.nodes.values():
            if (node.status == 'disrupted' and 
                node.disruption_end_time is not None and 
                node.disruption_end_time <= self.current_time):
                node.status = 'operational'
                node.disruption_end_time = None

        # Update edge disruptions
        for edge in self.network.edges.values():
            if (edge.status == 'disrupted' and 
                edge.disruption_end_time is not None and 
                edge.disruption_end_time <= self.current_time):
                edge.status = 'operational'
                edge.current_delay = 0
                edge.disruption_end_time = None

        # Clean up completed processes
        completed_shipments = [
            ship_id for ship_id, proc in self.active_processes.items()
            if proc.triggered
        ]
        for ship_id in completed_shipments:
            del self.active_processes[ship_id]