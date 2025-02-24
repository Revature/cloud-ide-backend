from pydantic import BaseModel

class ExtendSessionRequest(BaseModel):
    runner_id: int
    extra_time: int  # extra time in minutes