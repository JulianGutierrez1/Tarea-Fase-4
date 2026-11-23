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

# SERVICIOS
IVA = 0.19  # impuesto por defecto


class Servicio(EntidadBase):
    """Servicio abstracto: define el contrato que deben cumplir los hijos."""

    def __init__(self, nombre, tarifa_base):
        super().__init__()
        if not nombre or not str(nombre).strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        # Se valida que la tarifa sea numérica y positiva
        if not isinstance(tarifa_base, (int, float)) or isinstance(tarifa_base, bool):
            raise ServicioInvalidoError(f"Tarifa no numérica: {tarifa_base!r}.")
        if tarifa_base <= 0:
            raise ServicioInvalidoError("La tarifa base debe ser mayor que cero.")
        self._nombre = str(nombre).strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = True  # por defecto el servicio está disponible

    # - propiedades de solo lectura / controladas
    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool):
        self._disponible = bool(valor)

    # - metodos abstractos (deben sobrescribirse
    @abstractmethod
    def calcular_costo(self, horas: float) -> float:
        """Costo base del servicio para una duración dada."""

    @abstractmethod
    def validar_parametros(self, horas: float) -> None:
        """Valida los parámetros de uso propios de cada servicio."""

    # - método sobrecargado mediante parametros opcionales
    def calcular_costo_total(self, horas, impuesto=IVA, descuento=0.0):
        """Variantes de cálculo (Python no tiene sobrecarga nativa):

        calcular_costo_total(2)                   -> costo + IVA 19 %
        calcular_costo_total(2, 0.0)              -> costo sin impuesto
        calcular_costo_total(2, 0.19, 0.10)       -> costo + IVA - 10 % descuento
        """
        self.validar_parametros(horas)
        if not 0 <= impuesto <= 1 or not 0 <= descuento < 1:
            raise CalculoInconsistenteError(
                f"Impuesto ({impuesto}) o descuento ({descuento}) fuera de rango."
            )
        base = self.calcular_costo(horas)
        total = base * (1 - descuento) * (1 + impuesto)
        if total <= 0:
            raise CalculoInconsistenteError("El costo total calculado no es positivo.")
        return round(total, 2)

    def __str__(self) -> str:
        return self.describir()


class ReservaSala(Servicio):
    """Reserva de salas: tarifa por hora y límite de capacidad."""

    def __init__(self, nombre, tarifa_hora, capacidad):
        super().__init__(nombre, tarifa_hora)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}.")
        self._capacidad = capacidad

    def validar_parametros(self, horas):
        # Las salas se reservan entre 1 y 12 horas
        if not isinstance(horas, (int, float)) or not 1 <= horas <= 12:
            raise ServicioInvalidoError(f"Horas inválidas para sala: {horas!r} (1-12).")

    def calcular_costo(self, horas):
        return self.tarifa_base * horas

    def describir(self):
        return (f"Sala '{self.nombre}' - capacidad {self._capacidad} personas - "
                f"${self.tarifa_base:,.0f}/hora")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos: tarifa por hora más un cargo fijo de seguro."""

    def __init__(self, nombre, tarifa_hora, seguro=0.0):
        super().__init__(nombre, tarifa_hora)
        if not isinstance(seguro, (int, float)) or seguro < 0:
            raise ServicioInvalidoError(f"Valor de seguro inválido: {seguro!r}.")
        self._seguro = float(seguro)

    def validar_parametros(self, horas):
        # Los equipos se alquilan entre 1 y 72 horas
        if not isinstance(horas, (int, float)) or not 1 <= horas <= 72:
            raise ServicioInvalidoError(f"Horas inválidas para equipo: {horas!r} (1-72).")

    def calcular_costo(self, horas):
        return self.tarifa_base * horas + self._seguro

    def describir(self):
        return (f"Equipo '{self.nombre}' - ${self.tarifa_base:,.0f}/hora "
                f"+ seguro ${self._seguro:,.0f}")


class AsesoriaEspecializada(Servicio):
    """Asesoría: la tarifa se multiplica según el nivel del asesor."""

    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, nivel="junior"):
        super().__init__(nombre, tarifa_hora)
        if str(nivel).lower() not in self.NIVELES:
            raise ServicioInvalidoError(f"Nivel de asesor inválido: {nivel!r}.")
        self._nivel = str(nivel).lower()

    def validar_parametros(self, horas):
        # Las asesorías duran entre 1 y 8 horas
        if not isinstance(horas, (int, float)) or not 1 <= horas <= 8:
            raise ServicioInvalidoError(f"Horas inválidas para asesoría: {horas!r} (1-8).")

    def calcular_costo(self, horas):
        return self.tarifa_base * self.NIVELES[self._nivel] * horas

    def describir(self):
        return (f"Asesoría '{self.nombre}' - nivel {self._nivel} - "
                f"${self.tarifa_base:,.0f}/hora base")

# RESERVA 
class EstadoReserva(Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    PROCESADA = "procesada"


class Reserva(EntidadBase):
    def __init__(self, cliente, servicio, horas):
        super().__init__()
        # Validacion de tipos de los objetos asociados
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"'{servicio.nombre}' no está disponible.")
        # try/except/else: se validan las horas con las reglas del servicio
        try:
            servicio.validar_parametros(horas)
        except ServicioInvalidoError as error:
            # Encadenamiento de excepciones: se conserva la causa original
            raise ReservaInvalidaError("No se pudo crear la reserva.") from error
        else:
            log.info("Parámetros de reserva válidos para %s", servicio.nombre)
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = EstadoReserva.PENDIENTE

    @property
    def estado(self):
        return self._estado

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    def confirmar(self):
        """PENDIENTE -> CONFIRMADA."""
        if self._estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva en estado {self._estado.value}."
            )
        self._estado = EstadoReserva.CONFIRMADA
        log.info("Reserva #%s confirmada", self.id)

    def cancelar(self):
        """Se puede cancelar si está PENDIENTE o CONFIRMADA."""
        if self._estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva {self._estado.value}."
            )
        self._estado = EstadoReserva.CANCELADA
        log.info("Reserva #%s cancelada", self.id)

    def procesar(self, impuesto=0.19, descuento=0.0):
        """CONFIRMADA -> PROCESADA; devuelve el costo total."""
        try:
            if self._estado is not EstadoReserva.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    "Solo se procesan reservas confirmadas "
                    f"(estado actual: {self._estado.value})."
                )
            total = self._servicio.calcular_costo_total(self._horas, impuesto, descuento)
        except ErrorSoftwareFJ as error:
            log.error("Fallo al procesar reserva #%s: %s", self.id, error)
            raise  # se ejecuta denuevo para que el llamador decida
        else:
            self._estado = EstadoReserva.PROCESADA
            log.info("Reserva #%s procesada. Total: %s", self.id, total)
            return total
        finally:
            # Se ejecuta siempre, haya o no error
            log.info("Intento de procesamiento finalizado para reserva #%s", self.id)

    def describir(self):
        return (f"Reserva #{self.id} | {self._cliente.nombre} | "
                f"{self._servicio.nombre} | {self._horas} h | {self._estado.value}")

    def __str__(self):
        return self.describir()
