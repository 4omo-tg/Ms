from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.base_class import Base

# Association table for Route <-> POI (Many-to-Many) with order
route_poi_association = Table(
    'route_poi',
    Base.metadata,
    Column('route_id', Integer, ForeignKey('route.id'), primary_key=True),
    Column('poi_id', Integer, ForeignKey('point_of_interest.id'), primary_key=True),
    Column('order', Integer, default=0)
)

class Route(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    difficulty = Column(String, default="Easy") # Easy, Medium, Hard
    reward_xp = Column(Float, default=100.0)
    is_premium = Column(Boolean, default=False)
    
    # Relationships
    points = relationship("PointOfInterest", secondary=route_poi_association, backref="routes")
