# Import necessary modules
from importlib import import_module
import threading
import time
from app.model.ip_kapal import IpKapal
from flask import send_from_directory

from flask_cors import CORS

# Import extensions and resources from the current package
from .extensions import api, db, jwt, mail, socketio, app, scheduler
from .resources import ns, telnet_worker

# Import standard libraries and third-party packages
import os
from datetime import timedelta
from dotenv import load_dotenv

checked_configs = {}

# Dynamically import all modules in the "model" folder
def import_all_modules():
    model_folder = os.path.join(os.path.dirname(__file__), "model")

    for file in os.listdir(model_folder):
        if file.endswith(".py") and file != "__init__.py":
            # Get module name without file extension
            module_name = file[:-3]
            # Import the module dynamically
            module = import_module(f"app.model.{module_name}")
            # Make the module accessible globally
            globals()[module_name] = module


# Create a Flask application
def create_app():
    # Load environment variables from a .env file
    load_dotenv()

    # Configure the Flask app with database and JWT settings
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"{os.getenv('DB_CONNECTION')}+mysqlconnector://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_DATABASE')}"
    app.config["DEBUG"] = os.getenv("DEBUG")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_KEY")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        seconds=int(os.getenv("JWT_EXPIRE_TOKEN", 4800))
    )
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
    app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL")
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
    app.config["MAIL_DEBUG"] = os.getenv("MAIL_DEBUG")

    # Initialize Flask extensions
    api.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    CORS(app, origins="*")
    scheduler.start()

    # Add Flask-RESTful namespace
    api.add_namespace(ns)

    # Dynamically import all modules in the "model" folder
    import_all_modules()
    
    # Accessing File
    @app.route('/assets/<path:folder>/<path:filename>')
    def serve_assets(folder, filename):
        # Construct the path to the asset directory
        asset_dir = os.path.join(app.root_path, 'assets', folder)

        # Return the requested file from the asset directory
        return send_from_directory(asset_dir, filename)

    # Create database tables within the app context
    with app.app_context():
        db.create_all()

    return app  # Return the configured Flask app


# Variable to store checked status
def check_for_new_configurations():
    with app.app_context():
        while True:
            print(len(checked_configs))
            # Fetch IP and port from the database
            new_configs = db.session.query(IpKapal).all()

            # Check for new configurations
            for config in new_configs:
                if (config.ip, config.port) not in checked_configs:
                    # Start telnet connection for new configuration in a separate thread
                    telnet_thread = threading.Thread(
                        target=telnet_worker, args=(config.ip, config.port,config.call_sign,str(config.type_ip))
                    )
                    telnet_thread.start()
                    # Mark the configuration as checked
                    checked_configs[(config.ip, config.port)] = True

                    # Stop telnet readers for configurations that are no longer in the database
            for ip, port in list(checked_configs.keys()):
                if (ip, port) not in [
                    (config.ip, config.port) for config in new_configs
                ]:
                    telnet_thread = checked_configs.pop((ip, port))
                    telnet_thread.join()

            # Sleep for some time before checking again
            time.sleep(60)  # Adjust as needed
