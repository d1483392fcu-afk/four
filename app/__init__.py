import os
import sqlite3
from flask import Flask, g, redirect, url_for
from dotenv import load_dotenv


def init_db():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'database.db')
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'schema.sql')

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()

    conn = sqlite3.connect(db_path)
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print('Database initialized successfully.')


def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')
    app.config['DATABASE'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'database.db')

    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
    if not os.path.exists(app.config['DATABASE']):
        init_db()

    from app.routes.auth import bp as auth_bp
    from app.routes.ledger import bp as ledger_bp
    from app.routes.report import bp as report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(ledger_bp)
    app.register_blueprint(report_bp)

    @app.route('/')
    def home():
        if getattr(g, 'user', None):
            return redirect(url_for('ledger.index'))
        return redirect(url_for('auth.login'))

    return app
