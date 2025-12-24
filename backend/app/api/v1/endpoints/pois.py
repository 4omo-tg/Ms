from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point

from app import models, schemas
from app.api import deps

router = APIRouter()

@router.get("/")
async def read_pois(db: AsyncSession = Depends(deps.get_db)) -> Any:
    # Fallback to RAW SQL to avoid ORM/GeoAlchemy crashes in this environment
    from sqlalchemy import text
    result = await db.execute(text("SELECT id, title, description, historic_image_url, modern_image_url, ST_X(location::geometry) as lon, ST_Y(location::geometry) as lat FROM point_of_interest"))
    rows = result.all()
    
    poi_list = []
    for row in rows:
        poi_list.append({
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "historic_image_url": row.historic_image_url,
            "modern_image_url": row.modern_image_url,
            "latitude": row.lat,
            "longitude": row.lon
        })
    return poi_list

@router.post("/", response_model=schemas.PointOfInterest)
async def create_poi(
    *,
    db: AsyncSession = Depends(deps.get_db),
    poi_in: schemas.PointOfInterestCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new POI. Only superusers.
    """
    # Create GIS point
    # Note: geoalchemy2 handles WKT.
    # WKT for Point is 'POINT(x y)' -> 'POINT(lon lat)'
    wkt_location = f'POINT({poi_in.longitude} {poi_in.latitude})'
    
    poi = models.PointOfInterest(
        title=poi_in.title,
        description=poi_in.description,
        historic_image_url=poi_in.historic_image_url,
        modern_image_url=poi_in.modern_image_url,
        location=wkt_location 
    )
    db.add(poi)
    await db.commit()
    await db.refresh(poi)
    
    point = to_shape(poi.location)
    
    return schemas.PointOfInterest(
        id=poi.id,
        title=poi.title,
        description=poi.description,
        historic_image_url=poi.historic_image_url,
        modern_image_url=poi.modern_image_url,
        latitude=point.y,
        longitude=point.x
    )

@router.get("/{poi_id}", response_model=schemas.PointOfInterest)
async def read_poi(
    *,
    db: AsyncSession = Depends(deps.get_db),
    poi_id: int,
) -> Any:
    """
    Get POI by ID.
    """
    poi = await db.get(models.PointOfInterest, poi_id)
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
        
    point = to_shape(poi.location)
    return schemas.PointOfInterest(
        id=poi.id,
        title=poi.title,
        description=poi.description,
        historic_image_url=poi.historic_image_url,
        modern_image_url=poi.modern_image_url,
        latitude=point.y,
        longitude=point.x
    )
@router.put("/{poi_id}", response_model=schemas.PointOfInterest)
async def update_poi(
    *,
    db: AsyncSession = Depends(deps.get_db),
    poi_id: int,
    poi_in: schemas.PointOfInterestUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update POI. Only superusers.
    """
    poi = await db.get(models.PointOfInterest, poi_id)
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
        
    update_data = poi_in.model_dump(exclude_unset=True)
    if "latitude" in update_data and "longitude" in update_data:
        wkt_location = f'POINT({update_data["longitude"]} {update_data["latitude"]})'
        poi.location = wkt_location
        del update_data["latitude"]
        del update_data["longitude"]
    elif "latitude" in update_data or "longitude" in update_data:
         raise HTTPException(status_code=400, detail="Must provide both latitude and longitude to update location")

    for field, value in update_data.items():
        setattr(poi, field, value)

    db.add(poi)
    await db.commit()
    await db.refresh(poi)
    
    point = to_shape(poi.location)
    
    return schemas.PointOfInterest(
        id=poi.id,
        title=poi.title,
        description=poi.description,
        historic_image_url=poi.historic_image_url,
        modern_image_url=poi.modern_image_url,
        latitude=point.y,
        longitude=point.x
    )

@router.delete("/{poi_id}", response_model=schemas.PointOfInterest)
async def delete_poi(
    *,
    db: AsyncSession = Depends(deps.get_db),
    poi_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete POI. Only superusers.
    """
    poi = await db.get(models.PointOfInterest, poi_id)
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
        
    # We need to return schema, so capture state before delete or just ID return?
    # Schema requires all fields.
    point = to_shape(poi.location)
    poi_schema = schemas.PointOfInterest(
        id=poi.id,
        title=poi.title,
        description=poi.description,
        historic_image_url=poi.historic_image_url,
        modern_image_url=poi.modern_image_url,
        latitude=point.y,
        longitude=point.x
    )
    
    await db.delete(poi)
    await db.commit()
    return poi_schema
