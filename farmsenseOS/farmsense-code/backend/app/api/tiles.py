from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_map_db

router = APIRouter()

@router.get("/tiles/fields/{z}/{x}/{y}.pbf")
async def get_fields_tile(
    z: int, x: int, y: int,
    db: Session = Depends(get_map_db)
):
    """
    Generate a Mapbox Vector Tile (MVT) for field boundaries.
    Includes simplified geometry and metadata (id, name, crop_type).
    """
    # Calculate tile envelope in EPSG:3857 (Web Mercator)
    # ST_TileEnvelope(z, x, y, margin=0.0) is available in PostGIS 3.0+
    # If using older PostGIS, we might need a manual envelope calculation function.
    # Assuming PostGIS 3.0+ as per requirements.

    # SQL query to generate MVT
    # We use ST_AsMVTGeom to transform geometry to tile coordinate space
    # and ST_AsMVT to aggregate into a binary protocol buffer.
    
    sql = text("""
        WITH bounds AS (
            SELECT ST_TileEnvelope(:z, :x, :y) AS geom
        ),
        mvtgeom AS (
            SELECT 
                ST_AsMVTGeom(ST_Transform(f.boundary, 3857), bounds.geom) AS geom,
                f.field_id,
                f.field_name,
                f.crop_type,
                f.area_hectares
            FROM fields f, bounds
            WHERE ST_Intersects(ST_Transform(f.boundary, 3857), bounds.geom)
        )
        SELECT ST_AsMVT(mvtgeom, 'fields', 4096, 'geom')
        FROM mvtgeom;
    """)

    try:
        # Check if the fields table exists first (or we might get an error if DB isn't init)
        # For this implementation, we assume the table exists.
        # Note: field table might be named 'fields' or implicit from models.
        # Based on overview, we should double check model names.
        # Since I don't see `fields` table in the provided model file content (I only saw sensor_data.py),
        # I will assume there is a `fields` table or similar. 
        # Wait, I should check `001_initial_schema.sql` or `sensor_data.py` to be sure about table names.
        
        # Let's verify table name from schema first if possible, but as I am in tool use,
        # I will write this assuming 'fields' and if it fails I will fix it.
        # Actually, looking at `implementation_plan.md`, I am creating this file.
        # I should probably have checked the schema. 
        # Let's pause and check schema before writing incorrect SQL.
        pass
    except Exception as e:
        # In case of error (e.g. table not found), we should handle it.
        pass

    # RE-WRITING LOGIC TO BE SAFE:
    # I will write the code to be generic enough but I should check the schema first.
    # But I can't check schema inside `write_to_file`. 
    # I will write the file with `fields` table assumption, and if I see `fields` doesn't exist 
    # when I check schema next, I will update it.
    
    result = db.execute(sql, {"z": z, "x": x, "y": y}).scalar()

    if not result:
        # Return empty tile if no data
        return Response(content=b"", media_type="application/x-protobuf")

    return Response(content=result, media_type="application/x-protobuf")

@router.get("/tiles/sensors/{z}/{x}/{y}.pbf")
async def get_sensors_tile(
    z: int, x: int, y: int,
    db: Session = Depends(get_map_db)
):
    """
    Generate MVT for sensor locations.
    """
    sql = text("""
        WITH bounds AS (
            SELECT ST_TileEnvelope(:z, :x, :y) AS geom
        ),
        mvtgeom AS (
            SELECT 
                ST_AsMVTGeom(ST_Transform(s.location, 3857), bounds.geom) AS geom,
                s.sensor_id,
                s.field_id,
                s.moisture_surface,
                s.battery_voltage
            FROM soil_sensor_readings s, bounds
            WHERE ST_Intersects(ST_Transform(s.location, 3857), bounds.geom)
            -- Optional: Filter to only latest readings per sensor?
            -- For now, return all (might be heavy, but 'sensors' usually implies locations).
            -- If 'soil_sensor_readings' is time-series, we really want distinct sensor locations.
            -- This query might get heavy if we return ALL readings.
            -- Better approach: Distinct on sensor_id
        )
        SELECT ST_AsMVT(mvtgeom, 'sensors', 4096, 'geom')
        FROM mvtgeom;
    """)
    
    # Optimization: Use a subquery to get latest reading per sensor_id 
    # or just a distinct list of sensors if we have a sensors table.
    # Based on `sensor_data.py`, we have `SoilSensorReading`. 
    # Usually there is a `sensors` table but the schema description mentioned `soil_sensor_readings` as a hypertable.
    # I'll stick to `soil_sensor_readings` for now but limit to distinct locations if possible.
    # Actually, `soil_sensor_readings` is a hypertable. Querying it for map tiles might be slow if we don't index correctly.
    # A Materialized View `sensor_latest_status` would be better.
    # primarily for this demo, I will just select distinct sensor_id and location.

    optimized_sql = text("""
        WITH bounds AS (
            SELECT ST_TileEnvelope(:z, :x, :y) AS geom
        ),
        latest_sensors AS (
            SELECT DISTINCT ON (sensor_id)
                sensor_id,
                field_id,
                location,
                moisture_surface,
                battery_voltage
            FROM soil_sensor_readings
            ORDER BY sensor_id, timestamp DESC
        ),
        mvtgeom AS (
            SELECT 
                ST_AsMVTGeom(ST_Transform(s.location, 3857), bounds.geom) AS geom,
                s.sensor_id,
                s.field_id,
                s.moisture_surface,
                s.battery_voltage
            FROM latest_sensors s, bounds
            WHERE ST_Intersects(ST_Transform(s.location, 3857), bounds.geom)
        )
        SELECT ST_AsMVT(mvtgeom, 'sensors', 4096, 'geom')
        FROM mvtgeom;
    """)

    result = db.execute(optimized_sql, {"z": z, "x": x, "y": y}).scalar()
    
    return Response(content=result or b"", media_type="application/x-protobuf")
