"""--list-delayed: envios cargados que no estan entregados y cuya fecha estimada
de entrega es anterior a la fecha de corte (por defecto, 3 de octubre de 2026).

El estado y la fecha estimada no se guardan en app.db: se consultan en el momento
a la API con GET /v1/shipments/{tracking_id}, asi siempre estan actualizados.
"""
import datetime
import sqlite3
import urllib.error
from http import HTTPStatus

from .api import llamar_api
from .constantes import ESTADO_ENTREGADO, FECHA_CORTE_POR_DEFECTO, RUTA_ENVIOS
from .tabla import IZQUIERDA, imprimir_tabla

COLUMNAS = [
    ("Remito", 12, IZQUIERDA),
    ("Tracking", 12, IZQUIERDA),
    ("Estado", 11, IZQUIERDA),
    ("Estimada", 10, IZQUIERDA),
]


def listar_demorados(config, ruta_db, fecha_corte=FECHA_CORTE_POR_DEFECTO):
    if not ruta_db.is_file():
        print("No existe %s: todavía no se cargó ningún envío." % ruta_db.name)
        return

    db = sqlite3.connect(ruta_db)
    try:
        envios = db.execute(
            "SELECT external_ref, tracking_id FROM shipments "
            "WHERE tracking_id IS NOT NULL ORDER BY external_ref").fetchall()
    finally:
        db.close()

    demorados, no_encontrados, sin_respuesta = [], [], []
    for ref, tracking_id in envios:
        try:
            codigo, cuerpo = llamar_api(config, "GET", "%s/%s" % (RUTA_ENVIOS, tracking_id))
        except (urllib.error.URLError, OSError):
            sin_respuesta.append(ref)
            continue
        if codigo == HTTPStatus.NOT_FOUND:
            no_encontrados.append(ref)
            continue
        if codigo != HTTPStatus.OK:
            sin_respuesta.append(ref)
            continue
        eta = datetime.date.fromisoformat(cuerpo["estimated_delivery"])
        if cuerpo["status"] != ESTADO_ENTREGADO and eta < fecha_corte:
            demorados.append((ref, tracking_id, cuerpo["status"], eta.isoformat()))

    print("Envíos no entregados con fecha estimada anterior al %s" % fecha_corte.isoformat())
    print()
    if demorados:
        imprimir_tabla(COLUMNAS, demorados)
    print("%d de %d envíos consultados están demorados." % (len(demorados), len(envios)))
    if no_encontrados:
        print("La API no encontró: %s" % ", ".join(no_encontrados))
    if sin_respuesta:
        print("No se pudo consultar: %s" % ", ".join(sin_respuesta))
