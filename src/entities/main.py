from entities.entities import OrdenServicio, revisar_y_aplicar_restriccion
from value_objects.value_objects import ServicioMenu, ServicioPersonalExtra

if __name__ == "__main__":
    print("=== COMMIT 1: escenario base ===")
    orden = OrdenServicio(
        orden_id=101,
        evento_id_fk=55,
        nombre_empleado="Gabriel Meneses",
        cargo_empleado="Coordinador",
        monto_total=850.0,
    )
    orden.generarOrden()

    menu_extra = ServicioMenu("SM-01")
    menu_extra.cantidad_excedente = 6
    orden.cargar_servicio(menu_extra)

    personal_extra = ServicioPersonalExtra("SPE-01", ordenes_en_espera=4)
    personal_extra.cantidad_excedente = 3
    orden.cargar_servicio(personal_extra)

    print("Recargos totales:", orden.calcular_recargos_totales())

    try:
        orden.servicios_contratados.append("hackeo")
    except AttributeError as e:
        print("Bloqueado como se esperaba ->", e)

    try:
        for i in range(3):
            orden.cargar_servicio(ServicioMenu(f"SM-0{i+2}"))
    except ValueError as e:
        print("Bloqueado como se esperaba ->", e)

    print("\n=== COMMIT 2: evolucion del dominio ===")
    revisar_y_aplicar_restriccion(orden)

    try:
        orden.procesarPago()
    except RuntimeError as e:
        print("Bloqueado como se esperaba ->", e)
