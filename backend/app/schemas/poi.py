from typing import Optional
from pydantic import BaseModel, ConfigDict

class PointOfInterestBase(BaseModel):
    title: str
    description: Optional[str] = None
    historic_image_url: Optional[str] = None
    modern_image_url: Optional[str] = None
    # For simplicity in MVP, we can handle location as lat/lon fields for input
    # or WKT, but models.PointOfInterest uses Geometry.
    # Let's assume input is lat/lon for simplicity here.
    latitude: float
    longitude: float

class PointOfInterestCreate(PointOfInterestBase):
    pass

class PointOfInterestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    historic_image_url: Optional[str] = None
    modern_image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PointOfInterestInDBBase(PointOfInterestBase):
    id: int
    
    # We might need to compute lat/lon from the Geometry column for the response
    # Or rely on a property in the ORM model if we add one.
    # For now, let's keep the schema simple and we'll handle the conversion in the endpoint.
    
    model_config = ConfigDict(from_attributes=True)

class PointOfInterest(PointOfInterestInDBBase):
    pass
