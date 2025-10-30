from app import create_app, db
from app.models.models import User, Stock, Vehicle, Transport, TransportItem

app = create_app()

# Create an application context
with app.app_context():
    # Create all tables
    db.create_all()

    # Check if we need to create initial data
    if User.query.first() is None:
        # Create sample manager
        manager = User(username='manager', email='manager@example.com', role='manager')
        manager.set_password('manager123')
        db.session.add(manager)

        # Create sample workers
        worker1 = User(username='worker1', email='worker1@example.com', role='worker')
        worker1.set_password('worker123')
        db.session.add(worker1)

        worker2 = User(username='worker2', email='worker2@example.com', role='worker')
        worker2.set_password('worker123')
        db.session.add(worker2)

        # Create sample stocks
        stocks = [
            Stock(item_name='Electronics', quantity=100, unit='pieces', location='Warehouse A'),
            Stock(item_name='Furniture', quantity=50, unit='sets', location='Warehouse B'),
            Stock(item_name='Food Items', quantity=1000, unit='kg', location='Warehouse C')
        ]
        db.session.add_all(stocks)

        # Create sample vehicles
        vehicles = [
            Vehicle(vehicle_number='TRK001', vehicle_type='Truck', capacity=1000, status='available'),
            Vehicle(vehicle_number='VAN001', vehicle_type='Van', capacity=500, status='available')
        ]
        db.session.add_all(vehicles)

        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Using port 5001 instead of default 5000