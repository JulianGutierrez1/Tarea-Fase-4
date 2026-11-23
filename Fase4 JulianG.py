# Julian David Gutierrez Salinas  
# 561
# Ingenieria de sistemas
# Codigo fuente: autoria propia

from abc import ABC, abstractmethod
from enum import Enum
import itertools, logging, os, re


# EXCEPCIONES
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
