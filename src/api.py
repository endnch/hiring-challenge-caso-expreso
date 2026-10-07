"""Cliente HTTP minimo para la API de Expreso Andino (solo libreria estandar)."""
import json
import urllib.error
import urllib.request
from http import HTTPStatus

from .constantes import TIMEOUT_SEGUNDOS


class ApiKeyInvalida(Exception):
    """La API respondio 401."""


def llamar_api(config, metodo, ruta, cuerpo=None):
    """Hace la llamada y devuelve (codigo_http, json_de_respuesta).

    Los errores HTTP (4xx/5xx) se devuelven como codigo, no como excepcion.
    Un problema de conexion lanza urllib.error.URLError o OSError.
    Un 401 lanza ApiKeyInvalida (nunca se imprime la key).
    """
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    pedido = urllib.request.Request(config.api_url + ruta, data=datos, method=metodo)
    pedido.add_header("X-Api-Key", config.api_key)
    if datos is not None:
        pedido.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(pedido, timeout=TIMEOUT_SEGUNDOS) as respuesta:
            codigo, crudo = respuesta.status, respuesta.read()
    except urllib.error.HTTPError as e:
        codigo, crudo = e.code, e.read()
    if codigo == HTTPStatus.UNAUTHORIZED:
        raise ApiKeyInvalida("API key inválida: revisá EXPRESO_API_KEY")
    try:
        contenido = json.loads(crudo) if crudo else {}
    except ValueError:
        contenido = {"raw": crudo.decode(errors="replace")}
    return codigo, contenido
