from __future__ import annotations

from typing import Optional

from flask import Blueprint, jsonify, request

from api.dependencies import _llamar_repo, _get_repository, _serialize

crud_bp = Blueprint("crud", __name__)

#crea una vista CRUD genérica para un recurso específico, manejando GET, POST, PUT y DELETE
#resource_plural esta por temas de escalabilidad
def _build_crud_view(resource_plural: str, resource_singular: str):
    def view(resource_id: Optional[str] = None):
        repo = _get_repository()
        if repo is None:
            return jsonify({"error": "Repositorio no disponible"}), 503

        try:
            if request.method == "GET":
                if resource_id is None:
                    data = _llamar_repo(repo, resource_singular, "list")
                    return jsonify(_serialize(data)), 200

                data = _llamar_repo(repo, resource_singular, "get", resource_id)
                if data is None:
                    return jsonify({"error": "No encontrado"}), 404
                return jsonify(_serialize(data)), 200

            if request.method == "POST":
                payload = request.get_json(silent=True) or {}
                data = _llamar_repo(repo, resource_singular, "create", payload)
                return jsonify(_serialize(data)), 201

            if request.method == "PUT":
                payload = request.get_json(silent=True) or {}
                data = _llamar_repo(repo, resource_singular, "update", resource_id, payload)
                return jsonify(_serialize(data)), 200

            if request.method == "DELETE":
                result = _llamar_repo(repo, resource_singular, "delete", resource_id)
                return jsonify({"deleted": bool(result)}), 200

            return jsonify({"error": "Método no soportado"}), 405

        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return view


for plural, singular in [
    ("clientes", "cliente"),
    ("contactos", "contacto"),
    ("direcciones", "direccion"),
    ("eventos", "evento"),
    ("menus", "menu"),
    ("items-menu", "item_menu"),
    ("empleados", "empleado"),
]:
    endpoint_prefix = plural.replace("-", "_")
    crud_bp.add_url_rule(
        f"/{plural}",
        view_func=_build_crud_view(plural, singular),
        endpoint=f"{endpoint_prefix}_list_create",
        methods=["GET", "POST"],
    )
    crud_bp.add_url_rule(
        f"/{plural}/<resource_id>",
        view_func=_build_crud_view(plural, singular),
        endpoint=f"{endpoint_prefix}_detail",
        methods=["GET", "PUT", "DELETE"],
    )