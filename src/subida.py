"""Subida de envios a la API, con reintentos."""
import time
import urllib.error
from enum import Enum
from http import HTTPStatus

from .api import llamar_api
from .constantes import ESPERA_BASE_SEGUNDOS, FACTOR_ESPERA, INTENTOS_MAXIMOS, RUTA_ENVIOS


class Tipo(Enum):
    NUEVO = "nuevo"                    # lo creo esta corrida (201, o 409 despues de un fallo)
    RECUPERADO = "recuperado"          # 409 en el primer intento: ya existia de una batch anterior
    ERROR = "error"                    # la API rechazo los datos (4xx): hay que corregir el remito
    NO_DISPONIBLE = "no disponible"    # se agotaron los reintentos (5xx / sin conexion): los datos estan bien


def subir(config, payload):
    """POST con reintentos. Devuelve un dict con:
      tipo: Tipo.NUEVO | Tipo.RECUPERADO | Tipo.ERROR | Tipo.NO_DISPONIBLE
      tracking_id, fallos (codigos 5xx / errores de conexion vistos), detalle,
      creado_en_fallo: True si un intento que fallo igual habia creado el envio (409 posterior)
    """
    fallos = []
    for intento in range(1, INTENTOS_MAXIMOS + 1):
        try:
            codigo, cuerpo = llamar_api(config, "POST", RUTA_ENVIOS, payload)
        except (urllib.error.URLError, OSError) as e:
            codigo, cuerpo = None, {"error": str(e)}

        if codigo == HTTPStatus.CREATED:
            return {"tipo": Tipo.NUEVO, "tracking_id": cuerpo["tracking_id"],
                    "fallos": fallos, "creado_en_fallo": False}

        if codigo == HTTPStatus.CONFLICT:
            # En el primer intento: se presume creado en una batch anterior.
            # Despues de un fallo: el intento fallido llego a crearlo (lo creo esta corrida).
            tipo = Tipo.NUEVO if fallos else Tipo.RECUPERADO
            return {"tipo": tipo, "tracking_id": cuerpo.get("tracking_id"),
                    "fallos": fallos, "creado_en_fallo": bool(fallos)}

        if codigo is None or codigo >= HTTPStatus.INTERNAL_SERVER_ERROR:  # 5xx o sin conexion
            fallos.append(codigo or "sin conexión")
            if intento < INTENTOS_MAXIMOS:
                time.sleep(ESPERA_BASE_SEGUNDOS * FACTOR_ESPERA ** (intento - 1))
            continue

        # Otro 4xx (422, 400, 404...): no tiene sentido reintentar.
        detalles = cuerpo.get("details")
        if detalles:
            detalle = "; ".join("%s: %s" % (x.get("field"), x.get("message")) for x in detalles)
        else:
            detalle = cuerpo.get("message") or cuerpo.get("error") or str(cuerpo)
        return {"tipo": Tipo.ERROR, "tracking_id": None, "fallos": fallos,
                "detalle": "la API respondió %s: %s" % (codigo, detalle)}

    return {"tipo": Tipo.NO_DISPONIBLE, "tracking_id": None, "fallos": fallos,
            "detalle": "API no disponible: falló %d veces (%s)" % (
                len(fallos), ", ".join(str(f) for f in fallos))}
