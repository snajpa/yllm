"""Base tool schema stub."""

from pydantic import BaseModel


class BaseTool(BaseModel):
    name: str
