from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models, schemas
from app.api import deps
from geoalchemy2.shape import to_shape

router = APIRouter()

@router.get("/", response_model=List[schemas.Route])
async def read_routes(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve routes.
    """
    # Eager load points
    result = await db.execute(
        select(models.Route)
        .options(selectinload(models.Route.points))
        .offset(skip)
        .limit(limit)
    )
    routes = result.scalars().all()
    
    # We need to map the POIs inside to schema POIs with lat/lon
    route_schemas = []
    for r in routes:
        points_schema = []
        for p in r.points:
            pt = to_shape(p.location)
            points_schema.append(
                 schemas.PointOfInterest(
                    id=p.id,
                    title=p.title,
                    description=p.description,
                    historic_image_url=p.historic_image_url,
                    modern_image_url=p.modern_image_url,
                    latitude=pt.y,
                    longitude=pt.x
                )
            )
            
        route_schemas.append(
            schemas.Route(
                id=r.id,
                title=r.title,
                description=r.description,
                difficulty=r.difficulty,
                reward_xp=r.reward_xp,
                is_premium=r.is_premium,
                points=points_schema
            )
        )
    return route_schemas

@router.post("/", response_model=schemas.Route)
async def create_route(
    *,
    db: AsyncSession = Depends(deps.get_db),
    route_in: schemas.RouteCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new route. Only superusers.
    """
    route = models.Route(
        title=route_in.title,
        description=route_in.description,
        difficulty=route_in.difficulty,
        reward_xp=route_in.reward_xp,
        is_premium=route_in.is_premium
    )
    
    if route_in.poi_ids:
        # Fetch POIs
        result = await db.execute(select(models.PointOfInterest).where(models.PointOfInterest.id.in_(route_in.poi_ids)))
        pois = result.scalars().all()
        # Maintain order? For now, just add them. `in_` does not guarantee order.
        # If strict order is needed, need to handle RoutePoint association manually or sort.
        # For MVP we can assume simple association.
        route.points = pois

    db.add(route)
    await db.commit()
    await db.refresh(route, attribute_names=['points']) # refresh relationships
    
    points_schema = []
    for p in route.points:
        pt = to_shape(p.location)
        points_schema.append(
             schemas.PointOfInterest(
                id=p.id,
                title=p.title,
                description=p.description,
                historic_image_url=p.historic_image_url,
                modern_image_url=p.modern_image_url,
                latitude=pt.y,
                longitude=pt.x
            )
        )

    return schemas.Route(
        id=route.id,
        title=route.title,
        description=route.description,
        difficulty=route.difficulty,
        reward_xp=route.reward_xp,
        is_premium=route.is_premium,
        points=points_schema
    )

@router.get("/{route_id}", response_model=schemas.Route)
async def read_route(
    *,
    db: AsyncSession = Depends(deps.get_db),
    route_id: int,
) -> Any:
    """
    Get route by ID.
    """
    result = await db.execute(
        select(models.Route)
        .options(selectinload(models.Route.points))
        .where(models.Route.id == route_id)
    )
    route = result.scalars().first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    points_schema = []
    for p in route.points:
        pt = to_shape(p.location)
        points_schema.append(
             schemas.PointOfInterest(
                id=p.id,
                title=p.title,
                description=p.description,
                historic_image_url=p.historic_image_url,
                modern_image_url=p.modern_image_url,
                latitude=pt.y,
                longitude=pt.x
            )
        )

    return schemas.Route(
        id=route.id,
        title=route.title,
        description=route.description,
        difficulty=route.difficulty,
        reward_xp=route.reward_xp,
        is_premium=route.is_premium,
        points=points_schema
    )
@router.put("/{route_id}", response_model=schemas.Route)
async def update_route(
    *,
    db: AsyncSession = Depends(deps.get_db),
    route_id: int,
    route_in: schemas.RouteUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update route. Only superusers.
    """
    # Fetch route with points
    result = await db.execute(
        select(models.Route)
        .options(selectinload(models.Route.points))
        .where(models.Route.id == route_id)
    )
    route = result.scalars().first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    update_data = route_in.model_dump(exclude_unset=True)
    
    # Handle POI association update
    if "poi_ids" in update_data:
        poi_ids = update_data.pop("poi_ids")
        if poi_ids is not None:
             result_pois = await db.execute(select(models.PointOfInterest).where(models.PointOfInterest.id.in_(poi_ids)))
             pois = result_pois.scalars().all()
             route.points = pois

    for field, value in update_data.items():
        setattr(route, field, value)

    db.add(route)
    await db.commit()
    await db.refresh(route, attribute_names=['points'])
    
    points_schema = []
    for p in route.points:
        pt = to_shape(p.location)
        points_schema.append(
             schemas.PointOfInterest(
                id=p.id,
                title=p.title,
                description=p.description,
                historic_image_url=p.historic_image_url,
                modern_image_url=p.modern_image_url,
                latitude=pt.y,
                longitude=pt.x
            )
        )

    return schemas.Route(
        id=route.id,
        title=route.title,
        description=route.description,
        difficulty=route.difficulty,
        reward_xp=route.reward_xp,
        is_premium=route.is_premium,
        points=points_schema
    )

@router.delete("/{route_id}", response_model=schemas.Route)
async def delete_route(
    *,
    db: AsyncSession = Depends(deps.get_db),
    route_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete route. Only superusers.
    """
    # Fetch route with points to return schema
    result = await db.execute(
        select(models.Route)
        .options(selectinload(models.Route.points))
        .where(models.Route.id == route_id)
    )
    route = result.scalars().first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    points_schema = []
    for p in route.points:
        pt = to_shape(p.location)
        points_schema.append(
             schemas.PointOfInterest(
                id=p.id,
                title=p.title,
                description=p.description,
                historic_image_url=p.historic_image_url,
                modern_image_url=p.modern_image_url,
                latitude=pt.y,
                longitude=pt.x
            )
        )
    
    route_schema = schemas.Route(
        id=route.id,
        title=route.title,
        description=route.description,
        difficulty=route.difficulty,
        reward_xp=route.reward_xp,
        is_premium=route.is_premium,
        points=points_schema
    )

    await db.delete(route)
    await db.commit()
    return route_schema
