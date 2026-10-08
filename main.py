#!/usr/bin/env python3
"""Carga los remitos de Expreso Andino en la API y los registra en app.db.

Uso:
  python main.py [archivo.json] [--api-url URL]
  python main.py --list-delayed [--before AAAA-MM-DD]

Pasos: filtra los remitos de Expreso Andino, los valida (src/schemas/schema.py), los
transforma al payload de la API (src/schemas/schema_api.py), los sube con reintentos,
guarda lo creado en app.db (una batch por corrida con envios nuevos) y escribe un
reporte en reportes/.

Configuracion (API key y URL): ver src/config.py y .env.example.

Modulos en src/: argumentos.py (flags), procesamiento.py (flujo completo),
transformacion.py, subida.py, base_datos.py, reporte.py, lock.py.
"""
import datetime
import sys

from src.api import ApiKeyInvalida
from src.argumentos import parsear_argumentos
from src.config import obtener_config
from src.constantes import RUTA_DB, RUTA_LOCK
from src.list_delayed import listar_demorados
from src.lock import lock_exclusivo
from src.procesamiento import procesar
from src.reporte import escribir_reporte


def main():
    # Tildes correctas en la consola de Windows (stderr incluido: ahi van los sys.exit).
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    args = parsear_argumentos()
    config = obtener_config(args.api_url)

    try:
        if args.list_delayed:
            listar_demorados(config, RUTA_DB, args.before)
            return

        with lock_exclusivo(RUTA_LOCK):
            resultado = procesar(config, args.archivo)
            # En UTC, igual que batches.created_at (CURRENT_TIMESTAMP de SQLite).
            ruta = escribir_reporte(resultado, datetime.datetime.now(datetime.timezone.utc))
    except ApiKeyInvalida as e:
        sys.exit(str(e))

    if resultado["batch_id"]:
        print("Batch %d: %d envíos nuevos." % (resultado["batch_id"], len(resultado["nuevos"])))
    else:
        print("No se realizaron operaciones: no se creó ningún envío nuevo ni un nuevo batch.")
    print("Recuperados: %d | Ya registrados: %d | No enviados (fallas de la API): %d | Erróneos: %d" % (
        len(resultado["recuperados"]), len(resultado["ya_registrados"]), len(resultado["no_enviados"]),
        len(resultado["erroneos"])))
    print("Reporte: %s" % ruta)


if __name__ == "__main__":
    main()
