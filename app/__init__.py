import os
from flask import Flask
from database.db_config import init_db, seed_database


def create_app(test_config=None):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "abc-hospitals-development-key"),
        DATABASE=os.path.join(app.instance_path, "abc_hospitals.sqlite3"),
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    init_db(app.config["DATABASE"])
    seed_database(app.config["DATABASE"])

    from app.routes import bp
    app.register_blueprint(bp)
    return app
