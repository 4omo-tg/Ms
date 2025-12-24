from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserProgressBase(BaseModel):
    status: str
    completed_points_count: int = 0

class UserProgressCreate(UserProgressBase):
    route_id: int

class UserProgressUpdate(BaseModel):
    status: Optional[str] = None
    completed_points_count: Optional[int] = None

class UserProgressInDBBase(UserProgressBase):
    id: int
    user_id: int
    route_id: int

    model_config = ConfigDict(from_attributes=True)

class UserProgress(UserProgressInDBBase):
    pass
