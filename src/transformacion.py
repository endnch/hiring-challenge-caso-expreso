"""Transformacion remito -> payload de la API."""
from .constantes import PROVINCES, PROVINCIAS, SERVICIOS


def transformar(remito, observaciones):
    d = remito["destinatario"]
    ref = remito["nro_remito"]

    provincia = d["provincia"].strip()
    if provincia not in PROVINCES and provincia in PROVINCIAS:
        observaciones.append("%s: provincia '%s' convertida a '%s'" % (ref, d["provincia"], PROVINCIAS[provincia]))
        provincia = PROVINCIAS[provincia]

    peso = remito["peso_kg"]
    if isinstance(peso, str):  # el schema de entrada garantiza el formato "145,1"
        observaciones.append("%s: peso '%s' convertido a %s" % (ref, peso, peso.replace(",", ".")))
        peso = float(peso.replace(",", "."))

    payload = {
        "external_ref": ref,
        "recipient": {
            "name": d["razon_social"],
            "street": d["direccion"],
            "city": d["localidad"],
            "province": provincia,
            "zip_code": d["codigo_postal"],
        },
        "packages": remito["bultos"],
        "weight_kg": peso,
        "declared_value": remito["valor_declarado"],
        "service": SERVICIOS[remito["servicio"]],
    }
    if d["telefono"].strip():
        payload["recipient"]["phone"] = d["telefono"]
    return payload
