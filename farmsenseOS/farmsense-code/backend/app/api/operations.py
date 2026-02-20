"""
Operations Management API
- Daily goals, todos, tasks
- Roadmaps
- Financials
- Employee management
- Documents
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_user, RequireRole
from app.models.user import User, UserRole
from app.models.operations import (
    DailyGoal, Task, TaskStatus, TaskPriority,
    RoadmapItem, RoadmapCategory,
    FinancialRecord, FinancialCategory,
    Employee, EmployeeDepartment, EmployeeStatus,
    Document
)

router = APIRouter(prefix="/api/v1/operations", tags=["Operations"])


# ===== DAILY GOALS =====

@router.get("/daily-goals")
def get_daily_goals(
    date: Optional[str] = None,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get daily goals for a user or team"""
    query = db.query(DailyGoal)
    
    if user_id:
        query = query.filter(DailyGoal.user_id == uuid.UUID(user_id))
    else:
        query = query.filter(DailyGoal.user_id == current_user.id)
    
    if date:
        target_date = datetime.fromisoformat(date)
        query = query.filter(
            func.date(DailyGoal.date) == func.date(target_date)
        )
    else:
        # Default to today
        today = datetime.utcnow().date()
        query = query.filter(func.date(DailyGoal.date) == today)
    
    goals = query.order_by(desc(DailyGoal.priority), DailyGoal.created_at).all()
    return goals


@router.post("/daily-goals")
def create_daily_goal(
    title: str,
    description: Optional[str] = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new daily goal"""
    goal = DailyGoal(
        user_id=uuid.UUID(user_id) if user_id else current_user.id,
        title=title,
        description=description,
        priority=priority,
        date=datetime.utcnow()
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.put("/daily-goals/{goal_id}")
def update_daily_goal(
    goal_id: str,
    is_completed: Optional[bool] = None,
    title: Optional[str] = None,
    priority: Optional[TaskPriority] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a daily goal"""
    goal = db.query(DailyGoal).filter(DailyGoal.id == uuid.UUID(goal_id)).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    if title:
        goal.title = title
    if priority:
        goal.priority = priority
    if is_completed is not None:
        goal.is_completed = is_completed
        goal.completed_at = datetime.utcnow() if is_completed else None
    
    db.commit()
    db.refresh(goal)
    return goal


# ===== TASKS =====

@router.get("/tasks")
def get_tasks(
    status: Optional[TaskStatus] = None,
    assignee_id: Optional[str] = None,
    priority: Optional[TaskPriority] = None,
    category: Optional[str] = None,
    roadmap_item_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tasks with filters"""
    query = db.query(Task)
    
    if status:
        query = query.filter(Task.status == status)
    if assignee_id:
        query = query.filter(Task.assignee_id == uuid.UUID(assignee_id))
    if priority:
        query = query.filter(Task.priority == priority)
    if category:
        query = query.filter(Task.category == category)
    if roadmap_item_id:
        query = query.filter(Task.roadmap_item_id == uuid.UUID(roadmap_item_id))
    
    tasks = query.order_by(desc(Task.priority), Task.created_at).all()
    return tasks


@router.post("/tasks")
def create_task(
    title: str,
    description: Optional[str] = None,
    assignee_id: Optional[str] = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
    category: Optional[str] = None,
    estimated_hours: Optional[float] = None,
    due_date: Optional[datetime] = None,
    roadmap_item_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task"""
    task = Task(
        title=title,
        description=description,
        assignee_id=uuid.UUID(assignee_id) if assignee_id else None,
        reporter_id=current_user.id,
        priority=priority,
        category=category,
        estimated_hours=estimated_hours,
        due_date=due_date,
        roadmap_item_id=uuid.UUID(roadmap_item_id) if roadmap_item_id else None,
        status=TaskStatus.BACKLOG
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/tasks/{task_id}")
def update_task(
    task_id: str,
    status: Optional[TaskStatus] = None,
    assignee_id: Optional[str] = None,
    actual_hours: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task"""
    task = db.query(Task).filter(Task.id == uuid.UUID(task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if status:
        task.status = status
        if status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.utcnow()
        if status == TaskStatus.DONE:
            task.completed_at = datetime.utcnow()
    
    if assignee_id:
        task.assignee_id = uuid.UUID(assignee_id)
    
    if actual_hours is not None:
        task.actual_hours = actual_hours
    
    db.commit()
    db.refresh(task)
    return task


# ===== ROADMAP =====

@router.get("/roadmap")
def get_roadmap(
    category: Optional[RoadmapCategory] = None,
    status: Optional[TaskStatus] = None,
    quarter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get roadmap items"""
    query = db.query(RoadmapItem)
    
    if category:
        query = query.filter(RoadmapItem.category == category)
    if status:
        query = query.filter(RoadmapItem.status == status)
    if quarter:
        query = query.filter(RoadmapItem.target_quarter == quarter)
    
    items = query.order_by(RoadmapItem.target_date).all()
    return items


@router.post("/roadmap")
def create_roadmap_item(
    title: str,
    category: RoadmapCategory,
    target_quarter: str,
    description: Optional[str] = None,
    owner_id: Optional[str] = None,
    expected_impact: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN, UserRole.PARTNER]))
):
    """Create a roadmap item (Admin/Partner only)"""
    item = RoadmapItem(
        title=title,
        category=category,
        target_quarter=target_quarter,
        description=description,
        owner_id=uuid.UUID(owner_id) if owner_id else current_user.id,
        expected_impact=expected_impact
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/roadmap/{item_id}")
def update_roadmap_item(
    item_id: str,
    progress_percent: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update roadmap item progress"""
    item = db.query(RoadmapItem).filter(RoadmapItem.id == uuid.UUID(item_id)).first()
    if not item:
        raise HTTPException(status_code=404, detail="Roadmap item not found")
    
    if progress_percent is not None:
        item.progress_percent = progress_percent
    
    if status:
        item.status = status
        if status == TaskStatus.DONE:
            item.completed_date = datetime.utcnow()
    
    db.commit()
    db.refresh(item)
    return item


# ===== FINANCIALS =====

@router.get("/financials")
def get_financials(
    category: Optional[FinancialCategory] = None,
    fiscal_year: Optional[int] = None,
    fiscal_quarter: Optional[str] = None,
    is_forecast: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN, UserRole.INVESTOR]))
):
    """Get financial records (Admin/Investor only)"""
    query = db.query(FinancialRecord)
    
    if category:
        query = query.filter(FinancialRecord.category == category)
    if fiscal_year:
        query = query.filter(FinancialRecord.fiscal_year == fiscal_year)
    if fiscal_quarter:
        query = query.filter(FinancialRecord.fiscal_quarter == fiscal_quarter)
    if is_forecast is not None:
        query = query.filter(FinancialRecord.is_forecast == is_forecast)
    
    records = query.order_by(desc(FinancialRecord.transaction_date)).all()
    
    # Calculate summary
    actuals = [r for r in records if not r.is_forecast]
    forecasts = [r for r in records if r.is_forecast]
    
    summary = {
        "total_actual_revenue": sum(r.amount for r in actuals if r.category == FinancialCategory.REVENUE),
        "total_actual_expenses": sum(r.amount for r in actuals if r.category != FinancialCategory.REVENUE),
        "total_forecast_revenue": sum(r.amount for r in forecasts if r.category == FinancialCategory.REVENUE),
        "total_forecast_expenses": sum(r.amount for r in forecasts if r.category != FinancialCategory.REVENUE),
    }
    
    return {"records": records, "summary": summary}


@router.post("/financials")
def create_financial_record(
    category: FinancialCategory,
    amount: float,
    transaction_date: datetime,
    description: Optional[str] = None,
    is_forecast: bool = False,
    fiscal_quarter: Optional[str] = None,
    fiscal_year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Create financial record (Admin only)"""
    record = FinancialRecord(
        category=category,
        amount=amount,
        transaction_date=transaction_date,
        description=description,
        is_forecast=is_forecast,
        fiscal_quarter=fiscal_quarter,
        fiscal_year=fiscal_year,
        created_by_id=current_user.id
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ===== EMPLOYEES =====

@router.get("/employees")
def get_employees(
    department: Optional[EmployeeDepartment] = None,
    status: Optional[EmployeeStatus] = None,
    manager_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN, UserRole.PARTNER]))
):
    """Get employees (Admin/Partner only)"""
    query = db.query(Employee)
    
    if department:
        query = query.filter(Employee.department == department)
    if status:
        query = query.filter(Employee.status == status)
    if manager_id:
        query = query.filter(Employee.manager_id == uuid.UUID(manager_id))
    
    employees = query.order_by(Employee.department, Employee.job_title).all()
    return employees


@router.post("/employees")
def create_employee(
    user_id: str,
    employee_number: str,
    department: EmployeeDepartment,
    job_title: str,
    start_date: datetime,
    salary: float,
    manager_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Create employee record (Admin only)"""
    employee = Employee(
        user_id=uuid.UUID(user_id),
        employee_number=employee_number,
        department=department,
        job_title=job_title,
        start_date=start_date,
        salary=salary,
        manager_id=uuid.UUID(manager_id) if manager_id else None,
        status=EmployeeStatus.ONBOARDING
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.put("/employees/{employee_id}")
def update_employee(
    employee_id: str,
    status: Optional[EmployeeStatus] = None,
    salary: Optional[float] = None,
    manager_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Update employee record (Admin only)"""
    employee = db.query(Employee).filter(Employee.id == uuid.UUID(employee_id)).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if status:
        employee.status = status
    if salary:
        employee.salary = salary
    if manager_id:
        employee.manager_id = uuid.UUID(manager_id)
    
    db.commit()
    db.refresh(employee)
    return employee


# ===== DOCUMENTS =====

@router.get("/documents")
def get_documents(
    doc_type: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get documents"""
    query = db.query(Document).filter(Document.status == "published")
    
    if doc_type:
        query = query.filter(Document.doc_type == doc_type)
    if category:
        query = query.filter(Document.category == category)
    
    # Filter confidential docs for non-admins
    if current_user.role not in [UserRole.ADMIN, UserRole.PARTNER]:
        query = query.filter(Document.is_confidential == False)
    
    docs = query.order_by(desc(Document.updated_at)).all()
    return docs


@router.post("/documents")
def create_document(
    title: str,
    content: str,
    doc_type: str,
    category: str,
    is_confidential: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a document"""
    doc = Document(
        title=title,
        content=content,
        doc_type=doc_type,
        category=category,
        is_confidential=is_confidential,
        author_id=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


# ===== DASHBOARD SUMMARY =====

@router.get("/dashboard")
def get_operations_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get operations dashboard summary"""
    today = datetime.utcnow().date()
    
    # Daily goals
    daily_goals_count = db.query(DailyGoal).filter(
        func.date(DailyGoal.date) == today,
        DailyGoal.user_id == current_user.id
    ).count()
    
    daily_goals_completed = db.query(DailyGoal).filter(
        func.date(DailyGoal.date) == today,
        DailyGoal.user_id == current_user.id,
        DailyGoal.is_completed == True
    ).count()
    
    # Tasks
    tasks_total = db.query(Task).filter(
        Task.assignee_id == current_user.id
    ).count()
    
    tasks_in_progress = db.query(Task).filter(
        Task.assignee_id == current_user.id,
        Task.status == TaskStatus.IN_PROGRESS
    ).count()
    
    # Roadmap (current quarter)
    current_quarter = f"{today.year}-Q{(today.month-1)//3 + 1}"
    roadmap_items = db.query(RoadmapItem).filter(
        RoadmapItem.target_quarter == current_quarter
    ).count()
    
    return {
        "daily_goals": {
            "total": daily_goals_count,
            "completed": daily_goals_completed,
            "pending": daily_goals_count - daily_goals_completed
        },
        "tasks": {
            "total": tasks_total,
            "in_progress": tasks_in_progress
        },
        "roadmap_items_this_quarter": roadmap_items,
        "current_quarter": current_quarter
    }
