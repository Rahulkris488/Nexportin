import json
from typing import Dict, Any
from pathlib import Path

def load_initial_data() -> Dict[str, Any]:
    """Load initial supply chain network data from JSON file"""
    data_file = Path(__file__).parent.parent / 'data' / 'initial_network.json'
    
    # If file doesn't exist, return default mock data
    if not data_file.exists():
        return {
            'nodes': [
                {
                    'id': 'F1',
                    'type': 'factory',
                    'location': {'lat': 40.7128, 'lng': -74.0060},
                    'capacity': 1000
                },
                {
                    'id': 'F2',
                    'type': 'factory',
                    'location': {'lat': 34.0522, 'lng': -118.2437},
                    'capacity': 1500
                },
                {
                    'id': 'F3',
                    'type': 'factory',
                    'location': {'lat': 41.8781, 'lng': -87.6298},
                    'capacity': 1200
                },
                {
                    'id': 'W1',
                    'type': 'warehouse',
                    'location': {'lat': 39.9526, 'lng': -75.1652},
                    'capacity': 2000
                },
                {
                    'id': 'W2',
                    'type': 'warehouse',
                    'location': {'lat': 29.7604, 'lng': -95.3698},
                    'capacity': 2500
                }
            ],
            'edges': [
                {
                    'id': 'F1-W1',
                    'source': 'F1',
                    'target': 'W1',
                    'transport_type': 'road',
                    'base_time': 24,
                    'base_cost': 1000
                },
                {
                    'id': 'F2-W2',
                    'source': 'F2',
                    'target': 'W2',
                    'transport_type': 'road',
                    'base_time': 36,
                    'base_cost': 1500
                },
                {
                    'id': 'F3-W1',
                    'source': 'F3',
                    'target': 'W1',
                    'transport_type': 'road',
                    'base_time': 18,
                    'base_cost': 800
                },
                {
                    'id': 'F1-W2',
                    'source': 'F1',
                    'target': 'W2',
                    'transport_type': 'road',
                    'base_time': 48,
                    'base_cost': 2000
                },
                {
                    'id': 'F2-W1',
                    'source': 'F2',
                    'target': 'W1',
                    'transport_type': 'air',
                    'base_time': 6,
                    'base_cost': 5000
                }
            ]
        }
    
    with open(data_file, 'r') as f:
        return json.load(f)