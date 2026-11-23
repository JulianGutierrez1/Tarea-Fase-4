# Julian David Gutierrez Salinas  
# 561
# Ingenieria de sistemas
# Codigo fuente: autoria propia

from abc import ABC, abstractmethod
from enum import Enum
import itertools, logging, os, re


# Excepciones
class ErrorSoftwareFJ(Exception):
    """Excepción base: todas las excepciones del sistema heredan de ella."""

    def __init__(self, mensaje: str):
        # Se guarda el mensaje para poder registrarlo en el log
        super().__init__(mensaje)
        self.mensaje = mensaje

class ClienteInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando los datos de un cliente no cumplen las validaciones."""

class ServicioInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando los parámetros de un servicio son incorrectos."""
  
class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta reservar un servicio no disponible."""

class ParametroFaltanteError(ErrorSoftwareFJ):
    """Se lanza cuando falta un parámetro obligatorio."""

class ReservaInvalidaError(ErrorSoftwareFJ):
    """Se lanza cuando una reserva no puede crearse con los datos dados."""

class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Se lanza al intentar una transición de estado no permitida."""

class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Se lanza cuando un cálculo de costos produce un valor incoherente."""

# LOGGER
# Carpeta y archivo donde se guardan los eventos y errores
RUTA_LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
ARCHIVO_LOG = os.path.join(RUTA_LOGS, "software_fj.log")


def obtener_logger() -> logging.Logger:
    """Devuelve el logger del sistema, creándolo una sola vez."""
    os.makedirs(RUTA_LOGS, exist_ok=True)  # crea la carpeta si no existe
    logger = logging.getLogger("software_fj")
    if not logger.handlers:  # evita duplicar manejadores
        logger.setLevel(logging.INFO)
        manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
        manejador.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
        )
        logger.addHandler(manejador)
    return logger


# Instancia compartida por todos los módulos
log = obtener_logger()

# ENTIDADES
class EntidadBase(ABC):
    """Toda entidad (cliente, servicio, reserva) tiene un id y se describe."""

    _contador = itertools.count(1)  # generador de identificadores únicos

    def __init__(self):
        # Atributo "protegido": el id se asigna automáticamente
        self._id = next(EntidadBase._contador)

    @property
    def id(self) -> int:
        """Identificador de solo lectura (encapsulación)."""
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Cada entidad debe ofrecer una descripción legible."""

#   CLIENTE 
# Expresión regular simple para validar correos electrónicos
_PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


class Cliente(EntidadBase):
    """Cliente de Software FJ. Sus datos son privados y se validan al asignarse."""

    def __init__(self, nombre=None, documento=None, correo=None, telefono=None):
        super().__init__()  # se asigna el id
        # Se usan los setters (propiedades) para que siempre se valide
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono

    # - nombre
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El nombre del cliente es obligatorio.")
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ClienteInvalidoError(f"Nombre inválido: {valor!r}.")
        self.__nombre = valor.strip()

    # - documentoo
    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El documento del cliente es obligatorio.")
        valor = str(valor).strip()
        if not valor.isdigit() or not (6 <= len(valor) <= 12):
            raise ClienteInvalidoError(
                f"Documento inválido: {valor!r} (solo dígitos, 6 a 12)."
            )
        self.__documento = valor

    # -correo
    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El correo del cliente es obligatorio.")
        if not _PATRON_CORREO.match(str(valor).strip()):
            raise ClienteInvalidoError(f"Correo con formato inválido: {valor!r}.")
        self.__correo = str(valor).strip().lower()

    # -teléfono
    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El teléfono del cliente es obligatorio.")
        valor = str(valor).strip()
        if not valor.isdigit() or not (7 <= len(valor) <= 10):
            raise ClienteInvalidoError(f"Teléfono inválido: {valor!r}.")
        self.__telefono = valor

    def describir(self) -> str:
        """Descripción del cliente (implementa el método abstracto)."""
        return f"Cliente #{self.id}: {self.nombre} (doc. {self.documento}, {self.correo})"

    def __str__(self) -> str:
        return self.describir()
