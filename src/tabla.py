"""Impresion de tablas de ancho fijo en la consola.

Cada columna se define una sola vez como (titulo, ancho, alineacion); el formato de
las filas, el recorte de valores largos y el largo del separador salen de ahi.
"""
IZQUIERDA = "<"
DERECHA = ">"


def imprimir_tabla(columnas, filas):
    """columnas: lista de (titulo, ancho, IZQUIERDA | DERECHA). Recorta los valores al ancho."""
    # "{:<24.24}": alinea y rellena hasta el ancho, y recorta lo que lo exceda.
    formato = " ".join("{:%s%d.%d}" % (alineacion, ancho, ancho) for _, ancho, alineacion in columnas)
    separador = "-" * len(formato.format(*("" for _ in columnas)))
    print(formato.format(*(titulo for titulo, _, _ in columnas)))
    print(separador)
    for fila in filas:
        print(formato.format(*(str(valor) for valor in fila)))
    print(separador)
