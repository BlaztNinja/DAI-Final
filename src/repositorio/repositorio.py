from database import obtener_conexion
from datetime import date
from src.dominio.value_objects.value_objects import ServicioPersonalExtra, ServicioMenu
from src.dominio.entities.entities import OrdenServicio

PK_POR_TABLA = {
    "cliente": "cliente_id",
    "contacto": "contacto_id",
    "direccion": "direccion_id",
    "evento": "evento_id",
    "menu": "menu_id",
    "item_menu": "item_id",
    "empleado": "empleado_id",
    "orden_servicio": "orden_id",
    "pago": "pago_id",
    "factura": "factura_id",
}

class Repositorio:
    
    def listar(self, tabla: str) -> list[dict]:
        con = obtener_conexion()
        filas = con.execute(f"SELECT * FROM {tabla}").fetchall()
        con.close()
        return[dict(fila) for fila in filas]
    
    def obtener(self, tabla:str, id:int) -> dict | None:
        pk = PK_POR_TABLA[tabla]
        con = obtener_conexion()
        fila = con.execute(
            f"SELECT * FROM {tabla} WHERE {pk} = ?", (id,)
        ).fetchone()
        con.close()
        return dict(fila) if fila else None
    
    def crear(self, tabla:str, id:int, datos:dict):
        columnas = ", ".join(datos.keys())
        placeholders = ", ".join(["?"]*len(datos))
        valores = tuple(datos.values())
        con = obtener_conexion()
        cursor = con.execute(
            f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})", (valores)
        )
        con.commit()
        nuevo_id = cursor.lastrowid
        con.close()
        return dict(tabla, nuevo_id)
    
    def actualizar(self, tabla:str, id:int, datos: dict) -> dict | None:
        pk = PK_POR_TABLA[tabla] 
        set_clause = ", ".join([f"{col} = ?"  for col in datos.keys()])
        valores = tuple(datos.values()) + (id,)
        
        con = obtener_conexion()
        con.execute(
            f"UPDATE {tabla} SET {set_clause} WHERE {pk} = ?", valores
        )
        con.commit()
        con.close()
        
        return self.obtener(tabla, id)
    
    def eliminar(self, tabla:str, id:int) -> bool:
        pk = PK_POR_TABLA[tabla]
        con = obtener_conexion()
        
        cursor = con.execute(
            f"DELETE FROM {tabla} WHERE {pk} = ?", (id,)
        )
        con.commit()
        con.close()
        
        return cursor.rowcount > 0
    
    def guardar_orden(self, orden) -> dict:
        con = obtener_conexion()

        # 1. Guardar/actualizar al empleado responsable
        cursor = con.execute(
            "SELECT empleado_id FROM empleado WHERE nombre_completo = ? AND cargo = ?",
            (orden.responsable.nombre_completo, orden.responsable.cargo)
        )
        fila_empleado = cursor.fetchone()

        if fila_empleado:
            empleado_id = fila_empleado["empleado_id"]
        else:
            cursor = con.execute(
                "INSERT INTO empleado (nombre_completo, cargo, email, telefono) VALUES (?, ?, ?, ?)",
                (orden.responsable.nombre_completo, orden.responsable.cargo,
                orden.responsable.email, orden.responsable.telefono)
            )
            empleado_id = cursor.lastrowid

        # 2. Guardar la orden (INSERT si es nueva, UPDATE si ya existía)
        existe = con.execute(
            "SELECT orden_id FROM orden_servicio WHERE orden_id = ?", (orden.orden_id,)
        ).fetchone()

        if existe:
            con.execute(
                "UPDATE orden_servicio SET evento_id = ?, empleado_id = ?, estado = ? WHERE orden_id = ?",
                (orden.evento_id_fk, empleado_id, orden.estado, orden.orden_id)
            )
        else:
            con.execute(
                "INSERT INTO orden_servicio (orden_id, evento_id, empleado_id, fecha, estado) VALUES (?, ?, ?, ?, ?)",
                (orden.orden_id, orden.evento_id_fk, empleado_id,
                date.today().isoformat(), orden.estado)
            )

        # 3. Reemplazar los servicios contratados (borra los viejos, mete los actuales)
        con.execute("DELETE FROM servicio_contratado WHERE orden_id = ?", (orden.orden_id,))

        for servicio in orden.servicios_contratados:
            tipo = "personal_extra" if isinstance(servicio, ServicioPersonalExtra) else "menu"
            ordenes_en_espera = servicio.ordenes_en_espera if tipo == "personal_extra" else None
            con.execute(
                "INSERT INTO servicio_contratado (orden_id, tipo, codigo, cantidad_excedente, ordenes_en_espera) VALUES (?, ?, ?, ?, ?)",
                (orden.orden_id, tipo, servicio.codigo, servicio.cantidad_excedente, ordenes_en_espera)
            )

        con.commit()
        con.close()

        return self.obtener("orden_servicio", orden.orden_id)
    
    def obtener_orden(self, orden_id: int):
        con = obtener_conexion()

        fila_orden = con.execute(
            "SELECT * FROM orden_servicio WHERE orden_id = ?", (orden_id,)
        ).fetchone()
        if not fila_orden:
            con.close()
            return None

        fila_empleado = con.execute(
            "SELECT * FROM empleado WHERE empleado_id = ?", (fila_orden["empleado_id"],)
        ).fetchone()

        orden = OrdenServicio(
            orden_id=fila_orden["orden_id"],
            evento_id_fk=fila_orden["evento_id"],
            nombre_empleado=fila_empleado["nombre_completo"],
            cargo_empleado=fila_empleado["cargo"],
        )
        orden.estado = fila_orden["estado"]

        filas_servicios = con.execute(
            "SELECT * FROM servicio_contratado WHERE orden_id = ?", (orden_id,)
        ).fetchall()

        for fila in filas_servicios:
            if fila["tipo"] == "personal_extra":
                servicio = ServicioPersonalExtra(fila["codigo"], fila["ordenes_en_espera"])
            else:
                servicio = ServicioMenu(fila["codigo"])
            servicio.cantidad_excedente = fila["cantidad_excedente"]
            orden._servicios_contratados.append(servicio)

        con.close()
        return orden