"""Funciones compartidas para filtrar remitos y describir errores de validacion."""
from .constantes import TRANSPORTISTA


def normalizar_transportista(nombre):
    """Lleva las variantes del export a una forma comun.

    En el archivo aparecen "EXPRESO ANDINO", "Expreso Andino", "expreso andino",
    "EXPRESO ANDINO " (con espacio al final) y "Exp. Andino".
    """
    nombre = nombre.lower().replace("exp.", "expreso")
    return " ".join(nombre.split())  # saca espacios sobrantes


def es_expreso_andino(remito):
    return normalizar_transportista(remito.get("transportista", "")) == TRANSPORTISTA


def campo(error):
    """Ruta del campo con error, por ejemplo "destinatario.codigo_postal"."""
    return ".".join(str(p) for p in error.absolute_path) or "(remito)"


def causa(error):
    """Traduce el error de jsonschema a un mensaje en castellano."""
    tipo = error.validator
    regla = error.validator_value
    valor = repr(error.instance)
    if tipo == "required":
        # jsonschema genera un error por cada campo faltante, con el mensaje
        # "'cliente' is a required property"; el nombre es el primer texto entre comillas.
        faltante = error.message.split("'")[1] if "'" in error.message else error.message
        return "falta el campo obligatorio '%s'" % faltante
    if tipo == "type":
        return "%s no es del tipo esperado (%s)" % (valor, regla)
    if tipo == "minimum":
        return "%s es menor que el mínimo permitido (%s)" % (valor, regla)
    if tipo == "exclusiveMinimum":
        return "%s debe ser mayor que %s" % (valor, regla)
    if tipo == "minLength":
        return "%s tiene menos de %s caracteres" % (valor, regla)
    if tipo == "maxLength":
        return "%s tiene más de %s caracteres" % (valor, regla)
    if tipo == "pattern":
        if regla == "\\S":
            return "%s está vacío o tiene solo espacios" % valor
        return "%s no cumple el formato %s" % (valor, regla)
    if tipo == "enum":
        return "%s no es un valor permitido (%s)" % (valor, ", ".join(regla))
    if tipo == "anyOf":
        return "%s no tiene un formato válido" % valor
    return error.message  # cualquier otra regla: mensaje original de jsonschema


def errores_de(validador, documento):
    """Lista de "campo: causa" para un documento; vacia si es valido."""
    errores = sorted(validador.iter_errors(documento), key=campo)
    return ["%s: %s" % (campo(e), causa(e)) for e in errores]
