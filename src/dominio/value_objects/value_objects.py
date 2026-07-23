from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
import itertools


class ServicioContratado(ABC):
    """
    Todo ServicioContratado tiene un codigo identificador y una cantidad de
    UNIDADES EXCEDENTES (analogo a 'dias/horas de retraso'), que inicia en 0.

    La entidad conductora (OrdenServicio) jamas debe saber si un servicio es
    de tipo Menu o de tipo Personal: solo pide 'calcular_recargo()' y cada
    uno responde segun su propia naturaleza (Polimorfismo puro).
    """

    def __init__(self, codigo: str):
        self.codigo = codigo
        self.cantidad_excedente: float = 0

    @abstractmethod
    def calcular_recargo(self) -> float:
        """Cada subclase decide como se calcula su propio recargo."""
        pass


class ServicioMenu(ServicioContratado):
    """
    Tarifa FIJA por cada unidad excedente.

    Escenario de negocio: invitados que asistieron al evento por encima del
    numero_asistentes originalmente contratado en el Menu. Cada invitado
    excedente cuesta una tarifa fija.
    """
    TARIFA_FIJA_POR_INVITADO_EXCEDENTE = 2.50

    def calcular_recargo(self) -> float:
        return self.cantidad_excedente * self.TARIFA_FIJA_POR_INVITADO_EXCEDENTE


class ServicioPersonalExtra(ServicioContratado):
    """
    Tarifa VARIABLE segun un factor de demanda.

    Escenario de negocio: horas extra de personal (meseros, chefs, montaje)
    requeridas mas alla de lo planificado. El factor de recargo por hora
    depende de cuantas otras Ordenes_Servicio estan en espera en el mismo
    ciclo de revision (a mayor demanda de personal en la agenda, mas cara
    la hora extra).
    """

    def __init__(self, codigo: str, ordenes_en_espera: int = 0):
        super().__init__(codigo)
        self.ordenes_en_espera = ordenes_en_espera

    def _factor_demanda(self) -> float:
        # A mayor cantidad de ordenes en espera, mayor el costo por hora extra
        return 5.0 + (self.ordenes_en_espera * 0.75)

    def calcular_recargo(self) -> float:
        return self.cantidad_excedente * self._factor_demanda()
    
@dataclass(frozen=True)
class Pago():
    pago_id: int
    orden_id_fk: int
    fecha_pago: date
    monto: float
    metodo_pago: str
    tipo_pago: str
    
    __contador=itertools.count(1)
    
    @classmethod
    def crear(cls, orden_id_fk:int, fecha_pago:date, monto:float, metodo_pago:str, tipo_pago:str) -> "Pago":
        return cls(
            pago_id = next(cls.__contador),
            orden_id_fk = orden_id_fk,
            fecha_pago = fecha_pago,
            monto = monto,
            metodo_pago = metodo_pago,
            tipo_pago = tipo_pago,
        )
    
@dataclass(frozen=True)
class factura():
    factura_id: int
    orden_id_fk: int
    fecha_emision: datetime
    monto_facturado: float
    Estado_CDFI: str
    
    __contador = itertools.count(1)
    
    @classmethod
    def crear(cls, factura_id:int, orden_id_fk:int, fecha_emision:datetime, monto_facturado:float, Estado_CDFI:str,):
        return cls(
            factura_id = next(cls.__contador),
            orden_id_fk = orden_id_fk,
            fecha_emision = fecha_emision,
            monto_facturado = monto_facturado,
            Estado_CDFI = Estado_CDFI,
        )