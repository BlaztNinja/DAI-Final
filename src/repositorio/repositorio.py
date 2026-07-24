from database import obtener_conexion

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
        pass