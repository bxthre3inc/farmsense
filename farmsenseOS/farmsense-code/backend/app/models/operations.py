"""
Operations Management Models
- Daily goals, todos, tasks
- Roadmaps
- Financials
- Employee management
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.models.user import Base


class TaskStatus(str, enum.Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RoadmapCategory(str, enum.Enum):
    PRODUCT = "product"
    ENGINEERING = "engineering"
    BUSINESS = "business"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    RESEARCH = "research"


class FinancialCategory(str, enum.Enum):
    REVENUE = "revenue"
    EXPENSE = "expense"
    INVESTMENT = "investment"
    GRANT = "grant"
    PAYROLL = "payroll"
    OPERATIONS = "operations"
    MARKETING = "marketing"
    R_AND_D = "r_and_d"


class EmployeeDepartment(str, enum.Enum):
    EXECUTIVE = "executive"
    ENGINEERING = "engineering"
    PRODUCT = "product"
    DESIGN = "design"
    SALES = "sales"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    CUSTOMER_SUCCESS = "customer_success"
    FINANCE = "finance"
    LEGAL = "legal"
    HR = "hr"


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "active"
    ONBOARDING = "onboarding"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    CONTRACTOR = "contractor"


class DailyGoal(Base):
    """Daily goals for team members"""
    __tablename__ = "daily_goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="daily_goals")


class Task(Base):
    """Tasks and todos"""
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.BACKLOG)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    
    # Assignment
    assignee_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    reporter_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Categorization
    category = Column(String(50))  # e.g., "bug", "feature", "ops", "meeting"
    tags = Column(JSONB, default=list)
    
    # Time tracking
    estimated_hours = Column(Float)
    actual_hours = Column(Float, default=0)
    due_date = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    parent_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'))
    roadmap_item_id = Column(UUID(as_uuid=True), ForeignKey('roadmap_items.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignee = relationship("User", foreign_keys=[assignee_id], backref="assigned_tasks")
    reporter = relationship("User", foreign_keys=[reporter_id], backref="reported_tasks")
    parent = relationship("Task", remote_side=[id], backref="subtasks")
    roadmap_item = relationship("RoadmapItem", backref="tasks")


class RoadmapItem(Base):
    """Strategic roadmap items"""
    __tablename__ = "roadmap_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(SQLEnum(RoadmapCategory), nullable=False)
    
    # Timeline
    target_quarter = Column(String(10))  # e.g., "2025-Q1"
    start_date = Column(DateTime)
    target_date = Column(DateTime)
    completed_date = Column(DateTime)
    
    # Status
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.BACKLOG)
    progress_percent = Column(Integer, default=0)
    
    # Ownership
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Business impact
    expected_impact = Column(Text)
    success_metrics = Column(JSONB, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", backref="owned_roadmap_items")


class FinancialRecord(Base):
    """Financial transactions and forecasts"""
    __tablename__ = "financial_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction details
    category = Column(SQLEnum(FinancialCategory), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Description
    description = Column(String(500))
    notes = Column(Text)
    
    # Date
    transaction_date = Column(DateTime, nullable=False)
    fiscal_quarter = Column(String(10))  # e.g., "2025-Q1"
    fiscal_year = Column(Integer)
    
    # Classification
    is_forecast = Column(Boolean, default=False)  # True = projection, False = actual
    is_recurring = Column(Boolean, default=False)
    
    # Related entities
    related_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))  # For payroll
    related_grant_id = Column(String(100))  # For grant funding
    related_investor_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))  # For investments
    
    # Metadata
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    related_user = relationship("User", foreign_keys=[related_user_id], backref="payroll_records")
    related_investor = relationship("User", foreign_keys=[related_investor_id], backref="investment_records")
    created_by = relationship("User", foreign_keys=[created_by_id], backref="created_financials")


class Employee(Base):
    """Employee management"""
    __tablename__ = "employees"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Profile
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True)
    employee_number = Column(String(50), unique=True)
    
    # Role
    department = Column(SQLEnum(EmployeeDepartment), nullable=False)
    job_title = Column(String(100), nullable=False)
    level = Column(String(20))  # e.g., "L3", "Senior", "Principal"
    
    # Employment
    status = Column(SQLEnum(EmployeeStatus), default=EmployeeStatus.ONBOARDING)
    employment_type = Column(String(20), default="full_time")  # full_time, part_time, contract
    
    # Dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    
    # Compensation
    salary = Column(Float)
    salary_currency = Column(String(3), default="USD")
    equity_shares = Column(Float, default=0)
    
    # Management
    manager_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'))
    
    # Contact
    phone = Column(String(50))
    emergency_contact = Column(JSONB)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="employee_profile")
    manager = relationship("Employee", remote_side=[id], backref="direct_reports")


class Document(Base):
    """Strategic and tactical documents"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Document info
    title = Column(String(200), nullable=False)
    content = Column(Text)
    doc_type = Column(String(50))  # strategy, tactical, meeting_notes, policy, handbook
    
    # Organization
    category = Column(String(50))  # all-hands, engineering, product, etc.
    tags = Column(JSONB, default=list)
    
    # Access control
    is_internal = Column(Boolean, default=True)
    is_confidential = Column(Boolean, default=False)
    
    # Versioning
    version = Column(Integer, default=1)
    parent_version_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'))
    
    # Ownership
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Status
    status = Column(String(20), default="draft")  # draft, published, archived
    published_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship("User", backref="documents")
    parent_version = relationship("Document", remote_side=[id], backref="versions")
