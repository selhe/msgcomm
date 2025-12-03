from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)

    # MySQL RDS connection
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://admin:adminMsgComm@msgcommdb.cbci680aq1tu.us-east-2.rds.amazonaws.com:3306/msgcomm"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    # Import models first
    from . import models

    # Register routes AFTER CORS + db
    from .routes import bp
    app.register_blueprint(bp)

    from . import socket_events

    return app
