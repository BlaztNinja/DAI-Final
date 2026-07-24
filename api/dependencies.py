from __future__ import annotations

import importlib
import inspect
from typing import Any, Optional

#Dinamicamente importa un modulo y retorna None si no se puede importar
def _import_module(module_name: str) -> Optional[Any]: 
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None

#Importa una instancia de repositorio, accediendo a los datos dentro
def _get_repository() -> Optional[Any]:
    from src.repositorio.repositorio import Repositorio
    return Repositorio()

#Busca el modulo de dominio; usado en _build_order_from_payload
def _get_domain_module() -> Optional[Any]:
    for module_name in ("src.dominio.entities.entities", "src.dominio.entities"):
        module = _import_module(module_name)
        if module is not None and hasattr(module, "OrdenServicio"):
            return module
    return None

#Busca el modulo de value_objects; usado en _coerce_service_payload
def _get_value_objects_module() -> Optional[Any]:
    for module_name in ("src.dominio.value_objects.value_objects", "src.dominio.value_objects"):
        module = _import_module(module_name)
        if module is not None:
            return module
    return None

#Convierte objetos complejos a estructuras serializables (dict, list, etc.) para jsonify
def _serialize(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(v) for v in value]
    if hasattr(value, "to_dict"):
        return _serialize(value.to_dict())
    if hasattr(value, "as_dict"):
        return _serialize(value.as_dict())
    if hasattr(value, "__dict__"):
        data = {}
        for key, item in vars(value).items():
            if key.startswith("_"):
                continue
            data[key] = _serialize(item)
        cls = type(value)
        for name in dir(cls):
            if name.startswith("_"):
                continue
            if isinstance(getattr(cls, name, None), property):
                data[name] = _serialize(getattr(value, name))
        return data
    return str(value)

#Maneja las acciones de CRUD en el repositorio, llamando a los metodos correspondientes
def _llamar_repo(repo: Any, tabla: str, accion: str, *args: Any) -> Any:
    if repo is None:
        raise RuntimeError("Repositorio no disponible")

    metodos = {
        "list": repo.listar,
        "get": repo.obtener,
        "create": repo.crear,
        "update": repo.actualizar,
        "delete": repo.eliminar,
    }

    metodo = metodos[accion]

    if accion == "list":
        return metodo(tabla)
    return metodo(tabla, *args)

#usando OrdenServicio del modulo de dominio, construye un diccionario y retorna una instancia de OrdenServicio
def _build_order_from_payload(payload: dict[str, Any]) -> Any:
    domain_module = _get_domain_module()
    if domain_module is None:
        raise RuntimeError("No se pudo cargar el módulo de dominio")

    order_cls = getattr(domain_module, "OrdenServicio", None)
    if order_cls is None:
        raise RuntimeError("No se encontró OrdenServicio en el dominio")

    signature = inspect.signature(order_cls.__init__)
    kwargs: dict[str, Any] = {}

    for name, parameter in signature.parameters.items():
        if name == "self":
            continue
        if name in payload and parameter.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            kwargs[name] = payload[name]

    try:
        return order_cls(**kwargs)
    except TypeError as exc:
        raise RuntimeError(f"No se pudo crear la orden: {exc}") from exc

#Convierte el payload de un servicio a una instancia de su clase correspondiente
def _coerce_service_payload(service_payload: Any) -> Any:
    module = _get_value_objects_module()
    if module is None:
        return service_payload

    for nombre_clase in ("ServicioMenu", "ServicioPersonalExtra"):
        cls = getattr(module, nombre_clase, None)
        if cls is None:
            continue

        if not isinstance(service_payload, dict):
            return service_payload

        try:
            signature = inspect.signature(cls.__init__)
            kwargs: dict[str, Any] = {}
            for name, parameter in signature.parameters.items():
                if name == "self":
                    continue
                if name in service_payload and parameter.kind in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.KEYWORD_ONLY,
                ):
                    kwargs[name] = service_payload[name]
            instancia = cls(**kwargs)
            if "cantidad_excedente" in service_payload:
                instancia.cantidad_excedente = service_payload["cantidad_excedente"]
            return instancia
        except TypeError:
            continue
    return service_payload

#Guarda un objeto de dominio (orden) en el repositorio y retorna la instancia guardada
def _guardar_domain_object(repo: Any, obj: Any) -> Any:
    return repo.guardar_orden(obj)

#Obtiene una orden del repositorio usando su ID
def _get_orden_de_repo(repo: Any, order_id: Any) -> Any:
    return repo.obtener_orden(order_id)