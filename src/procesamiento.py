"""Flujo de carga: filtrar, deduplicar, validar, transformar, subir y registrar."""
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

    r = {"archivo": str(archivo), "total": len(remitos), "filtrados": [], "duplicados": [],
         "nuevos": [], "recuperados": [], "ya_registrados": [], "observaciones": [],
         "erroneos": [], "batch_id": None}

    # 1. Filtrar
    andino = []
    for remito in remitos:
        (andino if es_expreso_andino(remito) else r["filtrados"]).append(remito)
    r["total_andino"] = len(andino)

    # 2. Deduplicar por numero de remito
    vistos, unicos = set(), []
    for remito in andino:
        ref = remito.get("nro_remito")
        if ref in vistos:
            r["duplicados"].append(ref)
            r["observaciones"].append("%s: aparece repetido en el archivo; se procesó solo la primera aparición" % ref)
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
            r["erroneos"].append({"remito": remito, "etapa": "validación del remito", "causas": causas})
            continue
        payload = transformar(remito, r["observaciones"])
        causas = errores_de(validador_api, payload)
        if causas:
            r["erroneos"].append({"remito": remito, "etapa": "transformación al formato de la API", "causas": causas})
            continue
        a_subir.append((remito, payload))

    # 5 a 7. Subir y registrar
    db = abrir_db(RUTA_DB)
    try:
        for remito, payload in a_subir:
            ref = payload["external_ref"]
            if esta_registrado(db, ref):
                r["ya_registrados"].append(ref)
                continue

            resultado = subir(config, payload)
            if resultado["fallos"]:
                r["observaciones"].append("%s: %d intento(s) fallido(s) antes de la respuesta final (%s)" % (
                    ref, len(resultado["fallos"]), ", ".join(str(x) for x in resultado["fallos"])))

            if resultado["tipo"] is Tipo.ERROR:
                r["erroneos"].append({"remito": remito, "etapa": "envío a la API", "causas": [resultado["detalle"]]})
                continue

            if resultado["tipo"] is Tipo.NUEVO:
                # La batch se crea con el primer envio nuevo, en la misma transaccion.
                batch_creada_ahora = r["batch_id"] is None
                if batch_creada_ahora:
                    r["batch_id"] = db.execute("INSERT INTO batches DEFAULT VALUES").lastrowid
                if insertar_envio(db, payload, resultado["tracking_id"], r["batch_id"]):
                    db.commit()
                    r["nuevos"].append((ref, resultado["tracking_id"]))
                    if resultado["creado_en_fallo"]:
                        r["observaciones"].append("%s: la API respondió error pero el envío se había creado "
                                                  "(lo confirmó un 409 al reintentar); se registró en la batch "
                                                  "actual" % ref)
                else:
                    db.rollback()
                    if batch_creada_ahora:
                        r["batch_id"] = None
                    r["ya_registrados"].append(ref)
            else:  # Tipo.RECUPERADO
                if insertar_envio(db, payload, resultado["tracking_id"], None):
                    r["recuperados"].append((ref, resultado["tracking_id"]))
                else:
                    r["ya_registrados"].append(ref)
                db.commit()
    finally:
        db.close()

    return r
