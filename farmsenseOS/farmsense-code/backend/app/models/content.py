"""
Content Management System Models
Manages documents, team members, BOMs, and portal content
"""
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, Enum, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

Base = declarative_base()


class ContentType(str, enum.Enum):
    DOCUMENT = "document"
    BOM = "bom"
    TEAM_MEMBER = "team_member"
    LETTER = "letter"
    ROADMAP = "roadmap"
    TODO = "todo"
    SPEC = "spec"


class SectionType(str, enum.Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    KEY_TEAM = "key_team"
    FINANCIALS = "financials"
    TECHNICAL = "technical"
    MARKET = "market"
    MILESTONES = "milestones"
    RISKS = "risks"


class LetterType(str, enum.Enum):
    GRANT = "grant"
    PARTNER = "partner"
    GOVERNMENT = "government"
    ACADEMIC = "academic"


class TeamMember(Base):
    """Team members displayed across portals"""
    __tablename__ = "team_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    title = Column(String(200))
    bio = Column(Text)
    photo_url = Column(String(500))
    email = Column(String(255))
    linkedin_url = Column(String(500))
    
    # Certifications & Credentials
    certifications = Column(JSON)  # [{name, issuer, year, url}]
    education = Column(JSON)  # [{degree, institution, year}]
    
    # Role & Access
    role = Column(String(100))  # Founder, Engineer, Advisor, etc.
    is_public = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    documents_authored = relationship("ContentItem", back_populates="author")


class ContentItem(Base):
    """Base content item - documents, BOMs, specs, etc."""
    __tablename__ = "content_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    content_type = Column(Enum(ContentType), nullable=False)
    
    # File storage
    file_path = Column(String(1000))  # Path to stored file
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Extracted content
    raw_text = Column(Text)  # Full extracted text
    summary = Column(Text)  # AI-generated summary
    
    # Metadata
    tags = Column(JSON)  # ["financial", "2026", "grant"]
    version = Column(String(50), default="1.0")
    
    # Access Control
    is_public = Column(Boolean, default=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("team_members.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship("TeamMember", back_populates="documents_authored")
    sections = relationship("DocumentSection", back_populates="document", cascade="all, delete-orphan")


class DocumentSection(Base):
    """Extracted sections from documents for reuse across portals"""
    __tablename__ = "document_sections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id", ondelete="CASCADE"))
    
    # Section identity
    section_type = Column(Enum(SectionType), nullable=False)
    title = Column(String(500))
    content = Column(Text, nullable=False)
    
    # Position in original document
    page_number = Column(Integer)
    section_index = Column(Integer)
    
    # Usage tracking
    used_in_portals = Column(JSON)  # ["investor", "grant"]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("ContentItem", back_populates="sections")


class LetterOfSupport(Base):
    """Letters of support from partners, officials, institutions"""
    __tablename__ = "letters_of_support"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Sender info
    sender_name = Column(String(200), nullable=False)
    sender_title = Column(String(200))
    sender_organization = Column(String(200))
    sender_email = Column(String(255))
    
    # Letter details
    letter_type = Column(Enum(LetterType), nullable=False)
    content = Column(Text)
    file_path = Column(String(1000))
    
    # Status
    is_signed = Column(Boolean, default=False)
    signed_at = Column(DateTime)
    signature_token = Column(String(100))
    
    # Grant/Project association
    project_name = Column(String(200))
    grant_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class BOMEntry(Base):
    """Bill of Materials - hardware components"""
    __tablename__ = "bom_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Device info
    device_type = Column(String(50), nullable=False)  # LRZ, VFA, PFA, PMT, DHU, RSS
    device_name = Column(String(200))
    
    # Component details
    component_name = Column(String(200))
    component_description = Column(Text)
    supplier = Column(String(200))
    part_number = Column(String(100))
    
    # Costs
    unit_cost = Column(Float)
    quantity = Column(Integer)
    total_cost = Column(Float)
    
    # Technical specs
    specs = Column(JSON)  # {power, weight, dimensions, etc.}
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class PortalConfig(Base):
    """Portal configuration - what content to show where"""
    __tablename__ = "portal_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portal_type = Column(String(50), nullable=False)  # investor, grant, farmer, public
    
    # Display settings
    title = Column(String(200))
    tagline = Column(String(500))
    primary_color = Column(String(20), default="#10b981")
    logo_url = Column(String(500))
    
    # Content sections to display
    sections = Column(JSON)  # [{section_id, display_order, is_visible}]
    
    # Stats/metrics to show (from BOM or other sources)
    stats = Column(JSON)  # [{label, value, source, is_target}]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class DailyGoal(Base):
    """Daily goals and todos"""
    __tablename__ = "daily_goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    date = Column(DateTime, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    priority = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class BusinessPlanSection(Base):
    """Sections from business plan that can be reused"""
    __tablename__ = "business_plan_sections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_name = Column(String(200), nullable=False)
    section_type = Column(String(100))  # executive_summary, team, financials, market, etc.
    content = Column(Text, nullable=False)
    source_document = Column(String(500))
    
    # Where this section is used
    used_in_portals = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
