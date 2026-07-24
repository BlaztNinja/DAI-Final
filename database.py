import sqlite3

# Base de datos
DATABASE = "sistema_Sazonara.db"


# Conexión
def obtener_conexion():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion


# Crear todas las tablas
def crear_tablas():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # ================= CLIENTE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cliente(
        cliente_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellidos TEXT NOT NULL,
        razon_social TEXT,
        ruc TEXT,
        telefono TEXT,
        email TEXT
    )
    """)

    # ================= CONTACTO =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacto(
        contacto_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        nombre TEXT,
        telefono TEXT,
        email TEXT,
        FOREIGN KEY(cliente_id) REFERENCES cliente(cliente_id)
    )
    """)

    # ================= DIRECCION =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS direccion(
        direccion_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        direccion TEXT,
        ciudad TEXT,
        departamento TEXT,
        FOREIGN KEY(cliente_id) REFERENCES cliente(cliente_id)
    )
    """)

    # ================= EVENTO =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evento(
        evento_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        fecha_evento TEXT,
        hora_inicio TEXT,
        hora_fin TEXT,
        lugar TEXT,
        FOREIGN KEY(cliente_id) REFERENCES cliente(cliente_id)
    )
    """)

    # ================= MENU =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu(
        menu_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        descripcion TEXT,
        precio REAL
    )
    """)

    # ================= ITEM MENU =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_menu(
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu_id INTEGER,
        nombre TEXT,
        descripcion TEXT,
        FOREIGN KEY(menu_id) REFERENCES menu(menu_id)
    )
    """)

    # ================= EVENTO MENU =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evento_menu(
        evento_id INTEGER,
        menu_id INTEGER,
        PRIMARY KEY(evento_id, menu_id),
        FOREIGN KEY(evento_id) REFERENCES evento(evento_id),
        FOREIGN KEY(menu_id) REFERENCES menu(menu_id)
    )
    """)

    # ================= EMPLEADO =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empleado(
        empleado_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT,
        cargo TEXT,
        email TEXT,
        telefono TEXT
    )
    """)

    # ================= ORDEN SERVICIO =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orden_servicio(
        orden_id INTEGER PRIMARY KEY AUTOINCREMENT,
        evento_id INTEGER,
        empleado_id INTEGER,
        fecha TEXT,
        estado TEXT,
        FOREIGN KEY(evento_id) REFERENCES evento(evento_id),
        FOREIGN KEY(empleado_id) REFERENCES empleado(empleado_id)
    )
    """)

    # ================= PAGO =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pago(
        pago_id INTEGER PRIMARY KEY AUTOINCREMENT,
        orden_id INTEGER,
        monto REAL,
        fecha TEXT,
        metodo TEXT,
        FOREIGN KEY(orden_id) REFERENCES orden_servicio(orden_id)
    )
    """)

    # ================= FACTURA =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS factura(
        factura_id INTEGER PRIMARY KEY AUTOINCREMENT,
        orden_id INTEGER,
        numero TEXT,
        total REAL,
        fecha TEXT,
        FOREIGN KEY(orden_id) REFERENCES orden_servicio(orden_id)
    )
    """)

    # ================= CONTROL CALIDAD =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS control_calidad(
        control_id INTEGER PRIMARY KEY AUTOINCREMENT,
        orden_id INTEGER,
        observaciones TEXT,
        resultado TEXT,
        FOREIGN KEY(orden_id) REFERENCES orden_servicio(orden_id)
    )
    """)

    # ================= CONFORMIDAD =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conformidad(
        conformidad_id INTEGER PRIMARY KEY AUTOINCREMENT,
        orden_id INTEGER,
        cliente_firma TEXT,
        fecha TEXT,
        FOREIGN KEY(orden_id) REFERENCES orden_servicio(orden_id)
    )
    """)
    
    # ================= SERVICIO CONTRATADO =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS servicio_contratado(
        servicio_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        tipo TEXT,
        codigo TEXT,
        cantidad_excedente REAL,
        ordenes_en_espera INTEGER,
        FOREIGN KEY(order_id) REFERENCES orden_servicio(orden_id)
    )
    """)

    conexion.commit()
    conexion.close()


# Ejecutar solo una vez para crear la base de datos
crear_tablas()
