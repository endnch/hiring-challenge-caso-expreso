"""Aquí es donde sucede la magia.

Flujo de carga: filtrar, deduplicar, validar, transformar, subir y registrar."""
import json

from jsonschema import Draft202012Validator

from .base_datos import abrir_db, esta_registrado, insertar_envio
from .constantes import RUTA_DB
from .schemas.schema import schema as SCHEMA_REMITO
from .schemas.schema_api import schema as SCHEMA_API
from .subida import Tipo, subir
from .transformacion import transformar
from .validacion import errores_de, es_expreso_andino


def procesar(config, archivo):
    with open(archivo, encoding="utf-8") as f:
        remitos = json.load(f)

    resultado = {"archivo": str(archivo), "total": len(remitos), "filtrados": [], "duplicados": [],
                 "nuevos": [], "recuperados": [], "ya_registrados": [], "observaciones": [],
                 "erroneos": [], "batch_id": None}

    # 1. Filtrar
    andino = []

    for remito in remitos:
        (andino if es_expreso_andino(remito) else resultado["filtrados"]).append(remito)

    resultado["total_andino"] = len(andino)

    # 2. Deduplicar por numero de remito
    vistos = set()
    unicos = []

    for remito in andino:
        ref = remito.get("nro_remito")

        if ref in vistos:
            resultado["duplicados"].append(ref)
            resultado["observaciones"].append("%s: aparece repetido en el archivo; se procesó solo la primera aparición" % ref)
            continue

        vistos.add(ref)
        unicos.append(remito)

    # 3 y 4. Validar y transformar
    validador_remito = Draft202012Validator(SCHEMA_REMITO)
    validador_api = Draft202012Validator(SCHEMA_API)
    a_subir = []

    for remito in unicos:
        causas = errores_de(validador_remito, remito)

        if causas:
            resultado["erroneos"].append({"remito": remito, "etapa": "validación del remito", "causas": causas})
            continue

        payload = transformar(remito, resultado["observaciones"])
        causas = errores_de(validador_api, payload)

        if causas:
            resultado["erroneos"].append({"remito": remito, "etapa": "transformación al formato de la API", "causas": causas})
            continue

        a_subir.append((remito, payload))

    # 5 a 7. Subir y registrar
    db = abrir_db(RUTA_DB)
    try:
        for remito, payload in a_subir:
            ref = payload["external_ref"]

            if esta_registrado(db, ref):
                resultado["ya_registrados"].append(ref)
                continue

            # No confundir con "resultado", el resumen de toda la corrida.
            respuesta = subir(config, payload)

            if respuesta["fallos"]:
                resultado["observaciones"].append("%s: %d intento(s) fallido(s) antes de la respuesta final (%s)" % (
                    ref, len(respuesta["fallos"]), ", ".join(str(x) for x in respuesta["fallos"])))

            if respuesta["tipo"] is Tipo.ERROR:
                resultado["erroneos"].append({"remito": remito, "etapa": "envío a la API", "causas": [respuesta["detalle"]]})
                continue

            if respuesta["tipo"] is Tipo.NUEVO:
                # La batch se crea con el primer envio nuevo, en la misma transaccion.
                batch_creada_ahora = resultado["batch_id"] is None

                if batch_creada_ahora:
                    resultado["batch_id"] = db.execute("INSERT INTO batches DEFAULT VALUES").lastrowid

                if insertar_envio(db, payload, respuesta["tracking_id"], resultado["batch_id"]):
                    db.commit()

                    resultado["nuevos"].append((ref, respuesta["tracking_id"]))

                    if respuesta["creado_en_fallo"]:
                        resultado["observaciones"].append("%s: la API respondió error pero el envío se había creado "
                                                          "(lo confirmó un 409 al reintentar); se registró en la batch "
                                                          "actual" % ref)
                else:
                    db.rollback()

                    if batch_creada_ahora:
                        resultado["batch_id"] = None

                    resultado["ya_registrados"].append(ref)

            else:  # Tipo.RECUPERADO
                if insertar_envio(db, payload, respuesta["tracking_id"], None):
                    resultado["recuperados"].append((ref, respuesta["tracking_id"]))
                else:
                    resultado["ya_registrados"].append(ref)
                db.commit()
    finally:
        db.close()

    return resultado
