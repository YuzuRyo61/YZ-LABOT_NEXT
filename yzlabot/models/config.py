from typing import List, Union
from pydantic import BaseModel, Extra


class Config(BaseModel):
    config_id: str
    value: Union[str, int, List[str], List[int]]

    class Config:
        extra = Extra.forbid
