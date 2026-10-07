"""Constantes del programa de carga de remitos.

La API key no esta aca: se lee del entorno o de .env (ver config.py).
"""
import datetime
from pathlib import Path

# --------------------------------------------------------------------------
# Rutas (relativas a la carpeta del proyecto, no al directorio actual)
# --------------------------------------------------------------------------
PROYECTO = Path(__file__).resolve().parent.parent  # este archivo esta en <proyecto>/src/
ARCHIVO_ENV = PROYECTO / ".env"
ARCHIVO_REMITOS = PROYECTO / "remitos_2026-09-30.json"
RUTA_DB = PROYECTO / "app.db"
RUTA_LOCK = PROYECTO / "app.db.lock"
CARPETA_REPORTES = PROYECTO / "reportes"
CARPETA_SQL = PROYECTO / "sql"

# --------------------------------------------------------------------------
# Base de datos
# --------------------------------------------------------------------------
# sql/shipments.sql usa tablas STRICT (desde SQLite 3.37) y ON CONFLICT ... DO NOTHING (3.24).
SQLITE_VERSION_MINIMA = (3, 37, 0)

# --------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------
# 127.0.0.1 y no "localhost": en Windows "localhost" prueba IPv6 primero y la API
# de prueba solo escucha en IPv4, lo que agrega ~2 s a cada llamada.
URL_POR_DEFECTO = "http://127.0.0.1:8000"
RUTA_ENVIOS = "/v1/shipments"     # POST crea un envio; GET RUTA_ENVIOS/<tracking_id> consulta uno
ESTADO_ENTREGADO = "DELIVERED"    # valor de "status" de un envio entregado
TIMEOUT_SEGUNDOS = 10
REINTENTOS_MAXIMOS = 5            # ante 5xx o error de conexion
INTENTOS_MAXIMOS = REINTENTOS_MAXIMOS + 1  # el intento original + los reintentos
ESPERA_BASE_SEGUNDOS = 0.5        # espera antes del reintento n: ESPERA_BASE * FACTOR_ESPERA ** (n - 1)
FACTOR_ESPERA = 2                 # backoff exponencial: 0.5, 1, 2, 4, 8 s

# --------------------------------------------------------------------------
# Transformacion remito -> payload de la API
# --------------------------------------------------------------------------
TRANSPORTISTA = "expreso andino"  # forma normalizada (ver validacion.normalizar_transportista)

SERVICIOS = {"NORMAL": "standard", "URGENTE": "express"}

# Provincias que acepta la API (GET /v1/provinces), con tildes exactas.
# Unica definicion: la usan schemas/schema_api.py (enum) y sql/shipments.sql (CHECK,
# completado por base_datos.abrir_db).
PROVINCES = [
    "Buenos Aires", "Ciudad Autónoma de Buenos Aires", "Catamarca", "Chaco", "Chubut",
    "Córdoba", "Corrientes", "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza",
    "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe",
    "Santiago del Estero", "Tierra del Fuego", "Tucumán",
]

# Formas en que el export escribe las provincias -> valor exacto de PROVINCES.
PROVINCIAS = {
    "BA": "Buenos Aires",
    "Bs. As.": "Buenos Aires",
    "CABA": "Ciudad Autónoma de Buenos Aires",
    "Capital Federal": "Ciudad Autónoma de Buenos Aires",
    "Cba": "Córdoba",
    "Tucuman": "Tucumán",
    "Neuquen": "Neuquén",
}

# --------------------------------------------------------------------------
# Reporte y --list-delayed
# --------------------------------------------------------------------------
TITULO_ERRONEOS = "Aquí están los remitos erróneos para modificarlos"
FECHA_CORTE_POR_DEFECTO = datetime.date(2026, 10, 3)
