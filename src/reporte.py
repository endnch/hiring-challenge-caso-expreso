"""Reporte de cada corrida, en reportes/."""
import json

from .constantes import CARPETA_REPORTES, TITULO_ERRONEOS
from .validacion import es_expreso_andino


def ruta_reporte(batch_id, ahora):
    marca = ahora.strftime("%Y%m%d-%H%M%SZ")  # Z: hora UTC (ISO 8601)
    base = "reporte_batch_%d_%s" % (batch_id, marca) if batch_id else "reporte_sin_batch_%s" % marca
    ruta = CARPETA_REPORTES / (base + ".txt")
    n = 2
    while ruta.exists():  # dos corridas en el mismo segundo
        ruta = CARPETA_REPORTES / ("%s_%d.txt" % (base, n))
        n += 1
    return ruta


def escribir_reporte(r, ahora):
    """ahora: datetime en UTC (se usa en el nombre del archivo y en el encabezado)."""
    # Red de seguridad: los erroneos tienen que ser solo de Expreso Andino.
    assert all(es_expreso_andino(e["remito"]) for e in r["erroneos"])

    lineas = []
    agregar = lineas.append

    def seccion(titulo):
        agregar("")
        agregar(titulo)
        agregar("=" * len(titulo))

    agregar("Reporte de carga de remitos - Expreso Andino")
    agregar("Fecha: %s UTC" % ahora.strftime("%Y-%m-%d %H:%M:%S"))
    agregar("Archivo: %s" % r["archivo"])
    if r["batch_id"]:
        agregar("Batch: %d" % r["batch_id"])
    else:
        agregar("No se realizaron operaciones: no se creó ningún envío nuevo ni un nuevo batch.")

    seccion("Resumen")
    agregar("Remitos en el archivo:              %d" % r["total"])
    agregar("Filtrados (otro transportista):     %d" % len(r["filtrados"]))
    agregar("De Expreso Andino:                  %d" % r["total_andino"])
    agregar("Duplicados descartados:             %d" % len(r["duplicados"]))
    agregar("Envíos nuevos creados:              %d" % len(r["nuevos"]))
    agregar("Recuperados (ya existían en la API): %d" % len(r["recuperados"]))
    agregar("Ya registrados en app.db:           %d" % len(r["ya_registrados"]))
    agregar("Erróneos:                           %d" % len(r["erroneos"]))

    seccion("Envíos nuevos creados")
    for ref, tracking_id in r["nuevos"]:
        agregar("%s -> %s" % (ref, tracking_id))
    if not r["nuevos"]:
        agregar("(ninguno)")

    seccion("Recuperados (409 en el primer intento; registrados sin batch)")
    for ref, tracking_id in r["recuperados"]:
        agregar("%s -> %s" % (ref, tracking_id))
    if not r["recuperados"]:
        agregar("(ninguno)")

    seccion("Ya registrados en app.db (no se enviaron)")
    agregar(", ".join(r["ya_registrados"]) if r["ya_registrados"] else "(ninguno)")

    seccion("Observaciones")
    for o in r["observaciones"]:
        agregar("- " + o)
    if not r["observaciones"]:
        agregar("(ninguna)")

    seccion("Remitos filtrados al principio (no son de Expreso Andino)")
    for f in r["filtrados"]:
        agregar("%s | %s | %s" % (f.get("nro_remito"), f.get("transportista", "").strip(),
                                 f.get("destinatario", {}).get("razon_social", "")))
    if not r["filtrados"]:
        agregar("(ninguno)")

    seccion(TITULO_ERRONEOS)
    if not r["erroneos"]:
        agregar("(ninguno)")
    for e in r["erroneos"]:
        agregar("")
        agregar("%s (falló en: %s)" % (e["remito"].get("nro_remito", "<sin número>"), e["etapa"]))
        for c in e["causas"]:
            agregar("  - " + c)
        agregar(json.dumps(e["remito"], ensure_ascii=False, indent=2))

    CARPETA_REPORTES.mkdir(exist_ok=True)
    ruta = ruta_reporte(r["batch_id"], ahora)
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return ruta
