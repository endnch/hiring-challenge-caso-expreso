schema = {
    "type": "object",
    "properties": {
        "nro_remito": {"type": "string"},
        "fecha_remito": {"type": "string"},
        "cliente": {"type": "string"},
        "destinatario": {
            "type": "object",
            "properties": {
                "razon_social": {"type": "string"},
                "direccion": {"type": "string", "pattern": "\\S"},
                "localidad": {"type": "string"},
                "provincia": {"type": "string"},
                "codigo_postal": {"type": "string", "minLength": 4, "maxLength": 4},
                "telefono": {"type": "string"},

            },
            "required": ["razon_social", "direccion", "localidad", "provincia", "codigo_postal", "telefono"]
        },
        "bultos": {"type": "integer", "minimum": 1},
        "peso_kg": {"anyOf": [{"type": "number"}, {"type": "string", "pattern": "^\\d+,\\d+$"}]},
        "volumen_m3": {"type": "number"},
        "valor_declarado": {"type": "number"},
        "transportista": {"type": "string"},
        "servicio": {"type": "string", "enum": ["NORMAL", "URGENTE"]},
        "observaciones": {"type": "string"}
    },
    "required": ["nro_remito", "fecha_remito", "cliente", "destinatario", "bultos", "peso_kg", "volumen_m3", "valor_declarado", "transportista", "servicio", "observaciones"]
}