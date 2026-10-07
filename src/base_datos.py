"""Base de datos: creacion de app.db y registro de envios."""
import sqlite3
import sys

from .constantes import CARPETA_SQL, PROVINCES, SQLITE_VERSION_MINIMA


def verificar_version_sqlite():
    """Termina con un mensaje claro si la SQLite de Python es demasiado vieja."""
    if sqlite3.sqlite_version_info < SQLITE_VERSION_MINIMA:
        sys.exit("Se necesita SQLite %s o posterior y esta instalación de Python trae la %s. "
                 "Usá un Python más nuevo (por ejemplo, el de python.org)."
                 % (".".join(map(str, SQLITE_VERSION_MINIMA)), sqlite3.sqlite_version))


def sql_de_tabla(tabla):
    """DDL de sql/<tabla>.sql, con {provincias} reemplazado por la lista de PROVINCES."""
    sql = (CARPETA_SQL / (tabla + ".sql")).read_text(encoding="utf-8")
    # Literales SQL: comillas simples, escapando las internas duplicandolas.
    provincias = ", ".join("'%s'" % p.replace("'", "''") for p in PROVINCES)
    return sql.replace("{provincias}", provincias)


def abrir_db(ruta):
    """Abre app.db (la crea si no existe) y crea las tablas que falten."""
    verificar_version_sqlite()  # antes de conectar, para no dejar un app.db vacio
    db = sqlite3.connect(ruta)
    db.execute("PRAGMA foreign_keys = ON")
    existentes = {fila[0] for fila in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    for tabla in ("batches", "shipments"):  # batches primero: shipments la referencia
        if tabla not in existentes:
            db.executescript(sql_de_tabla(tabla))
    return db


def esta_registrado(db, external_ref):
    return db.execute("SELECT 1 FROM shipments WHERE external_ref = ?", (external_ref,)).fetchone() is not None


def insertar_envio(db, payload, tracking_id, batch_id):
    """Inserta el envio; devuelve False si ya estaba (no lo pisa)."""
    r = payload["recipient"]
    cursor = db.execute(
        """INSERT INTO shipments (external_ref, tracking_id, batch_id,
               recipient_name, recipient_street, recipient_city, recipient_province,
               recipient_zip_code, recipient_phone, packages, weight_kg, declared_value, service)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(external_ref) DO NOTHING""",
        (payload["external_ref"], tracking_id, batch_id,
         r["name"], r["street"], r["city"], r["province"], r["zip_code"], r.get("phone"),
         payload["packages"], payload["weight_kg"], payload.get("declared_value"), payload["service"]))
    return cursor.rowcount == 1
