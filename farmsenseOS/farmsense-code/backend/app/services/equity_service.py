
from typing import Dict, Optional
from datetime import datetime
import math
from sqlalchemy.orm import Session
from app.models.grant import EquityStake
from app.models.user import User

class EquityService:
    """
    Manages the 'Group 100' Equity Buy-in.
    10,000 shares represent 1% total ownership.
    Price follows a curve: P = P0 * (1 + rate)^n
    """
    BASE_PRICE_USD = 100.00  # Starting price per share
    TOTAL_SHARES = 10000
    RATE_INCREMENT = 0.025   # 2.5% increment per buy-in
    
    @staticmethod
    def get_current_price(db: Session) -> float:
        """Calculates the current share price based on total seats claimed"""
        count = db.query(EquityStake).count()
        # Price curve: Each new investor pays slightly more
        return EquityService.BASE_PRICE_USD * math.pow((1 + EquityService.RATE_INCREMENT), count)

    @staticmethod
    def process_buy_in(db: Session, user: User, amount_usd: float) -> EquityStake:
        """Processes a stock purchase and calculates shares issued"""
        price = EquityService.get_current_price(db)
        shares = int(amount_usd / price)
        
        if shares <= 0:
            raise ValueError("Investment amount too low for current share price")
            
        stake = EquityStake(
            user_id=user.id,
            shares=shares,
            purchase_price=price,
            purchased_at=datetime.utcnow()
        )
        db.add(stake)
        db.commit()
        db.refresh(stake)
        return stake

class SignatureService:
    """
    Manages the royalty-free Digital Signature flow.
    Generates unique tokens for non-account signing.
    """
    @staticmethod
    def generate_signing_token(letter_id: str) -> str:
        import secrets
        return secrets.token_urlsafe(32)
        
    @staticmethod
    def verify_token(db: Session, token: str):
        from app.models.grant import SupportLetter
        return db.query(SupportLetter).filter(SupportLetter.token == token).first()
