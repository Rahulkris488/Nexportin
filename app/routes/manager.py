from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.models import Stock, Vehicle, Transport, TransportItem, User
from app import db
from functools import wraps

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'manager':
            flash('Access denied. Manager privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@manager_bp.route('/dashboard')
@login_required
@manager_required
def dashboard():
    stocks = Stock.query.all()
    vehicles = Vehicle.query.all()
    active_transports = Transport.query.filter_by(status='in-transit').all()
    workers = User.query.filter_by(role='worker').all()
    
    return render_template('manager/dashboard.html',
                         stocks=stocks,
                         vehicles=vehicles,
                         active_transports=active_transports,
                         workers=workers)

@manager_bp.route('/stocks')
@login_required
@manager_required
def stocks():
    stocks = Stock.query.all()
    return render_template('manager/stocks.html', stocks=stocks)

@manager_bp.route('/vehicles')
@login_required
@manager_required
def vehicles():
    vehicles = Vehicle.query.all()
    drivers = User.query.filter_by(role='worker').all()
    return render_template('manager/vehicles.html', vehicles=vehicles, drivers=drivers)

@manager_bp.route('/transports')
@login_required
@manager_required
def transports():
    transports = Transport.query.all()
    return render_template('manager/transports.html', transports=transports)

@manager_bp.route('/transport/<int:id>')
@login_required
@manager_required
def transport_details(id):
    transport = Transport.query.get_or_404(id)
    return render_template('manager/transport_details.html', transport=transport)

@manager_bp.route('/transport/<int:id>/update_status/<status>', methods=['POST'])
@login_required
@manager_required
def update_transport_status(id, status):
    transport = Transport.query.get_or_404(id)
    if status == 'cancelled' and transport.status == 'pending':
        transport.status = 'cancelled'
        transport.vehicle.status = 'available'
        db.session.commit()
        flash('Transport has been cancelled.', 'success')
    return redirect(url_for('manager.dashboard'))

@manager_bp.route('/create_transport', methods=['GET', 'POST'])
@login_required
@manager_required
def create_transport():
    if request.method == 'POST':
        # Get basic transport info
        source = request.form.get('source')
        destination = request.form.get('destination')
        vehicle_id = request.form.get('vehicle_id')
        worker_id = request.form.get('worker_id')
        
        # Validate vehicle availability
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle or vehicle.status != 'available':
            flash('Selected vehicle is not available.', 'error')
            return redirect(url_for('manager.create_transport'))
        
        # Validate worker availability
        worker = User.query.get(worker_id)
        if not worker or worker.role != 'worker':
            flash('Invalid worker selected.', 'error')
            return redirect(url_for('manager.create_transport'))
        
        # Check if worker is already assigned to an active transport
        active_transport = Transport.query.filter_by(
            worker_id=worker_id,
            status='in-transit'
        ).first()
        if active_transport:
            flash('Selected worker is already assigned to an active transport.', 'error')
            return redirect(url_for('manager.create_transport'))
        
        # Create new transport
        transport = Transport(
            source=source,
            destination=destination,
            vehicle_id=vehicle_id,
            worker_id=worker_id,
            status='pending'
        )
        db.session.add(transport)
        
        # Process transport items
        total_weight = 0
        items_data = []
        
        # Get all items from the form
        for key in request.form:
            if key.startswith('items[') and key.endswith('[stock_id]'):
                index = key[6:-10]  # Extract index from 'items[0][stock_id]'
                stock_id = request.form.get(f'items[{index}][stock_id]')
                quantity = request.form.get(f'items[{index}][quantity]')
                
                if stock_id and quantity:
                    items_data.append({
                        'stock_id': int(stock_id),
                        'quantity': int(quantity)
                    })
        
        # Validate and create transport items
        for item_data in items_data:
            stock = Stock.query.get(item_data['stock_id'])
            if not stock:
                db.session.rollback()
                flash(f'Invalid stock item selected.', 'error')
                return redirect(url_for('manager.create_transport'))
            
            if stock.quantity < item_data['quantity']:
                db.session.rollback()
                flash(f'Insufficient quantity for {stock.item_name}.', 'error')
                return redirect(url_for('manager.create_transport'))
            
            # Create transport item
            transport_item = TransportItem(
                transport=transport,
                stock_id=item_data['stock_id'],
                quantity=item_data['quantity']
            )
            db.session.add(transport_item)
            
            # Update stock quantity
            stock.quantity -= item_data['quantity']
        
        # Update vehicle status
        vehicle.status = 'in-transit'
        
        try:
            db.session.commit()
            flash('Transport created successfully!', 'success')
            return redirect(url_for('manager.transports'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the transport.', 'error')
            return redirect(url_for('manager.create_transport'))
    
    # GET request - show form
    vehicles = Vehicle.query.filter_by(status='available').all()
    workers = User.query.filter_by(role='worker').all()
    available_workers = [w for w in workers if not any(
        t.status == 'in-transit' for t in w.assigned_transports
    )]
    stocks = Stock.query.filter(Stock.quantity > 0).all()
    
    return render_template('manager/create_transport.html',
                         vehicles=vehicles,
                         workers=available_workers,
                         stocks=stocks)