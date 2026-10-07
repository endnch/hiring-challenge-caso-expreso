"""Configuracion del programa: variables de entorno y archivo .env.

Variables:
  EXPRESO_API_KEY  (obligatoria) valor del header X-Api-Key
  EXPRESO_API_URL  (opcional)    URL base de la API, por defecto http://127.0.0.1:8000

Las variables ya definidas en el entorno tienen prioridad sobre el .env.
"""
import os
import sys
from collections import namedtuple
from pathlib import Path

from .constantes import ARCHIVO_ENV, URL_POR_DEFECTO

Config = namedtuple("Config", ["api_key", "api_url"])


def cargar_env(ruta=ARCHIVO_ENV):
    """Carga CLAVE=valor desde un archivo .env, si existe, sin pisar el entorno.

    Ignora lineas vacias y comentarios (#), admite el prefijo "export " y
    quita comillas que envuelvan el valor. Se lee con utf-8-sig por si el
    archivo se creo en PowerShell (que agrega BOM).
    """
    ruta = Path(ruta)
    if not ruta.is_file():
        return
    with open(ruta, encoding="utf-8-sig") as f:
        for numero, linea in enumerate(f, start=1):
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            if linea.startswith("export "):
                linea = linea[len("export "):].lstrip()
            if "=" not in linea:
                print("Aviso: %s línea %d ignorada (falta '=')" % (ruta.name, numero), file=sys.stderr)
                continue
            clave, valor = linea.split("=", 1)
            clave, valor = clave.strip(), valor.strip()
            if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
                valor = valor[1:-1]
            os.environ.setdefault(clave, valor)


def obtener_config(api_url=None):
    """Devuelve la configuracion o termina el programa si falta la API key.

    api_url (del flag --api-url) tiene prioridad sobre EXPRESO_API_URL.
    """
    cargar_env()
    api_key = os.environ.get("EXPRESO_API_KEY", "").strip()
    if not api_key:
        sys.exit("Falta EXPRESO_API_KEY: definila en el entorno o copiá .env.example a .env")
    url = api_url or os.environ.get("EXPRESO_API_URL", "").strip() or URL_POR_DEFECTO
    return Config(api_key=api_key, api_url=url.rstrip("/"))
