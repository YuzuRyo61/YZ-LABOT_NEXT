from typing import Optional

from pydantic import BaseModel, Extra


class VoiceRoom(BaseModel):
    assign_role_id: int
    voice_channel_id: int
    text_channel_id: Optional[int] = None

    class Config:
        extra = Extra.forbid
