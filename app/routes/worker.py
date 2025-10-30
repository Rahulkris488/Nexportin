from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.models import Transport, TransportItem
from app import db
from functools import wraps
from datetime import datetime

worker_bp = Blueprint('worker', __name__, url_prefix='/worker')

def worker_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'worker':
            flash('Access denied. Worker privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@worker_bp.route('/dashboard')
@login_required
@worker_required
def dashboard():
    assigned_transports = Transport.query.filter_by(
        worker_id=current_user.id
    ).order_by(Transport.created_at.desc()).all()
    
    return render_template('worker/dashboard.html', 
                         transports=assigned_transports)

@worker_bp.route('/transport/<int:id>/update_status/<status>')
@login_required
@worker_required
def update_transport_status(id, status):
    transport = Transport.query.get_or_404(id)
    
    if transport.worker_id != current_user.id:
        flash('You are not authorized to update this transport.', 'error')
        return redirect(url_for('worker.dashboard'))
    
    if status == 'completed':
        transport.completed_at = datetime.utcnow()
    
    transport.status = status
    db.session.commit()
    flash('Transport status updated successfully!', 'success')
    return redirect(url_for('worker.dashboard'))

@worker_bp.route('/transport/<int:id>/details')
@login_required
@worker_required
def transport_details(id):
    transport = Transport.query.get_or_404(id)
    
    if transport.worker_id != current_user.id:
        flash('You are not authorized to view this transport.', 'error')
        return redirect(url_for('worker.dashboard'))
    
    return render_template('worker/transport_details.html', transport=transport)