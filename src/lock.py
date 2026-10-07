"""Lock: evita dos ejecuciones simultaneas sobre la misma app.db."""
import os
import sys
from contextlib import contextmanager


@contextmanager
def lock_exclusivo(ruta):
    try:
        fd = os.open(ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        sys.exit("Ya hay otra ejecución en curso (existe %s). Si no hay ninguna, "
                 "borrá ese archivo y volvé a intentar." % ruta.name)
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        os.remove(ruta)
