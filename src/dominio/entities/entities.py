from value_objects.value_objects import ServicioContratado, ServicioPersonalExtra, Pago, factura
from datetime import date, datetime

class Empleado:
    """
    Empleado responsable de una Orden_Servicio.

    Este objeto NUNCA se crea de forma independiente y luego se "engancha" a
    la orden: se instancia obligatoriamente dentro del constructor de
    OrdenServicio (Composicion pura).
    """

    def __init__(self, nombre_completo: str, cargo: str,
                 email: str = "", telefono: str = ""):
        self.nombre_completo = nombre_completo
        self.cargo = cargo  # "Coordinador", "AUX-Logistica", etc.
        self.email = email
        self.telefono = telefono

    def es_personal_auxiliar(self) -> bool:
        return self.cargo.upper().startswith("AUX")

    def __repr__(self):
        return f"Empleado({self.nombre_completo}, cargo={self.cargo})"


class OrdenServicio:
    """
    Entidad CONDUCTORA del sistema.

    Invariante de negocio: una OrdenServicio no puede existir sin un
    Empleado responsable. Por eso el Empleado se crea DENTRO del
    constructor, nunca se recibe como objeto ya armado desde afuera.
    """

    MAX_SERVICIOS_POR_ORDEN = 4

    def __init__(self, orden_id: int, evento_id_fk: int,
                 nombre_empleado: str, cargo_empleado: str,
                 monto_total: float = 0.0):
        self.orden_id = orden_id
        self.evento_id_fk = evento_id_fk
        self.monto_total = monto_total
        self.estado = "PENDIENTE"

        self._responsable = Empleado(nombre_empleado, cargo_empleado)
        self._servicios_contratados = []
        self.factura = None
        self.pago = None

    @property
    def responsable(self) -> Empleado:
        return self._responsable

    @property
    def servicios_contratados(self):
        """
        Encapsulamiento defensivo: entrega la lista como una TUPLA
        (coleccion congelada/inmutable). Si algo externo intenta hacer
        .append() o .clear() sobre lo que retorna esta propiedad, Python
        arrojara un AttributeError de inmediato porque las tuplas no
        soportan esos metodos.
        """
        return tuple(self._servicios_contratados)

    def cargar_servicio(self, servicio: ServicioContratado) -> None:
        if self.estado == "CUENTA_SUSPENDIDA":
            raise RuntimeError(
                "No se pueden cargar servicios: la orden esta suspendida."
            )
        if len(self._servicios_contratados) >= self.MAX_SERVICIOS_POR_ORDEN:
            raise ValueError("Limite de servicios por orden alcanzado")
        self._servicios_contratados.append(servicio)

    def calcular_recargos_totales(self) -> float:
        """
        Ordena a TODOS los servicios cargados calcular su recargo
        simultaneamente, sin saber de que tipo especifico es cada uno.
        Este es el punto exacto de Polimorfismo puro.
        """
        return sum(s.calcular_recargo() for s in self._servicios_contratados)

    def generarOrden(self) -> None:
        if self.estado == "CUENTA_SUSPENDIDA":
            raise RuntimeError("No se puede generar la orden: cuenta suspendida.")

        self.factura = factura.crear(
            factura_id=0,
            orden_id_fk=self.orden_id,
            fecha_emision=datetime.now(),
            monto_facturado=self.monto_total,
            Estado_CDFI="PENDIENTE",
        )

        print(f"Orden {self.orden_id} generada correctamente. "
              f"Responsable: {self._responsable.nombre_completo}")

    def procesarPago(self, metodo_pago: str = "Efectivo", tipo_pago: str = "Total") -> bool:
        if self.estado == "CUENTA_SUSPENDIDA":
            raise RuntimeError("No se puede procesar el pago: cuenta suspendida.")

        self.pago = Pago.crear(
            orden_id_fk=self.orden_id,
            fecha_pago=date.today(),
            monto=self.monto_total,
            metodo_pago=metodo_pago,
            tipo_pago=tipo_pago,
        )

        print(f"Pago de la orden {self.orden_id} procesado por "
              f"${self.monto_total:.2f}")
        return True
    
    def generar_control_calidad(self) -> None:
        pass

class ControlCalidad:
    """
    Entidad que representa el control de calidad de una orden de servicio.
    Esta entidad se encarga de verificar que todos los servicios contratados
    cumplan con los estándares de calidad establecidos por la empresa.
    """

    def __init__(self, orden: OrdenServicio, controlid: int, tipo_manipulacion: str, uso_mascarilla: bool, uso_guantes: bool, red_cabello: bool, observaciones: str):
        self.orden_id = orden
        self.controlid = controlid
        self.tipo_manipulacion = tipo_manipulacion
        self.uso_mascarilla = uso_mascarilla
        self.uso_guantes = uso_guantes


    def verificar_calidad(self) -> bool:
        """
        Verifica la calidad de todos los servicios contratados en la orden.
        Retorna True si todos los servicios cumplen con los estándares,
        False en caso contrario.
        """
        for servicio in self.orden.servicios_contratados:
            if not self._verificar_servicio(servicio):
                return False
        return True

    def _verificar_servicio(self, servicio: ServicioContratado) -> bool:
        """
        Verifica la calidad de un servicio individual.
        Este método puede ser extendido para incluir criterios específicos
        de verificación según el tipo de servicio.
        """
        # Implementación simplificada: siempre retorna True
        return True

class Conformidad:
    """
    Entidad que representa la conformidad del cliente con los servicios
    prestados en una orden de servicio. Esta entidad se encarga de registrar
    la satisfacción del cliente y cualquier comentario adicional.
    """

    def __init__(self, orden: OrdenServicio, conformidad_id: int, fecha_conformidad: datetime, observacion_cliente: str, servicio_conforme: bool, firma_cliente: str, firma_sazonora: str):
        self.orden_id = orden
        self.conformidad_id = conformidad_id
        self.fecha_conformidad = fecha_conformidad
        self.observacion_cliente = observacion_cliente
        self.servicio_conforme = servicio_conforme
        self.firma_cliente = firma_cliente
        self.firma_sazonora = firma_sazonora


    def registrar_conformidad(self) -> None:
        """
        Registra la conformidad del cliente con los servicios prestados.
        """
        if self.servicio_conforme:
            print(f"Cliente satisfecho con la orden {self.orden_id}.")
        else:
            print(f"Cliente insatisfecho con la orden {self.orden_id}. "
                  f"Comentarios: {self.observacion_cliente}")

# ==============================================================================
# COMMIT 2 - EVOLUCION DEL DOMINIO (nueva regla de negocio)
# ==============================================================================
#
# "Si al finalizar una revision de recargos, el PROMEDIO de recargos de
# todos los servicios contratados en la orden supera los $15.00, O si el
# empleado responsable es Personal Auxiliar (cargo inicia con 'AUX') Y la
# orden tiene un ServicioPersonalExtra con mas de 10 ordenes en espera,
# el sistema debe activar automaticamente un protocolo de restriccion,
# cambiando el estado de la orden a 'CUENTA_SUSPENDIDA'."
#
# Esta regla vive aqui (en entities.py, junto a OrdenServicio) porque
# depende de la RELACION entre varios servicios y del empleado responsable,
# nunca de un solo servicio individual. Por eso NO puede vivir dentro de
# ServicioMenu ni de ServicioPersonalExtra.
# ==============================================================================

def revisar_y_aplicar_restriccion(orden: OrdenServicio) -> None:
    """
    Ejecuta la revision de saldos de una OrdenServicio y aplica el
    protocolo de restriccion si corresponde.
    """
    servicios = orden.servicios_contratados  # tupla inmutable

    if not servicios:
        return

    total_recargos = sum(s.calcular_recargo() for s in servicios)
    promedio_recargos = total_recargos / len(servicios)

    condicion_promedio = promedio_recargos > 15.00

    empleado_es_aux = orden.responsable.es_personal_auxiliar()
    hay_personal_extra_criticos = any(
        isinstance(s, ServicioPersonalExtra) and s.ordenes_en_espera > 10
        for s in servicios
    )
    condicion_aux = empleado_es_aux and hay_personal_extra_criticos

    if condicion_promedio or condicion_aux:
        orden.estado = "CUENTA_SUSPENDIDA"
        print(f"[ALERTA] Orden {orden.orden_id} -> estado cambiado a "
              f"'CUENTA_SUSPENDIDA' (promedio_recargos=${promedio_recargos:.2f})")
    else:
        print(f"Orden {orden.orden_id} dentro de parametros normales "
              f"(promedio_recargos=${promedio_recargos:.2f})")
