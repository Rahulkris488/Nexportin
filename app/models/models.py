from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'manager' or 'worker'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20))
    location = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50))
    capacity = db.Column(db.Float)
    status = db.Column(db.String(20))  # 'available', 'in-transit', 'maintenance'
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    driver = db.relationship('User', backref='assigned_vehicle')

class Transport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20))  # 'pending', 'in-transit', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    vehicle = db.relationship('Vehicle', backref='transports')
    worker = db.relationship('User', backref='assigned_transports')

class TransportItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transport_id = db.Column(db.Integer, db.ForeignKey('transport.id'))
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))
    quantity = db.Column(db.Integer, nullable=False)

    transport = db.relationship('Transport', backref='items')
    stock = db.relationship('Stock', backref='transport_items')