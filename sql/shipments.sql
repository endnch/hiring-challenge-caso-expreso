-- Tabla de envios basada en schema_api.py (payload de POST /v1/shipments).
-- El objeto "recipient" se aplana en columnas recipient_*.
-- STRICT (SQLite >= 3.37) hace que se respeten los tipos, igual que "type" en el schema.

CREATE TABLE shipments (
    -- external_ref: string no vacio y unico (la API no admite dos envios con la misma referencia)
    external_ref         TEXT    NOT NULL PRIMARY KEY
                         CHECK (trim(external_ref, ' ' || char(9, 10, 11, 12, 13)) <> ''),

    -- tracking_id: lo asigna la API (respuesta 201, o 409 si el envio ya existia).
    -- Queda NULL hasta que el envio se confirma; UNIQUE admite varios NULL en SQLite.
    tracking_id          TEXT    UNIQUE
                         CHECK (trim(tracking_id, ' ' || char(9, 10, 11, 12, 13)) <> ''),

    -- batch que creo el envio (1 batch -> N shipments). NULL para envios que ya
    -- existian en la API (409 en el primer intento) y solo se registraron en esta base.
    -- SQLite solo aplica la FK con PRAGMA foreign_keys = ON en cada conexion.
    batch_id             INTEGER REFERENCES batches(id),

    -- recipient.* (todos obligatorios salvo phone)
    -- trim(..., ' ' || char(9,10,11,12,13)) <> '' equivale a "pattern": "\\S":
    -- al menos un caracter que no sea espacio, tab o salto de linea.
    recipient_name       TEXT    NOT NULL CHECK (trim(recipient_name, ' ' || char(9, 10, 11, 12, 13)) <> ''),
    recipient_street     TEXT    NOT NULL CHECK (trim(recipient_street, ' ' || char(9, 10, 11, 12, 13)) <> ''),
    recipient_city       TEXT    NOT NULL CHECK (trim(recipient_city, ' ' || char(9, 10, 11, 12, 13)) <> ''),
    recipient_province   TEXT    NOT NULL CHECK (recipient_province IN (
                             'Buenos Aires', 'Ciudad Autónoma de Buenos Aires', 'Catamarca', 'Chaco', 'Chubut',
                             'Córdoba', 'Corrientes', 'Entre Ríos', 'Formosa', 'Jujuy', 'La Pampa', 'La Rioja',
                             'Mendoza', 'Misiones', 'Neuquén', 'Río Negro', 'Salta', 'San Juan', 'San Luis',
                             'Santa Cruz', 'Santa Fe', 'Santiago del Estero', 'Tierra del Fuego', 'Tucumán')),
    recipient_zip_code   TEXT    NOT NULL CHECK (trim(recipient_zip_code, ' ' || char(9, 10, 11, 12, 13)) <> ''),
    recipient_phone      TEXT,

    packages             INTEGER NOT NULL CHECK (packages >= 1),
    weight_kg            REAL    NOT NULL CHECK (weight_kg > 0),
    declared_value       REAL             CHECK (declared_value >= 0),  -- opcional (NULL permitido)
    service              TEXT    NOT NULL CHECK (service IN ('standard', 'express'))
) STRICT;

-- Para buscar rapido los envios de una batch.
CREATE INDEX shipments_batch_id ON shipments(batch_id);
