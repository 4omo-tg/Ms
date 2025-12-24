from sqlalchemy import Column, Integer, String, Boolean, Float
from app.db.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    
    # Gamification
    level = Column(Integer, default=1)
    xp = Column(Float, default=0.0)
    bio = Column(String, nullable=True)
