"""Schemas F3 (SPEC 006): validación pydantic v2 para tool args y submit."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _check_email(v: str, field: str) -> str:
    if not _EMAIL_RE.match(v or ""):
        raise ValueError(f"{field}_invalido")
    return v


class JiraArgs(BaseModel):
    proyecto: str = Field(min_length=1)
    titulo: str = Field(min_length=1, max_length=120)
    descripcion: str = Field(min_length=20)
    prioridad: Literal["Lowest", "Low", "Medium", "High", "Highest"]
    email_reporter: str = Field(min_length=3)
    etiquetas: list[str] = Field(default_factory=list)

    @field_validator("email_reporter")
    @classmethod
    def _email_ok(cls, v: str) -> str:
        return _check_email(v, "email_reporter")


class GcalArgs(BaseModel):
    titulo: str = Field(min_length=1)
    fecha_inicio: datetime
    duracion_minutos: Literal[30, 45, 60, 90]
    asistentes: list[str] = Field(min_length=1)
    zona_horaria: str = "America/Lima"
    descripcion: str | None = None

    @field_validator("asistentes")
    @classmethod
    def _asistentes_ok(cls, v: list[str]) -> list[str]:
        for item in v:
            _check_email(item, "asistente")
        return v


class CrmArgs(BaseModel):
    empresa: str = Field(min_length=1)
    nombre_contacto: str = Field(min_length=1)
    email: str = Field(min_length=3)
    etapa: Literal["nuevo", "contactado", "propuesta", "negociacion"]
    notas: str | None = None

    @field_validator("email")
    @classmethod
    def _email_ok(cls, v: str) -> str:
        return _check_email(v, "email")


class ToolOutputItem(BaseModel):
    tool_call_id: str = Field(min_length=1)
    output: str | None = None
    arguments: dict | None = None


class SubmitToolOutputsRequest(BaseModel):
    tool_outputs: list[ToolOutputItem] = Field(min_length=1)
