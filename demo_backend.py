from __future__ import annotations

import time

from api.app import app


def ejecutar_demo() -> None:
    print("\n=== Demo del backend ===")
    print("Vamos a recorrer un caso real de uso, paso a paso.\n")

    with app.test_client() as client:
        print("1) Creamos un cliente")
        respuesta_cliente = client.post(
            "/clientes",
            json={
                "nombre": "Ana",
                "apellidos": "Pérez",
                "razon_social": "Ana Eventos",
                "ruc": "12345678901",
                "telefono": "987654321",
                "email": "ana@example.com",
            },
        )
        cliente = respuesta_cliente.get_json()
        print("   Cliente registrado:", cliente.get("nombre"), cliente.get("apellidos"))

        print("\n2) Creamos un evento para ese cliente")
        respuesta_evento = client.post(
            "/eventos",
            json={
                "cliente_id": cliente.get("cliente_id"),
                "fecha_evento": "2026-08-15",
                "hora_inicio": "18:00",
                "hora_fin": "22:00",
                "lugar": "Salón Central",
            },
        )
        evento = respuesta_evento.get_json()
        print("   Evento creado para:", evento.get("lugar"))

        print("\n3) Creamos una orden de servicio")
        orden_id = 1000 + int(time.time()) % 10000
        respuesta_orden = client.post(
            "/ordenes-servicio",
            json={
                "orden_id": orden_id,
                "evento_id_fk": evento.get("evento_id"),
                "nombre_empleado": "Gabriel Meneses",
                "cargo_empleado": "Coordinador",
                "monto_total": 850.0,
            },
        )
        orden = respuesta_orden.get_json()
        print("   Orden creada con número:", orden_id)

        print("\n4) Cargamos servicios a la orden")
        respuesta_servicios = client.post(
            f"/ordenes-servicio/{orden_id}/servicios",
            json=[
                {"codigo": "MENU-01"},
                {"codigo": "SPE-01", "ordenes_en_espera": 3},
            ],
        )
        print("   Servicios agregados correctamente")

        print("\n5) Generamos la factura")
        respuesta_factura = client.post(f"/ordenes-servicio/{orden_id}/generar-factura")
        print("   Factura solicitada con éxito")

        print("\n6) Procesamos el pago")
        respuesta_pago = client.post(f"/ordenes-servicio/{orden_id}/procesar-pago")
        print("   Pago procesado correctamente")

        print("\n7) Revisamos la orden registrada")
        respuesta_detalle = client.get(f"/ordenes-servicio/{orden_id}")
        detalle = respuesta_detalle.get_json()
        print("   Estado final de la orden:", detalle.get("estado"))

    print("\n=== Demo finalizada ===")
    print("Todo el flujo quedó registrado en el sistema.")


if __name__ == "__main__":
    ejecutar_demo()
