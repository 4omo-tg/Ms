from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point

from app import models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.PointOfInterest])
async def read_pois(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    latitude: float | None = None,
    longitude: float | None = None,
    radius: float | None = 500, # meters
) -> Any:
    """
    Retrieve POIs. Filter by nearby if lat/lon/radius provided.
    """
    query = select(models.PointOfInterest)
    
    if latitude is not None and longitude is not None:
        # Create a point from input
        pt = f'POINT({longitude} {latitude})'
        # Filter by distance (in meters, assuming SRID 4326 and cast to geography for meters or use correct projection)
        # GeoAlchemy2's ST_DWithin with use_spheroid=True (default for geography) works on geography types.
        # But our column is Geometry(POINT, 4326). ST_DWithin on Geometry uses units of the CRS (degrees for 4326).
        # We should cast to geography for meter-based distance or use ST_DistanceSphere (PostGIS < 2.2) / ST_Distance(geography).
        # Better: ST_DWithin(geography(location), geography(ST_GeomFromText(...)), radius_meters)
        
        # Casting geometry to geography for metric distance
        from sqlalchemy import func
        # Note: We need to ensure we import func.
        
        query = query.where(
            func.ST_DWithin(
                func.Geography(models.PointOfInterest.location),
                func.Geography(func.ST_GeomFromText(pt, 4326)),
                radius
            )
        )
    
    result = await db.execute(query.offset(skip).limit(limit))
    pois = result.scalars().all()
    
    # helper to convert geometry to lat/lon for schema
    poi_schemas = []
    for poi in pois:
        point = to_shape(poi.location)
        poi_schemas.append(
            schemas.PointOfInterest(
                id=poi.id,
                title=poi.title,
                description=poi.description,
                historic_image_url=poi.historic_image_url,
                modern_image_url=poi.modern_image_url,
                latitude=point.y,
                longitude=point.x
            )
        )
    return poi_schemas

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
