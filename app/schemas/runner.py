from pydantic import BaseModel

class ExtendSessionRequest(BaseModel):
    extra_time: int  # extra time in minutes