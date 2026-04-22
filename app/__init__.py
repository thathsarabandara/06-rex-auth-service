import logging
import time
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from app.config import Config
from app.extensions import db, jwt, limiter, migrate
from app.routes.auth import auth_bp
from app.routes.health import health_bp

logger = logging.getLogger(__name__)


class CustomFlask(Flask):
    """Custom Flask app that handles form data properly."""

    def make_default_options_response(self):
        """Handle OPTIONS requests."""
        return super().make_default_options_response()


def create_app(config_overrides=None) -> Flask:
    template_dir = Path(__file__).parent / "templates"
    app = CustomFlask(__name__, template_folder=str(template_dir))
    app.config.from_object(Config)

    # Apply config overrides (useful for testing)
    if config_overrides:
        app.config.update(config_overrides)

    # Disable strict JSON parsing to allow form data
    app.config["JSON_AS_ASCII"] = False

    # JWT configuration for cookie support
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_COOKIE_SECURE"] = app.config.get("JWT_COOKIE_SECURE", False)
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["JWT_COOKIE_SAMESITE"] = app.config.get("JWT_COOKIE_SAMESITE", "Lax")

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    # Configure CORS with allowed origins
    allowed_origins = app.config.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
    CORS(
        app,
        origins=allowed_origins.split(","),
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)

    # Initialize database tables on startup
    with app.app_context():
        max_retries = 10
        retry_count = 0
        while retry_count < max_retries:
            try:
                app.logger.info(
                    f"Attempting to create database tables "
                    f"(attempt {retry_count + 1}/{max_retries})"
                )
                db.create_all()
                app.logger.info("✓ Database tables created/verified successfully")
                break
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    app.logger.warning(
                        f"Database not ready yet: {str(e)}. "
                        f"Retrying in 2 seconds..."
                    )
                    time.sleep(2)
                else:
                    app.logger.error(
                        f"Failed to create database tables after "
                        f"{max_retries} attempts: {str(e)}"
                    )



    @app.errorhandler(404)
    def _not_found(_error):
        return jsonify({"message": "Not found"}), 404

    @app.errorhandler(429)
    def _rate_limited(_error):
        return jsonify({"message": "Too many requests"}), 429

    @app.errorhandler(415)
    def _unsupported_media_type(_error):
        return jsonify({"message": "Unsupported media type"}), 415

    @app.errorhandler(400)
    def _bad_request(error):
        return jsonify({"message": "Invalid request format"}), 400

    return app
