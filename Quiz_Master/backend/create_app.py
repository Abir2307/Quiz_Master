from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Use PostgreSQL on Render, SQLite locally
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Some platforms use postgres:// instead of postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://",
                "postgresql://",
                1
            )

        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, "instance", "QuizMaster.sqlite3")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.getenv("SECRET_KEY", "secret_key")

    # Redis
    app.config["broker_url"] = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    app.config["result_backend"] = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    # Session
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["SESSION_COOKIE_HTTPONLY"] = True

    Session(app)
    db.init_app(app)

    CORS(
        app,
        supports_credentials=True,
        origins=[
            "https://quiz-master-13ip-hum1zgfrs-abir-sahas-projects-5fb2fcc3.vercel.app",
            "https://quiz-master-13ip-ehyj765p6-abir-sahas-projects-5fb2fcc3.vercel.app",
            "https://quiz-master-13ip-three.vercel.app/",
            "https://quiz-maestro-two.vercel.app/"
        ]
    )

    return app
