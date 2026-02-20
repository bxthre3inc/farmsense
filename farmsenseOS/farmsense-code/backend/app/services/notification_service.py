"""
Real Notification Service with Multi-Channel Support
Supports Email, SMS, and Push notifications
"""
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Session
import os
import logging

from app.models.sensor_data import SoilSensorReading
from app.models.field import Field

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(Enum):
    LOW_MOISTURE = "low_moisture"
    PUMP_FAILURE = "pump_failure"
    DEVICE_OFFLINE = "device_offline"
    BATTERY_LOW = "battery_low"
    IRRIGATION_COMPLETE = "irrigation_complete"
    WEATHER_ALERT = "weather_alert"
    COMPLIANCE_VIOLATION = "compliance_violation"


class AlertThresholds:
    """Configurable thresholds per field"""
    CRITICAL_MOISTURE = 0.10
    WARNING_MOISTURE = 0.18
    CRITICAL_BATTERY = 3.0  # Volts
    OFFLINE_TIMEOUT_MINUTES = 60


class NotificationChannel:
    """Base class for notification channels"""
    
    def send(self, recipient: str, subject: str, message: str) -> bool:
        raise NotImplementedError


class EmailChannel(NotificationChannel):
    """SMTP Email notifications"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.from_email = os.getenv("FROM_EMAIL", "alerts@farmsense.io")
        self.enabled = all([self.smtp_user, self.smtp_pass])
    
    def send(self, recipient: str, subject: str, message: str) -> bool:
        if not self.enabled:
            logger.warning("Email not configured. Skipping email alert.")
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = recipient
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Email sent to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


class SMSChannel(NotificationChannel):
    """Twilio SMS notifications"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.enabled = all([self.account_sid, self.auth_token, self.from_number])
    
    def send(self, recipient: str, subject: str, message: str) -> bool:
        if not self.enabled:
            logger.warning("SMS not configured. Skipping SMS alert.")
            return False
        
        try:
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            
            # Clean phone number format
            phone = recipient.strip()
            if not phone.startswith('+'):
                # Assume US number
                phone = '+1' + phone.replace('-', '').replace(' ', '')
            
            message_obj = client.messages.create(
                body=f"{subject}: {message}",
                from_=self.from_number,
                to=phone
            )
            
            logger.info(f"SMS sent to {recipient}, SID: {message_obj.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False


class PushChannel(NotificationChannel):
    """Firebase Push Notifications"""
    
    def __init__(self):
        self.firebase_creds = os.getenv("FIREBASE_CREDENTIALS_PATH")
        self.enabled = self.firebase_creds is not None
        self._fcm = None
    
    def _get_fcm(self):
        if self._fcm is None and self.enabled:
            try:
                import firebase_admin
                from firebase_admin import credentials, messaging
                
                cred = credentials.Certificate(self.firebase_creds)
                firebase_admin.initialize_app(cred)
                self._fcm = messaging
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}")
                self.enabled = False
        return self._fcm
    
    def send(self, recipient: str, subject: str, message: str) -> bool:
        if not self.enabled:
            logger.warning("Push not configured. Skipping push alert.")
            return False
        
        try:
            fcm = self._get_fcm()
            if not fcm:
                return False
            
            notification = fcm.Notification(
                title=subject,
                body=message
            )
            
            msg = fcm.Message(
                notification=notification,
                token=recipient,  # FCM device token
                data={
                    'alert_type': 'farmsense',
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            response = fcm.send(msg)
            logger.info(f"Push sent to {recipient}, Message ID: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to send push: {e}")
            return False


class AlertHistory(Base):
    """Store alert history in database"""
    __tablename__ = 'alert_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(String(50), nullable=False, index=True)
    device_id = Column(String(50), index=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(String(500))
    
    # Delivery tracking
    email_sent = Column(String(10), default='false')
    sms_sent = Column(String(10), default='false')
    push_sent = Column(String(10), default='false')
    
    # Recipient info
    email_recipient = Column(String(100))
    phone_recipient = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_field_time', 'field_id', 'created_at'),
    )


class NotificationService:
    """Main notification service with rate limiting and deduplication"""
    
    def __init__(self):
        self.email = EmailChannel()
        self.sms = SMSChannel()
        self.push = PushChannel()
        self._recent_alerts = {}  # Deduplication cache
        self._alert_cooldown_minutes = 30
    
    def _is_duplicate(self, key: str) -> bool:
        """Check if alert was sent recently"""
        from datetime import timedelta
        
        if key in self._recent_alerts:
            last_sent = self._recent_alerts[key]
            if datetime.utcnow() - last_sent < timedelta(minutes=self._alert_cooldown_minutes):
                return True
        return False
    
    def _mark_sent(self, key: str):
        """Mark alert as sent"""
        self._recent_alerts[key] = datetime.utcnow()
        # Clean old entries periodically
        if len(self._recent_alerts) > 1000:
            cutoff = datetime.utcnow() - timedelta(hours=1)
            self._recent_alerts = {
                k: v for k, v in self._recent_alerts.items() 
                if v > cutoff
            }
    
    def evaluate_reading(self, reading: SoilSensorReading, db: Session):
        """Evaluates a sensor reading and sends alerts if needed"""
        # Get field configuration
        field = db.query(Field).filter(Field.id == reading.field_id).first()
        
        # Use field-specific thresholds or defaults
        critical_threshold = field.moisture_threshold_critical if field else AlertThresholds.CRITICAL_MOISTURE
        warning_threshold = field.moisture_threshold_warning if field else AlertThresholds.WARNING_MOISTURE
        
        alerts = []
        
        if reading.moisture_surface < critical_threshold:
            alerts.append({
                "type": AlertType.LOW_MOISTURE,
                "severity": AlertSeverity.CRITICAL,
                "message": f"CRITICAL: Moisture at {reading.moisture_surface*100:.1f}% on sensor {reading.sensor_id}. Immediate irrigation needed.",
                "field_id": reading.field_id,
                "device_id": reading.sensor_id
            })
        elif reading.moisture_surface < warning_threshold:
            alerts.append({
                "type": AlertType.LOW_MOISTURE,
                "severity": AlertSeverity.WARNING,
                "message": f"WARNING: Moisture at {reading.moisture_surface*100:.1f}% on sensor {reading.sensor_id}. Consider irrigation.",
                "field_id": reading.field_id,
                "device_id": reading.sensor_id
            })
        
        # Battery check
        if reading.battery_voltage and reading.battery_voltage < AlertThresholds.CRITICAL_BATTERY:
            alerts.append({
                "type": AlertType.BATTERY_LOW,
                "severity": AlertSeverity.WARNING,
                "message": f"LOW BATTERY: Sensor {reading.sensor_id} at {reading.battery_voltage:.2f}V",
                "field_id": reading.field_id,
                "device_id": reading.sensor_id
            })
        
        for alert in alerts:
            self.send_alert(alert, field, db)
    
    def send_alert(self, alert: dict, field: Optional[Field], db: Session):
        """Send alert through all configured channels"""
        # Deduplication key
        dedup_key = f"{alert['field_id']}:{alert.get('device_id', 'system')}:{alert['type']}:{alert['severity']}"
        
        if self._is_duplicate(dedup_key):
            logger.info(f"Skipping duplicate alert: {dedup_key}")
            return
        
        # Create history record
        history = AlertHistory(
            field_id=alert['field_id'],
            device_id=alert.get('device_id'),
            alert_type=alert['type'].value if isinstance(alert['type'], AlertType) else alert['type'],
            severity=alert['severity'].value if isinstance(alert['severity'], AlertSeverity) else alert['severity'],
            message=alert['message'],
            email_recipient=field.alert_email if field else None,
            phone_recipient=field.alert_phone if field else None
        )
        db.add(history)
        
        subject = f"[{alert['severity'].upper()}] FarmSense Alert - {alert['type']}"
        
        # Send through all channels
        if field and field.alert_email:
            success = self.email.send(field.alert_email, subject, alert['message'])
            history.email_sent = 'true' if success else 'false'
        
        if field and field.alert_phone:
            success = self.sms.send(field.alert_phone, subject[:20], alert['message'][:100])
            history.sms_sent = 'true' if success else 'false'
        
        db.commit()
        self._mark_sent(dedup_key)
        
        logger.info(f"Alert sent: {alert['message']}")


# Global instance
notification_service = NotificationService()
