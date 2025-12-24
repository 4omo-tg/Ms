import asyncio
import logging
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.poi import PointOfInterest
from app.models.route import Route
from app.core.security import get_password_hash
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db() -> None:
    async with AsyncSessionLocal() as db:
        # 1. Create Superuser
        print("Checking superuser...")
        result = await db.execute(select(User).where(User.email == "admin@example.com"))
        user = result.scalars().first()
        if not user:
            print("Creating superuser admin@example.com")
            user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("changethis"),
                is_superuser=True,
                is_active=True
            )
            db.add(user)
            await db.commit()
        else:
            print("Superuser already exists.")

        # 2. Create Sample POIs
        print("Checking POIs...")
        result = await db.execute(select(PointOfInterest).where(PointOfInterest.title == "Red Square"))
        poi = result.scalars().first()
        if not poi:
            print("Creating Red Square POI")
            # Red Square lat/lon: 55.7539, 37.6208
            poi = PointOfInterest(
                title="Red Square",
                description="The heart of Moscow.",
                # Historic image placeholder
                historic_image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Red_square_moscow.JPG/1200px-Red_square_moscow.JPG",
                modern_image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Red_square_moscow.JPG/1200px-Red_square_moscow.JPG",
                location="POINT(37.6208 55.7539)" 
            )
            db.add(poi)
            await db.commit()
            await db.refresh(poi)
        else:
            print("POI Red Square already exists")
            
        result = await db.execute(select(PointOfInterest).where(PointOfInterest.title == "Bolshoi Theatre"))
        poi2 = result.scalars().first()
        if not poi2:
             print("Creating Bolshoi Theatre POI")
             # Bolshoi lat/lon: 55.7602, 37.6186
             poi2 = PointOfInterest(
                title="Bolshoi Theatre",
                description="Historic theatre.",
                location="POINT(37.6186 55.7602)"
             )
             db.add(poi2)
             await db.commit()
             await db.refresh(poi2)
        else:
             print("POI Bolshoi Theatre already exists")

        # 3. Create Sample Route
        print("Checking Routes...")
        result = await db.execute(select(Route).where(Route.title == "Moscow Center Walk"))
        route = result.scalars().first()
        if not route:
            print("Creating Sample Route")
            route = Route(
                title="Moscow Center Walk",
                description="A nice walk through the center.",
                difficulty="easy",
                reward_xp=100.0,
                is_premium=False
            )
            # Add POIs
            route.points = [poi, poi2]
            db.add(route)
            await db.commit()
        else:
            print("Route 'Moscow Center Walk' already exists")

        print("Initial data created.")

if __name__ == "__main__":
    asyncio.run(init_db())
