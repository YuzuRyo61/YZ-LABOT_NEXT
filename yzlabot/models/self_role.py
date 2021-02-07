from pydantic import BaseModel, Extra


class SelfRole(BaseModel):
    role_id: int
    emoji: str

    class Config:
        extra = Extra.forbid
