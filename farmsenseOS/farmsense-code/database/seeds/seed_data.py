
"""
Database Seeder
Populates the database with initial users and demo data
"""
import sys
import os
import uuid
from datetime import datetime, timedelta
import random

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.core.database import SessionLocal, init_db, engine
from app.models.user import User, UserRole, SubscriptionTier
from app.models.sensor_data import SoilSensorReading, PumpTelemetry, Base

def seed_users(db):
    """Create default users for all roles"""
    users = [
        # FREE FARMER
        {
            "email": "free@farmsense.demo",
            "api_key": "demo-free-key",
            "role": UserRole.FARMER,
            "tier": SubscriptionTier.FREE
        },
        # BASIC FARMER
        {
            "email": "basic@farmsense.demo",
            "api_key": "demo-basic-key",
            "role": UserRole.FARMER,
            "tier": SubscriptionTier.BASIC
        },
        # PRO FARMER
        {
            "email": "pro@farmsense.demo",
            "api_key": "demo-pro-key",
            "role": UserRole.FARMER,
            "tier": SubscriptionTier.PRO
        },
        # ADMIN
        {
            "email": "admin@farmsense.demo",
            "api_key": "demo-admin-key",
            "role": UserRole.ADMIN,
            "tier": SubscriptionTier.ENTERPRISE
        },
        # AUDITOR
        {
            "email": "audit@farmsense.demo",
            "api_key": "demo-audit-key",
            "role": UserRole.AUDITOR,
            "tier": SubscriptionTier.FREE
        },
        # RESEARCHER
        {
            "email": "csu@farmsense.demo",
            "api_key": "demo-research-key",
            "role": UserRole.RESEARCHER,
            "tier": SubscriptionTier.ENTERPRISE
        },
        # INVESTOR
        {
            "email": "money@farmsense.demo",
            "api_key": "demo-investor-key",
            "role": UserRole.INVESTOR,
            "tier": SubscriptionTier.PRO
        },
        # REVIEWER
        {
            "email": "grant@farmsense.demo",
            "api_key": "demo-grant-key",
            "role": UserRole.REVIEWER,
            "tier": SubscriptionTier.FREE
        }
    ]

    print("Seeding Users...")
    for u in users:
        exists = db.query(User).filter(User.email == u["email"]).first()
        if not exists:
            user = User(
                email=u["email"],
                api_key=u["api_key"],
                role=u["role"],
                tier=u["tier"],
                is_active=True
            )
            db.add(user)
            print(f"  Created {u['role'].value}: {u['email']}")
        else:
            print(f"  Skipped {u['email']} (exists)")
    
    db.commit()

def seed_sensor_data(db):
    """Create sample field and sensor readings"""
    print("\nSeeding Sensor Data...")
    
    # Demo Field ID
    field_id = "field_demo_001"
    
    # Check if data exists
    exists = db.query(SoilSensorReading).filter(SoilSensorReading.field_id == field_id).first()
    if exists:
        print("  Skipping sensor data (already exists)")
        return

    # Create 3 sensors
    sensors = ["sensor_A", "sensor_B", "sensor_C"]
    
    # Generate 24 hours of data
    start_time = datetime.utcnow() - timedelta(hours=24)
    
    readings = []
    
    for hour in range(24):
        current_time = start_time + timedelta(hours=hour)
        
        for sensor in sensors:
            # Simulate a drying curve
            moisture = max(0.1, 0.35 - (hour * 0.005)) + random.uniform(-0.01, 0.01)
            
            reading = SoilSensorReading(
                sensor_id=sensor,
                field_id=field_id,
                timestamp=current_time,
                location=f"POINT(-105.0 {40.0 + random.uniform(0, 0.01)})", # Mock coords
                moisture_surface=moisture,
                moisture_root=moisture + 0.05,
                temp_surface=20.0 + (5 * (1 - abs(12 - hour)/12)), # Temp curve
                temp_root=18.0,
                battery_voltage=3.7
            )
            readings.append(reading)
            
    db.add_all(readings)
    db.commit()
    print(f"  Created {len(readings)} sensor readings for {field_id}")

    # Seed Pump Data
    print("\nSeeding Pump Data...")
    pumps = []
    for hour in range(24):
        # Pump runs for 4 hours
        is_running = 10 <= hour < 14
        timestamp = start_time + timedelta(hours=hour)
        
        telemetry = PumpTelemetry(
            pump_id="pump_main_01",
            field_id=field_id,
            timestamp=timestamp,
            status="running" if is_running else "idle",
            flow_rate_lpm=500.0 if is_running else 0.0,
            volume_delivered_l=500.0 * 60 if is_running else 0.0,
            power_consumption_kw=5.5 if is_running else 0.0
        )
        pumps.append(telemetry)
        
    db.add_all(pumps)
    db.commit()
    print(f"  Created {len(pumps)} pump telemetry records")

def main():
    # Ensure tables exist
    # init_db() # Call safe init from database.py if needed, or rely on migrations
    # Ideally migrations should handle schema, but for dev we might need this:
    from app.models import sensor_data, user # Import models to register with Base
    Base.metadata.create_all(bind=engine) 
    
    db = SessionLocal()
    try:
        seed_users(db)
        seed_sensor_data(db)
        print("\n✅ Database seeding complete!")
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
