from __future__ import annotations

import importlib
import inspect
from typing import Any, Optional


def _import_module(module_name: str) -> Optional[Any]:
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None


def _get_repository() -> Optional[Any]:
    from src.repositorio.repositorio import Repositorio
    return Repositorio()


def _get_domain_module() -> Optional[Any]:
    for module_name in ("src.dominio.entities.entities", "src.dominio.entities"):
        module = _import_module(module_name)
        if module is not None and hasattr(module, "OrdenServicio"):
            return module
    return None


def _get_value_objects_module() -> Optional[Any]:
    for module_name in ("src.dominio.value_objects.value_objects", "src.dominio.value_objects"):
        module = _import_module(module_name)
        if module is not None:
            return module
    return None


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
        return data
    return str(value)


def _call_repo(repo: Any, tabla: str, accion: str, *args: Any) -> Any:
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
    return metodo(tabla, args)


def _llamar_repo(repo: Any, tabla: str, accion: str, *args: Any) -> Any:
    return _call_repo(repo, tabla, accion, *args)


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
            return cls(**kwargs)
        except TypeError:
            continue

    return service_payload


def _guardar_domain_object(repo: Any, obj: Any) -> Any:
    return repo.guardar_orden(obj)


def _get_orden_de_repo(repo: Any, order_id: Any) -> Any:
    return repo.obtener_orden(order_id)