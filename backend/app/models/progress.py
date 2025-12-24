from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class RouteStatus(str, enum.Enum):
    STARTED = "started"
    COMPLETED = "completed"

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    route_id = Column(Integer, ForeignKey("route.id"), index=True)
    
    status = Column(String, default=RouteStatus.STARTED)
    completed_points_count = Column(Integer, default=0)
    
    user = relationship("User", backref="progress")
    route = relationship("Route")
