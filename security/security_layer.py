"""
CAPA DE SEGURIDAD
=================
Módulo responsable de:
1. Control de versiones: compara versión local vs API
2. Login: autenticación contra API y almacenamiento en SQLite

Principios SOLID aplicados:
- Single Responsibility: cada función tiene una única responsabilidad
- Open/Closed: fácil de extender sin modificar el núcleo
"""

import requests
from data.database import DatabaseManager

# ──────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────

VERSION_LOCAL = "1.0.0"  # Versión actual del aplicativo local

VERSION_URL = (
    "https://apitesting.interrapidisimo.co/apicontrollerpruebas/api/"
    "ParametrosFramework/ConsultarParametrosFramework/VPStoreAppControl"
)

LOGIN_URL = (
    "https://apitesting.interrapidisimo.co/FtEntregaElectronica/MultiCanales/"
    "ApiSeguridadPruebas/api/Seguridad/AuthenticaUsuarioApp"
)

LOGIN_HEADERS = {
    "Usuario": "pam.meredy21",
    "Identificacion": "987204545",
    "Accept": "text/json",
    "IdUsuario": "pam.meredy21",
    "IdCentroServicio": "1295",
    "NombreCentroServicio": "PTO/BOGOTA/CUND/COL/OF PRINCIPAL - CRA 30 # 7-45",
    "IdAplicativoOrigen": "9",
    "Content-Type": "application/json",
}

LOGIN_BODY = {
    "Mac": "",
    "NomAplicacion": "Controller APP",
    "Password": "SW50ZXIyMDIx\n",
    "Path": "",
    "Usuario": "cGFtLm1lcmVkeTIx\n",
}

TIMEOUT = 10  # segundos máximo de espera por request


# ──────────────────────────────────────────────
# CONTROL DE VERSIONES
# ──────────────────────────────────────────────

def check_version() -> dict:
    """
    Consulta la versión actual en la API y la compara con la versión local.

    Returns:
        dict con claves:
          - success (bool): si la consulta fue exitosa
          - local (str): versión local
          - remote (str | None): versión de la API
          - status (str): 'updated' | 'outdated' | 'ahead' | 'error'
          - message (str): mensaje legible para el usuario
    """
    try:
        response = requests.get(VERSION_URL, timeout=TIMEOUT)
        response.raise_for_status()  # lanza excepción si status >= 400

        data = response.json()

        # La API devuelve el valor dentro de un campo; ajusta según respuesta real
        version_api = str(data.get("Valor") or data.get("valor") or data.get("version") or "").strip()

        if not version_api:
            return {
                "success": False,
                "local": VERSION_LOCAL,
                "remote": None,
                "status": "error",
                "message": "⚠️ No se pudo leer la versión desde la API.",
            }

        # Comparación semántica simple
        local_parts = [int(x) for x in VERSION_LOCAL.split(".")]
        remote_parts = [int(x) for x in version_api.split(".")]

        if local_parts < remote_parts:
            status, message = "outdated", f"⬆️ Hay una versión más nueva disponible: {version_api}. Por favor actualiza la app."
        elif local_parts > remote_parts:
            status, message = "ahead", f"🚀 Tu versión local ({VERSION_LOCAL}) es más nueva que la del servidor ({version_api})."
        else:
            status, message = "updated", f"✅ Tu app está al día. Versión: {VERSION_LOCAL}"

        return {
            "success": True,
            "local": VERSION_LOCAL,
            "remote": version_api,
            "status": status,
            "message": message,
        }

    except requests.exceptions.ConnectionError:
        return _version_error("❌ Sin conexión a internet. Verifica tu red.")
    except requests.exceptions.Timeout:
        return _version_error("⏱️ La API tardó demasiado en responder. Intenta de nuevo.")
    except requests.exceptions.HTTPError as e:
        return _version_error(f"❌ Error HTTP al consultar versión: {e}")
    except ValueError:
        return _version_error("❌ La API devolvió una respuesta inválida.")
    except Exception as e:
        return _version_error(f"❌ Error inesperado: {e}")


def _version_error(message: str) -> dict:
    """Helper para construir respuestas de error de versión."""
    return {
        "success": False,
        "local": VERSION_LOCAL,
        "remote": None,
        "status": "error",
        "message": message,
    }


# ──────────────────────────────────────────────
# LOGIN
# ──────────────────────────────────────────────

def login() -> dict:
    """
    Realiza la autenticación contra la API y guarda el usuario en SQLite.

    Returns:
        dict con claves:
          - success (bool): si el login fue exitoso
          - user (dict | None): datos del usuario {Usuario, Identificacion, Nombre}
          - message (str): mensaje legible para el usuario
    """
    try:
        response = requests.post(
            LOGIN_URL,
            headers=LOGIN_HEADERS,
            json=LOGIN_BODY,
            timeout=TIMEOUT,
        )

        # ── Validación de código HTTP ──────────────────
        if response.status_code != 200:
            return {
                "success": False,
                "user": None,
                "message": (
                    f"❌ Error de autenticación. "
                    f"Código HTTP: {response.status_code}. "
                    f"Detalle: {response.text[:200]}"
                ),
            }

        data = response.json()

        # ── Extracción de campos del response ──────────
        usuario       = data.get("Usuario")       or data.get("usuario")       or ""
        identificacion = data.get("Identificacion") or data.get("identificacion") or ""
        nombre        = data.get("Nombre")        or data.get("nombre")        or ""

        if not usuario:
            return {
                "success": False,
                "user": None,
                "message": "⚠️ Login exitoso pero la API no devolvió datos de usuario.",
            }

        user_data = {
            "Usuario": usuario,
            "Identificacion": identificacion,
            "Nombre": nombre,
        }

        # ── Persistencia en SQLite ──────────────────────
        db = DatabaseManager()
        db.save_user(user_data)

        return {
            "success": True,
            "user": user_data,
            "message": f"✅ Bienvenido, {nombre}.",
        }

    except requests.exceptions.ConnectionError:
        return {"success": False, "user": None, "message": "❌ Sin conexión. Verifica tu red."}
    except requests.exceptions.Timeout:
        return {"success": False, "user": None, "message": "⏱️ El servidor tardó demasiado. Intenta de nuevo."}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "user": None, "message": f"❌ Error HTTP: {e}"}
    except ValueError:
        return {"success": False, "user": None, "message": "❌ La API devolvió una respuesta no válida (no es JSON)."}
    except Exception as e:
        return {"success": False, "user": None, "message": f"❌ Error inesperado en login: {e}"}
