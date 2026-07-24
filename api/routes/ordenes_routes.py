from __future__ import annotations

from flask import Blueprint, jsonify, request

from api.dependencies import (
    _build_order_from_payload,
    _llamar_repo,
    _coerce_service_payload,
    _get_orden_de_repo,
    _get_repository,
    _guardar_domain_object,
    _serialize,
)

ordenes_bp = Blueprint("ordenes", __name__)

#Consigue la lista de ordenes de servicio(GET) o crea una nueva orden(POST)
@ordenes_bp.route("/ordenes-servicio", methods=["GET", "POST"])
def ordenes_servicio_collection():
    repo = _get_repository()
    if repo is None:
        return jsonify({"error": "Repositorio no disponible"}), 503

    try:
        if request.method == "GET":
            data = _llamar_repo(repo, "orden_servicio", "list")
            return jsonify(_serialize(data)), 200

        payload = request.get_json(silent=True) or {}
        orden = _build_order_from_payload(payload)
        saved = _guardar_domain_object(repo, orden)
        return jsonify(_serialize(saved)), 201

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

#Consigue los detalles de una orden de servicio específica usando el id
@ordenes_bp.route("/ordenes-servicio/<resource_id>", methods=["GET"])
def orden_servicio_detail(resource_id):
    repo = _get_repository()
    if repo is None:
        return jsonify({"error": "Repositorio no disponible"}), 503

    try:
        orden = _get_orden_de_repo(repo, resource_id)
        if orden is None:
            return jsonify({"error": "Orden no encontrada"}), 404
        return jsonify(_serialize(orden)), 200

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

#agrega un servicio a una orden de servicio específica y aplica restricciones si es necesario (reglas de negocio)
@ordenes_bp.route("/ordenes-servicio/<resource_id>/servicios", methods=["POST"])
def cargar_servicios(resource_id):
    repo = _get_repository()
    if repo is None:
        return jsonify({"error": "Repositorio no disponible"}), 503

    try:
        orden = _get_orden_de_repo(repo, resource_id)
        if orden is None:
            return jsonify({"error": "Orden no encontrada"}), 404

        payload = request.get_json(silent=True) or {}
        services = payload if isinstance(payload, list) else [payload]

        for service_payload in services:
            servicio_obj = _coerce_service_payload(service_payload)
            if hasattr(orden, "cargar_servicio"):
                orden.cargar_servicio(servicio_obj)
            else:
                raise RuntimeError("La orden no expone cargar_servicio()")

        if hasattr(orden, "revisar_y_aplicar_restriccion"):
            orden.revisar_y_aplicar_restriccion(orden)

        saved = _guardar_domain_object(repo, orden)
        return jsonify(_serialize(saved)), 200

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

#Genera una factura para una orden de servicio específica
@ordenes_bp.route("/ordenes-servicio/<resource_id>/generar-factura", methods=["POST"])
def generar_factura(resource_id):
    repo = _get_repository()
    if repo is None:
        return jsonify({"error": "Repositorio no disponible"}), 503

    try:
        orden = _get_orden_de_repo(repo, resource_id)
        if orden is None:
            return jsonify({"error": "Orden no encontrada"}), 404

        method = getattr(orden, "generarOrden", None) or getattr(orden, "generar_orden", None)
        if method is None:
            raise RuntimeError("La orden no expone generarOrden()")

        method()
        saved = _guardar_domain_object(repo, orden)
        return jsonify(_serialize(saved)), 200

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

#invoca el metodo de la orden para procesar el pago de una orden de servicio específica
@ordenes_bp.route("/ordenes-servicio/<resource_id>/procesar-pago", methods=["POST"])
def procesar_pago(resource_id):
    repo = _get_repository()
    if repo is None:
        return jsonify({"error": "Repositorio no disponible"}), 503

    try:
        orden = _get_orden_de_repo(repo, resource_id)
        if orden is None:
            return jsonify({"error": "Orden no encontrada"}), 404

        method = getattr(orden, "procesarPago", None) or getattr(orden, "procesar_pago", None)
        if method is None:
            raise RuntimeError("La orden no expone procesarPago()")

        method()
        saved = _guardar_domain_object(repo, orden)
        return jsonify(_serialize(saved)), 200

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500