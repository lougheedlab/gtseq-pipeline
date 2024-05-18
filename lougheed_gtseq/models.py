from pydantic import BaseModel

__all__ = ["Sample"]


class Sample(BaseModel):
    name: str
    plate: str
    i7_name: str
    i5_name: str
