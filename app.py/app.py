# app.py

import os
from flask import Flask, render_template, request, url_for, jsonify, redirect, flash
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from celery.result import AsyncResult
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import base64

db = SQLAlchemy()
login_manager = LoginManager()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(100), unique=True, nullable=False)
    rating = db.Column(db.String(50), nullable=False)
    bias = db.Column(db.String(50), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        sources_to_add = [
            {'domain': 'reuters.com', 'rating': 'Generally Reliable', 'bias': 'Center'},
            {'domain': 'apnews.com', 'rating': 'Generally Reliable', 'bias': 'Center'},
            {'domain': 'bbc.com', 'rating': 'Generally Reliable', 'bias': 'Center'},
            {'domain': 'thehindu.com', 'rating': 'Generally Reliable', 'bias': 'Center'},
            {'domain': 'indianexpress.com', 'rating': 'Generally Reliable', 'bias': 'Center'},
            {'domain': 'theonion.com', 'rating': 'Satire', 'bias': 'N/A'}
        ]
        for s in sources_to_add:
            if not Source.query.filter_by(domain=s['domain']).first():
                db.session.add(Source(**s))
        db.session.commit()
        print("Initialized and populated the database.")

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username, password = request.form.get('username'), request.form.get('password')
            if User.query.filter_by(username=username).first():
                flash('Username already exists.')
                return redirect(url_for('signup'))
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('signup.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username, password = request.form.get('username'), request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                flash('Please check your login details and try again.')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    @app.route('/analyze', methods=['POST'])
    @login_required
    def analyze():
        from tasks import run_analysis
        task = run_analysis.delay(request.form.get('url'))
        return jsonify({'task_id': task.id, 'status_url': url_for('task_status', task_id=task.id)})

    @app.route('/status/<task_id>')
    @login_required
    def task_status(task_id):
        from celery_worker import celery_app
        task = celery_app.AsyncResult(task_id)
        response = {'state': task.state}
        if task.state == 'SUCCESS': response['result'] = task.result
        elif task.state == 'FAILURE': response['result'] = 'Task failed.'
        return jsonify(response)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
