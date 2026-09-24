"""Schemas F2 (SPEC 006). Solo lo necesario para threads/runs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ThreadCreate(BaseModel):
    metadata: dict = Field(default_factory=dict)


class MessageCreate(BaseModel):
    role: Literal["user", "assistant"] = "user"
    content: str = Field(min_length=1)


class RunCreate(BaseModel):
    assistant_id: str | None = None
    instructions: str | None = None


class ToolOutput(BaseModel):
    tool_call_id: str = Field(min_length=1)
    output: str = Field(min_length=1)
