"""
Content Management API for Command Center
Manages team members, documents, BOMs, letters, and portal configurations
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import uuid
import os
import json

from app.core.database import get_db
from app.api.dependencies import get_current_user, RequireRole
from app.models.user import User, UserRole
from app.models.content import (
    TeamMember, ContentItem, DocumentSection, LetterOfSupport,
    BOMEntry, PortalConfig, DailyGoal, BusinessPlanSection,
    ContentType, SectionType, LetterType
)

router = APIRouter(prefix="/api/v1/content", tags=["Content Management"])


# ===== TEAM MEMBERS =====

@router.get("/team")
def list_team_members(
    public_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all team members"""
    query = db.query(TeamMember)
    if public_only:
        query = query.filter(TeamMember.is_public == True)
    return query.order_by(TeamMember.display_order).all()


@router.post("/team")
def create_team_member(
    name: str = Form(...),
    title: str = Form(...),
    bio: str = Form(None),
    email: str = Form(None),
    linkedin_url: str = Form(None),
    role: str = Form(None),
    certifications: str = Form(None),  # JSON string
    education: str = Form(None),  # JSON string
    is_public: bool = Form(True),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Create a new team member"""
    member = TeamMember(
        name=name,
        title=title,
        bio=bio,
        email=email,
        linkedin_url=linkedin_url,
        role=role,
        certifications=json.loads(certifications) if certifications else None,
        education=json.loads(education) if education else None,
        is_public=is_public
    )
    
    if photo:
        # Store photo and get URL
        photo_path = f"/uploads/team/{uuid.uuid4()}_{photo.filename}"
        # In production, upload to S3 or similar
        member.photo_url = photo_path
    
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.put("/team/{member_id}")
def update_team_member(
    member_id: str,
    name: str = Form(None),
    title: str = Form(None),
    bio: str = Form(None),
    is_public: bool = Form(None),
    display_order: int = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Update a team member"""
    member = db.query(TeamMember).filter(TeamMember.id == uuid.UUID(member_id)).first()
    if not member:
        raise HTTPException(404, "Team member not found")
    
    if name: member.name = name
    if title: member.title = title
    if bio: member.bio = bio
    if is_public is not None: member.is_public = is_public
    if display_order is not None: member.display_order = display_order
    
    db.commit()
    return member


@router.delete("/team/{member_id}")
def delete_team_member(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Delete a team member"""
    member = db.query(TeamMember).filter(TeamMember.id == uuid.UUID(member_id)).first()
    if not member:
        raise HTTPException(404, "Team member not found")
    
    db.delete(member)
    db.commit()
    return {"status": "deleted"}


# ===== DOCUMENTS =====

@router.get("/documents")
def list_documents(
    content_type: Optional[ContentType] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all documents"""
    query = db.query(ContentItem)
    
    if content_type:
        query = query.filter(ContentItem.content_type == content_type)
    if tag:
        query = query.filter(ContentItem.tags.contains([tag]))
    
    return query.order_by(ContentItem.created_at.desc()).all()


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    content_type: ContentType = Form(...),
    tags: str = Form(None),
    is_public: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN, UserRole.PARTNER]))
):
    """Upload a document and extract sections"""
    # Store file
    file_path = f"/uploads/documents/{uuid.uuid4()}_{file.filename}"
    content = await file.read()
    
    # In production, store in S3 and process with document parser
    # For now, just create the record
    
    doc = ContentItem(
        title=title,
        content_type=content_type,
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type,
        tags=json.loads(tags) if tags else [],
        is_public=is_public,
        author_id=current_user.id
    )
    
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # TODO: Trigger document parsing to extract sections
    # This would call a background task to parse the document
    
    return doc


@router.post("/documents/{doc_id}/sections")
def create_document_section(
    doc_id: str,
    section_type: SectionType,
    title: str,
    content: str,
    page_number: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Create a section within a document"""
    section = DocumentSection(
        document_id=uuid.UUID(doc_id),
        section_type=section_type,
        title=title,
        content=content,
        page_number=page_number
    )
    
    db.add(section)
    db.commit()
    return section


@router.get("/sections")
def list_sections(
    section_type: Optional[SectionType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all document sections (for reuse across portals)"""
    query = db.query(DocumentSection)
    
    if section_type:
        query = query.filter(DocumentSection.section_type == section_type)
    
    return query.all()


# ===== LETTERS OF SUPPORT =====

@router.get("/letters")
def list_letters(
    letter_type: Optional[LetterType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List letters of support"""
    query = db.query(LetterOfSupport)
    
    if letter_type:
        query = query.filter(LetterOfSupport.letter_type == letter_type)
    
    return query.order_by(LetterOfSupport.created_at.desc()).all()


@router.post("/letters")
def create_letter(
    sender_name: str,
    sender_title: str,
    sender_organization: str,
    sender_email: str,
    letter_type: LetterType,
    content: str,
    project_name: str = None,
    grant_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Create a letter of support request"""
    letter = LetterOfSupport(
        sender_name=sender_name,
        sender_title=sender_title,
        sender_organization=sender_organization,
        sender_email=sender_email,
        letter_type=letter_type,
        content=content,
        project_name=project_name,
        grant_id=grant_id
    )
    
    db.add(letter)
    db.commit()
    return letter


# ===== BOM ENTRIES =====

@router.get("/bom")
def list_bom(
    device_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List BOM entries"""
    query = db.query(BOMEntry)
    
    if device_type:
        query = query.filter(BOMEntry.device_type == device_type)
    
    return query.all()


@router.get("/bom/summary")
def get_bom_summary(db: Session = Depends(get_db)):
    """Get BOM summary with totals"""
    summary = db.query(
        BOMEntry.device_type,
        func.count(BOMEntry.id).label('component_count'),
        func.sum(BOMEntry.total_cost).label('total_cost')
    ).group_by(BOMEntry.device_type).all()
    
    grand_total = db.query(func.sum(BOMEntry.total_cost)).scalar()
    
    return {
        "devices": [
            {
                "device_type": s.device_type,
                "component_count": s.component_count,
                "total_cost": s.total_cost
            }
            for s in summary
        ],
        "grand_total": grand_total
    }


@router.post("/bom")
def create_bom_entry(
    device_type: str,
    device_name: str,
    component_name: str,
    component_description: str,
    supplier: str,
    part_number: str,
    unit_cost: float,
    quantity: int,
    specs: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Create a BOM entry"""
    entry = BOMEntry(
        device_type=device_type,
        device_name=device_name,
        component_name=component_name,
        component_description=component_description,
        supplier=supplier,
        part_number=part_number,
        unit_cost=unit_cost,
        quantity=quantity,
        total_cost=unit_cost * quantity,
        specs=json.loads(specs) if specs else None
    )
    
    db.add(entry)
    db.commit()
    return entry


# ===== PORTAL CONFIG =====

@router.get("/portal/{portal_type}")
def get_portal_config(
    portal_type: str,
    db: Session = Depends(get_db)
):
    """Get portal configuration"""
    config = db.query(PortalConfig).filter(
        PortalConfig.portal_type == portal_type
    ).first()
    
    if not config:
        # Return default config
        return {
            "portal_type": portal_type,
            "title": "FarmSense",
            "tagline": "Precision Agriculture Platform",
            "primary_color": "#10b981",
            "sections": [],
            "stats": []
        }
    
    return config


@router.put("/portal/{portal_type}")
def update_portal_config(
    portal_type: str,
    title: str = None,
    tagline: str = None,
    primary_color: str = None,
    sections: str = None,
    stats: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Update portal configuration"""
    config = db.query(PortalConfig).filter(
        PortalConfig.portal_type == portal_type
    ).first()
    
    if not config:
        config = PortalConfig(portal_type=portal_type)
        db.add(config)
    
    if title: config.title = title
    if tagline: config.tagline = tagline
    if primary_color: config.primary_color = primary_color
    if sections: config.sections = json.loads(sections)
    if stats: config.stats = json.loads(stats)
    
    db.commit()
    return config


# ===== DAILY GOALS =====

@router.get("/goals")
def list_goals(
    date: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List daily goals"""
    query = db.query(DailyGoal).filter(DailyGoal.user_id == current_user.id)
    
    if date:
        target_date = datetime.fromisoformat(date)
        query = query.filter(func.date(DailyGoal.date) == func.date(target_date))
    
    return query.order_by(DailyGoal.priority.desc()).all()


@router.post("/goals")
def create_goal(
    title: str,
    description: str = None,
    date: str = None,
    priority: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a daily goal"""
    goal = DailyGoal(
        user_id=current_user.id,
        date=datetime.fromisoformat(date) if date else datetime.utcnow(),
        title=title,
        description=description,
        priority=priority
    )
    
    db.add(goal)
    db.commit()
    return goal


@router.put("/goals/{goal_id}/complete")
def complete_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a goal as complete"""
    goal = db.query(DailyGoal).filter(
        DailyGoal.id == uuid.UUID(goal_id),
        DailyGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(404, "Goal not found")
    
    goal.is_completed = True
    goal.completed_at = datetime.utcnow()
    
    db.commit()
    return goal


# ===== BUSINESS PLAN SECTIONS =====

@router.get("/business-plan")
def list_business_plan_sections(
    section_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List business plan sections for reuse"""
    query = db.query(BusinessPlanSection)
    
    if section_type:
        query = query.filter(BusinessPlanSection.section_type == section_type)
    
    return query.all()


@router.post("/business-plan")
def create_business_plan_section(
    section_name: str,
    section_type: str,
    content: str,
    source_document: str = None,
    used_in_portals: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Create a business plan section"""
    section = BusinessPlanSection(
        section_name=section_name,
        section_type=section_type,
        content=content,
        source_document=source_document,
        used_in_portals=json.loads(used_in_portals) if used_in_portals else []
    )
    
    db.add(section)
    db.commit()
    return section
