# Cómo correrlo

En macOS y Linux, usar `python3` donde dice `python`.

## 1. Requisitos

- Python 3.9 o posterior (probado con 3.14): `python --version`
- SQLite 3.37 o posterior, la que trae Python:

  ```
  python -c "import sqlite3; print(sqlite3.sqlite_version)"
  ```

  Los instaladores de python.org la incluyen; algunas distribuciones de Linux traen una más vieja
  (Ubuntu 20.04, Debian 11). En ese caso, instalar un Python más nuevo.

## 2. Instalar las dependencias

Desde la carpeta del proyecto, idealmente en un entorno virtual:

```
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

## 3. Configurar la API key

`.env` no se versiona: se crea a partir del ejemplo.

```
copy .env.example .env          # Windows
cp .env.example .env            # macOS / Linux
```

Completar `EXPRESO_API_KEY` en `.env` (la de la API de prueba está en `api/API.md`).
`EXPRESO_API_URL` ya viene con `http://127.0.0.1:8000`. Las variables de entorno con el
mismo nombre tienen prioridad sobre `.env`.

## 4. Levantar la API de prueba

En otra terminal, desde la carpeta del proyecto:

```
python api/expreso_api.py
```

Queda escuchando en `http://127.0.0.1:8000`. Guarda los datos en memoria: si se reinicia, arranca vacía.

## 5. Correr el programa

```
python main.py
```

Muestra un resumen y genera:

- `app.db`: envíos registrados y batches.
- `reportes/reporte_batch_<id>_<fecha>Z.txt` (o `reporte_sin_batch_<fecha>Z.txt` si no hubo
  envíos nuevos). Las fechas están en UTC.

Otras opciones:

```
python main.py otro_archivo.json                     # otro export de remitos
python main.py --api-url http://otra-url:8000        # otra API, sin editar .env
python main.py --list-delayed                        # no entregados con fecha estimada < 2026-10-03
python main.py --list-delayed --before 2026-10-07    # con otra fecha de corte
python main.py --help
```

## Problemas frecuentes

| Mensaje | Qué hacer |
|---|---|
| `Falta EXPRESO_API_KEY` | Crear y completar `.env` (paso 3). |
| `API key inválida` | Revisar `EXPRESO_API_KEY` en `.env` o en el entorno. |
| Remitos en "no enviados por fallas de la API" en el reporte | Levantar la API (paso 4) o revisar `EXPRESO_API_URL` y volver a correr: se reintentan solos. |
| `Ya hay otra ejecución en curso` | Si no hay otra corrida, el programa terminó a la fuerza: borrar `app.db.lock`. |
| `Se necesita SQLite 3.37…` | Instalar un Python más nuevo (paso 1). |

Para empezar de cero: borrar `app.db` y `reportes/` **y reiniciar la API**. Si la API no se
reinicia, recuerda los envíos y vuelven como "recuperados".

# Que supuestos tomé
- 🐍 Tiene que estar escrito en Python y no otro lenguaje de programación.
- ⛰️ En esta prueba solo importan los remitos de Expreso Andino ya que se trabaja sobre su API.
- ✖️ Los remitos incompletos son rechazados y marcados explícitamente en el reporte final.
- ⚙️ Que funcione y sea robusto tiene mayor prioridad a la presentación.
- 📄 El programa genera un archivo que es un resumen de una corrida contra la API.
- ✖️ Los datos en el JSON pueden contener errores y estar incompletos.
- 🧱 La API no tiene rate limiting a diferencia de una API real.
- ⚖️ Cuando el campo peso_kg en un remito es de piso texto el separador de decimales siempre es una coma.
- 📫 Un remito sin código postal es rechazado.
- ✅ El programa aspira a validar los remitos de tal forma que no sean rechazados por la API.
- 5️⃣ Como número de reintentos máximo elegí 5.

# Que cambiaría o agregaría para usarlo en producción todos los días
- 📋 Agregar linting y formatting automatico.
- 🤖 Integrar IA para que verifique que los detalles que presente un remito caigan dentro de los casos que el programa maneja y si no lo hace anotarlo para así continuamente mejorar el programa y hacerlo más robusto.
- ⚙️ Sistema de CI/CD.
- ✅ Agregarle pruebas unitarias y end-to-end.
- 🔠 Ejemplo de una prueba: Probar que el programa acentúa las provincias escritas sin acento.
- 🚩 Agregarle un chequeo que haga "flag" de las combinaciones de peso, bultos y volumen poco creíbles.
- 🖼️ Mejorar interfaz de usuario.
- ❓ Analizar otros casos especiales que ocurren con otros transportistas y no solo Expreso Andino.
- 🧱 Tomar en cuenta el rate limiting de una API real.