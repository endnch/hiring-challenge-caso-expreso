PROVINCES = [
    "Buenos Aires", "Ciudad Autónoma de Buenos Aires", "Catamarca", "Chaco", "Chubut",
    "Córdoba", "Corrientes", "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza",
    "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe",
    "Santiago del Estero", "Tierra del Fuego", "Tucumán",
]

schema = {
    "type": "object",
    "properties": {
        "external_ref": {"type": "string", "pattern": "\\S"},
        "recipient": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "pattern": "\\S"},
                "street": {"type": "string", "pattern": "\\S"},
                "city": {"type": "string", "pattern": "\\S"},
                "province": {"type": "string", "enum": PROVINCES},
                "zip_code": {"type": "string", "pattern": "\\S"},
                "phone": {"type": "string"},

            },
            "required": ["name", "street", "city", "province", "zip_code"]
        },
        "packages": {"type": "integer", "minimum": 1},
        "weight_kg": {"type": "number", "exclusiveMinimum": 0},
        "declared_value": {"type": "number", "minimum": 0},
        "service": {"type": "string", "enum": ["standard", "express"]},
    },
    "required": ["external_ref", "recipient", "packages", "weight_kg", "service"]
}