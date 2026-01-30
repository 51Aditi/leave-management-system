from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, LeaveRequest
from config import Config
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create database and default users
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='manager').first():
        manager = User(username='manager', email='manager@company.com', role='manager')
        manager.set_password('manager123')
        db.session.add(manager)
        db.session.commit()
    if not User.query.filter_by(username='emp1').first():
        emp = User(username='emp1', email='emp1@company.com', role='employee')
        emp.set_password('emp123')
        db.session.add(emp)
        db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    leave_counts = {
        'pending': LeaveRequest.query.filter_by(user_id=current_user.id, status='pending', cancelled=False).count(),
        'approved': LeaveRequest.query.filter_by(user_id=current_user.id, status='approved').count(),
        'rejected': LeaveRequest.query.filter_by(user_id=current_user.id, status='rejected').count()
    }
    return render_template('dashboard.html', leave_counts=leave_counts)

@app.route('/apply_leave', methods=['GET', 'POST'])
@login_required
def apply_leave():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        leave_type = request.form['leave_type']
        reason = request.form['reason']
        
        if start_date < date.today():
            flash('Cannot apply for past dates', 'error')
            return render_template('apply_leave.html')
        
        days = (end_date - start_date).days + 1
        balance = getattr(current_user, f"{leave_type}_leave")
        if days > balance:
            flash('Not enough leave balance', 'error')
            return render_template('apply_leave.html')
        
        last_id = db.session.query(db.func.max(LeaveRequest.id)).scalar()
        new_id_num = 1 if not last_id else int(last_id[1:]) + 1
        leave_id = f"L{new_id_num:03d}"
        
        leave = LeaveRequest(id=leave_id, user_id=current_user.id, start_date=start_date,
                           end_date=end_date, leave_type=leave_type, reason=reason)
        db.session.add(leave)
        db.session.commit()
        flash(f'Leave {leave_id} applied successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('apply_leave.html')

@app.route('/manager')
@login_required
def manager_dashboard():
    if current_user.role != 'manager':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    pending_leaves = LeaveRequest.query.filter_by(status='pending', cancelled=False).order_by(LeaveRequest.created_at.desc()).all()
    return render_template('manager.html', pending_leaves=pending_leaves)

@app.route('/approve/<leave_id>', methods=['POST'])
@login_required
def approve_leave(leave_id):
    if current_user.role != 'manager':
        return jsonify({'error': 'Access denied'}), 403
    
    leave = LeaveRequest.query.get_or_404(leave_id)
    if leave.status != 'pending':
        return jsonify({'error': 'Already processed'}), 400
    
    leave.status = 'approved'
    user = User.query.get(leave.user_id)
    days = (leave.end_date - leave.start_date).days + 1
    setattr(user, f"{leave.leave_type}_leave", getattr(user, f"{leave.leave_type}_leave") - days)
    db.session.commit()
    flash('Leave approved successfully!', 'success')
    return jsonify({'success': True})

@app.route('/reject/<leave_id>', methods=['POST'])
@login_required
def reject_leave(leave_id):
    if current_user.role != 'manager':
        return jsonify({'error': 'Access denied'}), 403
    
    leave = LeaveRequest.query.get_or_404(leave_id)
    leave.status = 'rejected'
    db.session.commit()
    flash('Leave rejected!', 'success')
    return jsonify({'success': True})\
    
@app.route('/history')
@login_required
def leave_history():
    leaves = LeaveRequest.query.filter_by(user_id=current_user.id)\
        .filter_by(cancelled=False)\
        .order_by(LeaveRequest.created_at.desc()).all()
    return render_template('history.html', leaves=leaves)

@app.route('/reset', methods=['POST'])
@login_required
def reset_database():
    if current_user.username != 'manager':
        flash('Only manager can reset!', 'error')
        return redirect(url_for('dashboard'))
    
    # Delete all leaves only (keep users)
    LeaveRequest.query.delete()
    db.session.commit()
    
    # Reset all leave balances
    for user in User.query.all():
        user.casual_leave = 10
        user.sick_leave = 8
        user.paid_leave = 12
        db.session.commit()
    
    flash('✅ Database RESET! All balances restored!', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
