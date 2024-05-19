from pathlib import Path
from pydantic import BaseModel

__all__ = ["Params", "Sample"]


class Params(BaseModel):
    species: str
    work_dir: Path
    run: Path
    samples: Path

    processes: int


class Sample(BaseModel):
    name: str
    plate: str
    i7_name: str
    i5_name: str
