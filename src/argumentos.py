"""Flags de linea de comandos del programa (ver main.py)."""
import argparse
import datetime

from .constantes import ARCHIVO_REMITOS, FECHA_CORTE_POR_DEFECTO


def parsear_argumentos(argv=None):
    """Devuelve los argumentos parseados. argv=None usa sys.argv."""
    parser = argparse.ArgumentParser(description="Carga los remitos de Expreso Andino en la API.")
    parser.add_argument("archivo", nargs="?", default=ARCHIVO_REMITOS,
                        help="JSON de remitos (por defecto: %s)" % ARCHIVO_REMITOS.name)
    parser.add_argument("--api-url", help="URL base de la API (tiene prioridad sobre EXPRESO_API_URL)")
    parser.add_argument("--list-delayed", action="store_true",
                        help="lista los envíos cargados no entregados con fecha estimada anterior a --before")
    parser.add_argument("--before", type=datetime.date.fromisoformat, default=FECHA_CORTE_POR_DEFECTO,
                        help="fecha de corte para --list-delayed, AAAA-MM-DD (por defecto: %s)"
                             % FECHA_CORTE_POR_DEFECTO.isoformat())
    return parser.parse_args(argv)
