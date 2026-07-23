from __future__ import annotations

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask

from api.routes.crud_routes import crud_bp
from api.routes.ordenes_routes import ordenes_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    app.register_blueprint(crud_bp)
    app.register_blueprint(ordenes_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)