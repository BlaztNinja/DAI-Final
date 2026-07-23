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
    candidates = [
        "src.repositorio.repositorio",
        "src.repositorio.repository",
        "src.repositorio",
        "repositorio",
    ]

    for module_name in candidates:
        module = _import_module(module_name)
        if module is None:
            continue

        for class_name in (
            "Repositorio",
            "Repository",
            "RepositorioSQLite",
            "SQLiteRepositorio",
            "RepositorioSQL",
        ):
            cls = getattr(module, class_name, None)
            if inspect.isclass(cls):
                try:
                    return cls()
                except TypeError:
                    return cls

        factory = getattr(module, "crear_repositorio", None)
        if callable(factory):
            try:
                return factory()
            except TypeError:
                pass

    return None


def _get_domain_module() -> Optional[Any]:
    for module_name in ("src.domain.entities.entities", "src.domain.entities"):
        module = _import_module(module_name)
        if module is not None and hasattr(module, "OrdenServicio"):
            return module
    return None


def _get_value_objects_module() -> Optional[Any]:
    for module_name in ("src.domain.value_objects.value_objects", "src.domain.value_objects"):
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


def _call_repo(repo: Any, resource_singular: str, action: str, *args: Any) -> Any:
    if repo is None:
        raise RuntimeError("Repositorio no disponible")

    candidates: list[str] = []

    if action == "list":
        candidates = [
            f"listar_{resource_singular}",
            f"listar_{resource_singular}s",
            "listar",
            "list",
        ]
    elif action == "get":
        candidates = [
            f"obtener_{resource_singular}",
            f"leer_{resource_singular}",
            f"get_{resource_singular}",
            "obtener",
            "get",
        ]
    elif action == "create":
        candidates = [
            f"crear_{resource_singular}",
            f"guardar_{resource_singular}",
            "crear",
            "guardar",
            "create",
        ]
    elif action == "update":
        candidates = [
            f"actualizar_{resource_singular}",
            f"editar_{resource_singular}",
            f"guardar_{resource_singular}",
            "actualizar",
            "editar",
            "guardar",
            "update",
        ]
    elif action == "delete":
        candidates = [
            f"eliminar_{resource_singular}",
            f"borrar_{resource_singular}",
            f"delete_{resource_singular}",
            "eliminar",
            "borrar",
            "delete",
        ]

    for name in candidates:
        method = getattr(repo, name, None)
        if callable(method):
            try:
                if action == "list":
                    return method()
                if action == "get":
                    return method(*args)
                if action == "create":
                    return method(*args)
                if action == "update":
                    return method(*args)
                if action == "delete":
                    return method(*args)
            except TypeError:
                continue

    if action == "list" and hasattr(repo, "listar"):
        return repo.listar()
    if action == "get" and hasattr(repo, "obtener"):
        return repo.obtener(*args)
    if action == "create" and hasattr(repo, "guardar"):
        return repo.guardar(*args)
    if action == "update" and hasattr(repo, "guardar"):
        return repo.guardar(*args)
    if action == "delete" and hasattr(repo, "eliminar"):
        return repo.eliminar(*args)

    raise RuntimeError(f"No existe un método de repositorio para {action} ({resource_singular})")


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

    for class_name in ("ServicioMenu", "ServicioPersonalExtra"):
        cls = getattr(module, class_name, None)
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


def _save_domain_object(repo: Any, obj: Any) -> Any:
    for method_name in (
        "guardar",
        "guardar_orden_servicio",
        "guardar_orden",
        "crear_orden_servicio",
        "crear_orden",
    ):
        method = getattr(repo, method_name, None)
        if callable(method):
            return method(obj)
    raise RuntimeError("El repositorio no expone un método guardar() para objetos de dominio")


def _get_order_from_repo(repo: Any, order_id: Any) -> Any:
    for method_name in (
        "obtener",
        "obtener_orden_servicio",
        "obtener_orden",
        "leer_orden_servicio",
        "leer_orden",
    ):
        method = getattr(repo, method_name, None)
        if callable(method):
            try:
                return method(order_id)
            except TypeError:
                continue
    return None