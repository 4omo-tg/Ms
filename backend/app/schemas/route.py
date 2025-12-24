from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from .poi import PointOfInterest

class RouteBase(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty: Optional[str] = "easy"
    reward_xp: Optional[float] = 0.0
    is_premium: Optional[bool] = False

class RouteCreate(RouteBase):
    poi_ids: List[int] = []

class RouteUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    reward_xp: Optional[float] = None
    is_premium: Optional[bool] = None
    poi_ids: Optional[List[int]] = None

class RouteInDBBase(RouteBase):
    id: int
    points: List[PointOfInterest] = []

    model_config = ConfigDict(from_attributes=True)

class Route(RouteInDBBase):
    pass
