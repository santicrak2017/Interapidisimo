
import sqlite3
import requests
from pathlib import Path



DB_PATH = Path(__file__).parent.parent / "data" / "interrapidisimo.db"

ESQUEMA_URL = (
    "https://apitesting.interrapidisimo.co/apicontrollerpruebas/api/"
    "SincronizadorDatos/ObtenerEsquema/true"
)

LOCALIDADES_URL = (
    "https://apitesting.interrapidisimo.co/apicontrollerpruebas/api/"
    "ParametrosFramework/ObtenerLocalidadesRecogidas"
)

TIMEOUT = 10

class DatabaseManager:
    """
    Gestiona todas las operaciones sobre la base de datos SQLite local.
    Implementa el patrón de contexto para manejo seguro de conexiones.
    """

    def __init__(self):
        """Inicializa la BD y crea las tablas si no existen."""
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Retorna una conexión con row_factory para acceso por nombre de columna."""
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_tables(self):
        """
        Crea las tablas necesarias si no existen.
        Se ejecuta al inicio de la aplicación de forma segura (idempotente).
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Tabla de usuario autenticado
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id             INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario        TEXT NOT NULL,
                        identificacion TEXT NOT NULL,
                        nombre         TEXT NOT NULL,
                        fecha_login    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Tabla de esquema (tablas del sistema)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS esquema_tablas (
                        id             INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_tabla   TEXT NOT NULL,
                        descripcion    TEXT,
                        campos         TEXT,
                        fecha_sync     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Tabla de datos de sistema / configuración.
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sistemas (
                        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                        clave               TEXT NOT NULL UNIQUE,
                        valor               TEXT NOT NULL,
                        descripcion         TEXT,
                        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.commit()

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al inicializar la base de datos: {e}")

   

    def save_user(self, user_data: dict):
        """
        Guarda un usuario en la tabla local.
        Limpia registros anteriores para mantener solo el último login.

        Args:
            user_data: dict con keys Usuario, Identificacion, Nombre
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM usuarios")  # solo un usuario activo
                cursor.execute(
                    """
                    INSERT INTO usuarios (usuario, identificacion, nombre)
                    VALUES (?, ?, ?)
                    """,
                    (
                        user_data.get("Usuario", ""),
                        user_data.get("Identificacion", ""),
                        user_data.get("Nombre", ""),
                    ),
                )
                conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al guardar usuario: {e}")

    def get_user(self) -> dict | None:
      
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT usuario, identificacion, nombre FROM usuarios ORDER BY id DESC LIMIT 1"
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "Usuario": row["usuario"],
                        "Identificacion": row["identificacion"],
                        "Nombre": row["nombre"],
                    }
                return None
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al consultar usuario: {e}")

  

    def save_system_value(self, clave: str, valor: str, descripcion: str = ""):
   
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sistemas (clave, valor, descripcion) VALUES (?, ?, ?)"
                    "ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor, descripcion = excluded.descripcion, fecha_actualizacion = CURRENT_TIMESTAMP",
                    (clave, valor, descripcion),
                )
                conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al guardar dato de sistema: {e}")

    def get_system_value(self, clave: str) -> str | None:
        """
        Retorna el valor de sistema para la clave dada, o None si no existe.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT valor FROM sistemas WHERE clave = ? LIMIT 1",
                    (clave,),
                )
                row = cursor.fetchone()
                return row["valor"] if row else None
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al consultar dato de sistema: {e}")

    def get_all_system_values(self) -> list[dict]:
        """
        Retorna todas las claves y valores almacenados en `sistemas`.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT clave, valor, descripcion, fecha_actualizacion FROM sistemas"
                )
                rows = cursor.fetchall()
                return [
                    {
                        "clave": row["clave"],
                        "valor": row["valor"],
                        "descripcion": row["descripcion"],
                        "fecha_actualizacion": row["fecha_actualizacion"],
                    }
                    for row in rows
                ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al leer datos del sistema: {e}")


    def save_tables_schema(self, tables: list[dict]):
        """
        Guarda la lista de tablas del esquema recibidas desde la API
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM esquema_tablas")  # reemplaza en cada sync
                for table in tables:
                    cursor.execute(
                        """
                        INSERT INTO esquema_tablas (nombre_tabla, descripcion, campos)
                        VALUES (?, ?, ?)
                        """,
                        (
                            table.get("NombreTabla") or table.get("nombre") or table.get("Tabla") or "Sin nombre",
                            table.get("Descripcion") or table.get("descripcion") or "",
                            str(table.get("Campos") or table.get("campos") or ""),
                        ),
                    )
                conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al guardar esquema: {e}")

    def get_tables_schema(self) -> list[dict]:
        """Retorna todas las tablas almacenadas en el esquema local."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre_tabla, descripcion, campos, fecha_sync FROM esquema_tablas")
                rows = cursor.fetchall()
                return [
                    {
                        "nombre_tabla": row["nombre_tabla"],
                        "descripcion":  row["descripcion"],
                        "campos":       row["campos"],
                        "fecha_sync":   row["fecha_sync"],
                    }
                    for row in rows
                ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al leer esquema: {e}")




class DataSynchronizer:

    def __init__(self):
        self.db = DatabaseManager()

    def sync_schema(self) -> dict:
       
        try:
            response = requests.get(ESQUEMA_URL, timeout=TIMEOUT)
            response.raise_for_status()

            data = response.json()

            # La API puede devolver la lista directamente o dentro de una clave
            if isinstance(data, list):
                tables = data
            elif isinstance(data, dict):
                tables = (
                    data.get("Tablas")
                    or data.get("tablas")
                    or data.get("Data")
                    or data.get("data")
                    or []
                )
            else:
                tables = []

            if not tables:
                return {
                    "success": False,
                    "count": 0,
                    "message": "⚠️ La API no devolvió tablas en el esquema.",
                }

            self.db.save_tables_schema(tables)

            return {
                "success": True,
                "count": len(tables),
                "message": f" Sincronizadas {len(tables)} tablas correctamente. :))))",
            }

        except requests.exceptions.ConnectionError:
            return {"success": False, "count": 0, "message": " Sin conexión para sincronizar esquema."}
        except requests.exceptions.Timeout:
            return {"success": False, "count": 0, "message": " Timeout al obtener esquema."}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "count": 0, "message": f" Error HTTP: {e}"}
        except RuntimeError as e:
            return {"success": False, "count": 0, "message": str(e)}
        except Exception as e:
            return {"success": False, "count": 0, "message": f" Error ...: {e}"}

    def get_localidades(self) -> dict:
        """
        Consume la API de localidades recogidas y retorna la lista.

        Returns:
            dict con success, data (lista) y message
        """
        try:
            response = requests.get(LOCALIDADES_URL, timeout=TIMEOUT)
            response.raise_for_status()

            data = response.json()

            # Normalizar respuesta
            if isinstance(data, list):
                localidades = data
            elif isinstance(data, dict):
                localidades = (
                    data.get("Localidades")
                    or data.get("localidades")
                    or data.get("Data")
                    or data.get("data")
                    or []
                )
            else:
                localidades = []

            return {
                "success": True,
                "data": localidades,
                "message": f" {len(localidades)} localidades cargadas. ",
            }

        except requests.exceptions.ConnectionError:
            return {"success": False, "data": [], "message": " Sin conexión para cargar localidades."}
        except requests.exceptions.Timeout:
            return {"success": False, "data": [], "message": " Timeout al obtener localidades."}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "data": [], "message": f" Error HTTP: {e}"}
        except Exception as e:
            return {"success": False, "data": [], "message": f" Error inesperado: {e}"}
