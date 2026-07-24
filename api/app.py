from __future__ import annotations

import os
import sys

#Bsca el path del proyecto para que los modulos puedan ser importados correctamente
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify

from api.routes.crud_routes import crud_bp
from api.routes.ordenes_routes import ordenes_bp

#Instancia el Flask app y registra los blueprints de las rutas
def crear_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    app.register_blueprint(crud_bp)
    app.register_blueprint(ordenes_bp)
    
    #Este route es para el predeterminado al llamar al http://localhost:5000
    @app.route("/")
    def index():
        endpoints = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint == "static":
                continue
            methods = sorted(rule.methods - {"HEAD", "OPTIONS"})
            endpoints.append(
                {
                    "path": rule.rule,
                    "endpoint": rule.endpoint,
                    "methods": methods,
                }
            )
        return jsonify({
            "message": "API disponible",
            "base_url": "http://localhost:5000",
            "endpoints": endpoints,
        })

    return app

#Crea la app globalmente
app = crear_app()


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)