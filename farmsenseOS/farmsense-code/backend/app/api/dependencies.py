from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, SubscriptionTier, UserRole
import logging

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

logger = logging.getLogger(__name__)

async def get_current_user(
    api_key_header: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """
    Retrieve the user associated with the provided API key.
    """
    if not api_key_header:
        # For development/demo purposes without strict auth, we might default to FREE
        # But for security, we should eventually require keys.
        # For now, we'll return None or raise based on config.
        # Let's start strict:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )

    user = db.query(User).filter(User.api_key == api_key_header).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
        
    if not user.is_active:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user

class RequireTier:
    """
    Dependency to enforce minimum subscription tier.
    HIERARCHY: FREE < BASIC < PRO < ENTERPRISE
    """
    TIER_LEVELS = {
        SubscriptionTier.FREE: 0,
        SubscriptionTier.BASIC: 1,
        SubscriptionTier.PRO: 2,
        SubscriptionTier.ENTERPRISE: 3
    }

    def __init__(self, min_tier: SubscriptionTier):
        self.min_tier = min_tier

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        # Audit Override: Auditors get access to everything
        if user.role == UserRole.AUDITOR:
            return user
            
        user_level = self.TIER_LEVELS.get(user.tier, 0)
        required_level = self.TIER_LEVELS.get(self.min_tier, 0)

        if user_level < required_level:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tier {self.min_tier.value} required. Current tier: {user.tier.value}"
            )
        return user

class RequireRole:
    """
    Dependency to enforce exact user role.
    """
    def __init__(self, allowed_roles: list[UserRole]):
        if isinstance(allowed_roles, UserRole):
            self.allowed_roles = [allowed_roles]
        else:
            self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user.role.value} not authorized. Required: {[r.value for r in self.allowed_roles]}"
            )
        return user
