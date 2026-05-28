from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets


import os

# Render requires this
port = int(os.environ.get("PORT", 5000))


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///hecg.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ── Models ──────────────────────────────────────────────────────────────────

class ContactMessage(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(100), nullable=False)
    email     = db.Column(db.String(120), nullable=False)
    service   = db.Column(db.String(100))
    message   = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ── Helpers ──────────────────────────────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# ── Public Routes ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        msg = ContactMessage(
            name    = request.form.get('name', '').strip(),
            email   = request.form.get('email', '').strip(),
            service = request.form.get('service', '').strip(),
            message = request.form.get('message', '').strip(),
        )
        db.session.add(msg)
        db.session.commit()
        flash('Message sent! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# ── Admin Routes ─────────────────────────────────────────────────────────────

@app.route('/admin')
@login_required
def admin():
    messages = ContactMessage.query.order_by(ContactMessage.timestamp.desc()).all()
    return render_template('admin.html', messages=messages)

@app.route('/admin/delete/<int:msg_id>', methods=['POST'])
@login_required
def delete_message(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.', 'success')
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Change these credentials to something private!
        if request.form['username'] == 'admin' and request.form['password'] == 'hecg2024':
            session['admin'] = True
            return redirect(url_for('admin'))
        flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

# ── Init & Run ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=port)