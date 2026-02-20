from sqlalchemy import Column, String, Enum, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
from .sensor_data import Base

class SubscriptionTier(str, enum.Enum):
    FREE = "FREE"             # 50m only, read-only, manual compliance
    BASIC = "BASIC"           # 20m, recommendations, no actuation
    PRO = "PRO"               # 10m, actuation, weekly reports
    ENTERPRISE = "ENTERPRISE" # 1m, actuation, compliance guarantee, daily reports

class UserRole(str, enum.Enum):
    FARMER = "FARMER"
    AUDITOR = "AUDITOR"
    ADMIN = "ADMIN"
    RESEARCHER = "RESEARCHER"
    INVESTOR = "INVESTOR"
    REVIEWER = "REVIEWER"
    PARTNER = "PARTNER"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    api_key = Column(String, unique=True, index=True, nullable=False)
    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FARMER, nullable=False)
    is_active = Column(Boolean, default=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
