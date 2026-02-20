// Edge Compute Module - 20m Virtual Sensor Grid Calculation
// Runs on Raspberry Pi 4 / Jetson Nano at field edge
// Performs real-time IDW interpolation with offline resilience

package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"time"

	_ "github.com/lib/pq"
	"github.com/paulmach/orb"
	"github.com/paulmach/orb/geo"
)

// Configuration
type EdgeConfig struct {
	FieldID         string  `json:"field_id"`
	GridResolution  float64 `json:"grid_resolution_m"` // 20.0 for 20m grid
	IDWPower        float64 `json:"idw_power"`          // 2.0 typical
	SearchRadius    float64 `json:"search_radius_m"`    // 100.0 - max distance to consider sensors
	MinSensors      int     `json:"min_sensors"`        // 3 minimum for interpolation
	DatabaseURL     string  `json:"database_url"`
	LocalCacheDB    string  `json:"local_cache_db"`
	SyncInterval    int     `json:"sync_interval_sec"`
	ComputeInterval int     `json:"compute_interval_sec"`
}

// Sensor reading from database
type SensorReading struct {
	SensorID         string    `json:"sensor_id"`
	Timestamp        time.Time `json:"timestamp"`
	Latitude         float64   `json:"latitude"`
	Longitude        float64   `json:"longitude"`
	MoistureSurface  float64   `json:"moisture_surface"`
	MoistureRoot     float64   `json:"moisture_root"`
	TempSurface      float64   `json:"temp_surface"`
	BatteryVoltage   float64   `json:"battery_voltage"`
	QualityFlag      string    `json:"quality_flag"`
}

// Virtual grid point (20m resolution)
type VirtualGridPoint struct {
	GridID           string    `json:"grid_id"`
	FieldID          string    `json:"field_id"`
	Timestamp        time.Time `json:"timestamp"`
	Latitude         float64   `json:"latitude"`
	Longitude        float64   `json:"longitude"`
	MoistureSurface  float64   `json:"moisture_surface"`
	MoistureRoot     float64   `json:"moisture_root"`
	Temperature      float64   `json:"temperature"`
	WaterDeficit     float64   `json:"water_deficit_mm"`
	StressIndex      float64   `json:"stress_index"`
	IrrigationNeed   string    `json:"irrigation_need"`
	SourceSensors    []string  `json:"source_sensors"`
	Confidence       float64   `json:"confidence"`
	ComputationMode  string    `json:"computation_mode"`
	EdgeDeviceID     string    `json:"edge_device_id"`
}

// Edge Processor
type EdgeProcessor struct {
	config      EdgeConfig
	cloudDB     *sql.DB
	localDB     *sql.DB
	deviceID    string
	isOnline    bool
	pendingSync []VirtualGridPoint
}

func NewEdgeProcessor(config EdgeConfig, deviceID string) (*EdgeProcessor, error) {
	// Connect to cloud database (PostgreSQL)
	cloudDB, err := sql.Open("postgres", config.DatabaseURL)
	if err != nil {
		log.Printf("Warning: Could not connect to cloud DB: %v", err)
		cloudDB = nil
	}

	// Local SQLite cache for offline operation
	localDB, err := sql.Open("sqlite3", config.LocalCacheDB)
	if err != nil {
		return nil, fmt.Errorf("failed to open local cache: %v", err)
	}

	processor := &EdgeProcessor{
		config:      config,
		cloudDB:     cloudDB,
		localDB:     localDB,
		deviceID:    deviceID,
		isOnline:    cloudDB != nil,
		pendingSync: make([]VirtualGridPoint, 0),
	}

	return processor, nil
}

// Main processing loop
func (ep *EdgeProcessor) Run() {
	computeTicker := time.NewTicker(time.Duration(ep.config.ComputeInterval) * time.Second)
	syncTicker := time.NewTicker(time.Duration(ep.config.SyncInterval) * time.Second)

	for {
		select {
		case <-computeTicker.C:
			ep.computeVirtualGrid()
		case <-syncTicker.C:
			ep.syncToCloud()
		}
	}
}

// Compute 20m virtual grid using IDW interpolation
func (ep *EdgeProcessor) computeVirtualGrid() {
	log.Println("Starting virtual grid computation...")
	startTime := time.Now()

	// 1. Fetch recent sensor readings (last 15 minutes)
	sensors, err := ep.fetchRecentSensors(15 * time.Minute)
	if err != nil {
		log.Printf("Error fetching sensors: %v", err)
		return
	}

	if len(sensors) < ep.config.MinSensors {
		log.Printf("Insufficient sensors: %d (minimum %d required)", len(sensors), ep.config.MinSensors)
		return
	}

	// 2. Generate grid points for field
	gridPoints := ep.generateGridPoints()
	log.Printf("Generated %d grid points", len(gridPoints))

	// 3. Interpolate values for each grid point
	virtualPoints := make([]VirtualGridPoint, 0, len(gridPoints))
	
	for _, point := range gridPoints {
		vp := ep.interpolatePoint(point, sensors)
		if vp != nil {
			virtualPoints = append(virtualPoints, *vp)
		}
	}

	// 4. Store results (local cache + cloud if online)
	ep.storeVirtualGrid(virtualPoints)

	duration := time.Since(startTime)
	log.Printf("Grid computation complete: %d points in %.2f seconds", len(virtualPoints), duration.Seconds())
}

// IDW (Inverse Distance Weighting) interpolation
func (ep *EdgeProcessor) interpolatePoint(point orb.Point, sensors []SensorReading) *VirtualGridPoint {
	weights := make([]float64, 0)
	moistureSurfaceValues := make([]float64, 0)
	moistureRootValues := make([]float64, 0)
	tempValues := make([]float64, 0)
	sourceSensors := make([]string, 0)

	totalWeight := 0.0

	// Calculate weights based on distance
	for _, sensor := range sensors {
		sensorPoint := orb.Point{sensor.Longitude, sensor.Latitude}
		distance := geo.Distance(point, sensorPoint)

		// Skip sensors outside search radius
		if distance > ep.config.SearchRadius {
			continue
		}

		// Handle coincident points
		if distance < 1.0 {
			// If sensor is at grid point, use its value directly
			return &VirtualGridPoint{
				GridID:          ep.generateGridID(point),
				FieldID:         ep.config.FieldID,
				Timestamp:       time.Now(),
				Latitude:        point.Lat(),
				Longitude:       point.Lon(),
				MoistureSurface: sensor.MoistureSurface,
				MoistureRoot:    sensor.MoistureRoot,
				Temperature:     sensor.TempSurface,
				SourceSensors:   []string{sensor.SensorID},
				Confidence:      1.0,
				EdgeDeviceID:    ep.deviceID,
			}
		}

		// IDW weight = 1 / distance^power
		weight := 1.0 / math.Pow(distance, ep.config.IDWPower)
		weights = append(weights, weight)
		moistureSurfaceValues = append(moistureSurfaceValues, sensor.MoistureSurface)
		moistureRootValues = append(moistureRootValues, sensor.MoistureRoot)
		tempValues = append(tempValues, sensor.TempSurface)
		sourceSensors = append(sourceSensors, sensor.SensorID)
		totalWeight += weight
	}

	// Need at least 3 sensors for reliable interpolation
	if len(weights) < ep.config.MinSensors {
		return nil
	}

	// Calculate weighted averages
	moistureSurface := 0.0
	moistureRoot := 0.0
	temperature := 0.0

	for i := range weights {
		normWeight := weights[i] / totalWeight
		moistureSurface += moistureSurfaceValues[i] * normWeight
		moistureRoot += moistureRootValues[i] * normWeight
		temperature += tempValues[i] * normWeight
	}

	// Calculate confidence based on sensor density and spread
	confidence := ep.calculateConfidence(len(weights), weights)

	// Derive metrics
	waterDeficit := ep.calculateWaterDeficit(moistureSurface, moistureRoot)
	stressIndex := ep.calculateStressIndex(moistureSurface, temperature)
	irrigationNeed := ep.classifyIrrigationNeed(waterDeficit, stressIndex)

	return &VirtualGridPoint{
		GridID:          ep.generateGridID(point),
		FieldID:         ep.config.FieldID,
		Timestamp:       time.Now(),
		Latitude:        point.Lat(),
		Longitude:       point.Lon(),
		MoistureSurface: moistureSurface,
		MoistureRoot:    moistureRoot,
		Temperature:     temperature,
		WaterDeficit:    waterDeficit,
		StressIndex:     stressIndex,
		IrrigationNeed:  irrigationNeed,
		SourceSensors:   sourceSensors,
		Confidence:      confidence,
		ComputationMode: "edge_20m",
		EdgeDeviceID:    ep.deviceID,
	}
}

// Generate 20m grid points covering the field
func (ep *EdgeProcessor) generateGridPoints() []orb.Point {
	// TODO: Load field boundary from database
	// For now, generate simple rectangular grid
	
	// Example: 100m x 100m field = 5x5 grid at 20m resolution
	points := make([]orb.Point, 0)
	
	// This should be replaced with actual field boundary query
	minLat, maxLat := 37.7749, 37.7800
	minLon, maxLon := -122.4194, -122.4100
	
	// Convert 20m to approximate degrees (rough approximation)
	latStep := 0.0002 // ~20m at mid-latitudes
	lonStep := 0.0002
	
	for lat := minLat; lat <= maxLat; lat += latStep {
		for lon := minLon; lon <= maxLon; lon += lonStep {
			points = append(points, orb.Point{lon, lat})
		}
	}
	
	return points
}

// Fetch recent sensor readings from database (cloud or local cache)
func (ep *EdgeProcessor) fetchRecentSensors(window time.Duration) ([]SensorReading, error) {
	query := `
		SELECT sensor_id, timestamp, 
		       ST_Y(location::geometry) as latitude, 
		       ST_X(location::geometry) as longitude,
		       moisture_surface, moisture_root, temp_surface,
		       battery_voltage, quality_flag
		FROM soil_sensor_readings
		WHERE field_id = $1 
		  AND timestamp > $2
		  AND quality_flag = 'valid'
		ORDER BY timestamp DESC
	`
	
	cutoff := time.Now().Add(-window)
	
	// Try cloud DB first, fallback to local cache
	db := ep.cloudDB
	if db == nil {
		db = ep.localDB
	}
	
	rows, err := db.Query(query, ep.config.FieldID, cutoff)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	sensors := make([]SensorReading, 0)
	for rows.Next() {
		var s SensorReading
		err := rows.Scan(
			&s.SensorID, &s.Timestamp, &s.Latitude, &s.Longitude,
			&s.MoistureSurface, &s.MoistureRoot, &s.TempSurface,
			&s.BatteryVoltage, &s.QualityFlag,
		)
		if err != nil {
			log.Printf("Row scan error: %v", err)
			continue
		}
		sensors = append(sensors, s)
	}
	
	return sensors, nil
}

// Calculate confidence score based on sensor coverage
func (ep *EdgeProcessor) calculateConfidence(sensorCount int, weights []float64) float64 {
	// Base confidence on sensor count
	baseConfidence := math.Min(float64(sensorCount)/10.0, 1.0)
	
	// Adjust for weight distribution (prefer evenly distributed sensors)
	if len(weights) > 0 {
		variance := calculateVariance(weights)
		distributionFactor := 1.0 / (1.0 + variance)
		return baseConfidence * distributionFactor
	}
	
	return baseConfidence
}

// Helper: calculate variance of weights
func calculateVariance(values []float64) float64 {
	if len(values) == 0 {
		return 0
	}
	
	mean := 0.0
	for _, v := range values {
		mean += v
	}
	mean /= float64(len(values))
	
	variance := 0.0
	for _, v := range values {
		variance += math.Pow(v-mean, 2)
	}
	variance /= float64(len(values))
	
	return variance
}

// Calculate water deficit in mm
func (ep *EdgeProcessor) calculateWaterDeficit(moistureSurface, moistureRoot float64) float64 {
	// Field capacity assumed at 0.35, wilting point at 0.15
	fieldCapacity := 0.35
	avgMoisture := (moistureSurface + moistureRoot) / 2.0
	
	if avgMoisture >= fieldCapacity {
		return 0.0
	}
	
	// Deficit in volumetric terms, converted to mm for 60cm depth
	deficit := (fieldCapacity - avgMoisture) * 600.0 // 60cm = 600mm
	return math.Max(deficit, 0.0)
}

// Calculate crop stress index (0-1)
func (ep *EdgeProcessor) calculateStressIndex(moisture, temperature float64) float64 {
	moistureStress := 0.0
	if moisture < 0.20 {
		moistureStress = (0.20 - moisture) / 0.20 // 0-1 scale
	}
	
	tempStress := 0.0
	if temperature > 30.0 {
		tempStress = (temperature - 30.0) / 15.0 // 30-45°C range
	}
	
	combinedStress := (moistureStress + tempStress) / 2.0
	return math.Min(combinedStress, 1.0)
}

// Classify irrigation need
func (ep *EdgeProcessor) classifyIrrigationNeed(waterDeficit, stressIndex float64) string {
	if waterDeficit < 10 && stressIndex < 0.2 {
		return "none"
	} else if waterDeficit < 30 && stressIndex < 0.4 {
		return "low"
	} else if waterDeficit < 60 && stressIndex < 0.6 {
		return "medium"
	} else if waterDeficit < 100 && stressIndex < 0.8 {
		return "high"
	} else {
		return "critical"
	}
}

// Generate grid cell ID
func (ep *EdgeProcessor) generateGridID(point orb.Point) string {
	// Simple grid ID based on rounded coordinates
	return fmt.Sprintf("%s_%.5f_%.5f", ep.config.FieldID, point.Lat(), point.Lon())
}

// Store virtual grid results
func (ep *EdgeProcessor) storeVirtualGrid(points []VirtualGridPoint) {
	// Store locally first (always)
	ep.storeLocal(points)
	
	// Try to store to cloud if online
	if ep.isOnline && ep.cloudDB != nil {
		err := ep.storeCloud(points)
		if err != nil {
			log.Printf("Cloud storage failed, queuing for sync: %v", err)
			ep.pendingSync = append(ep.pendingSync, points...)
		}
	} else {
		// Queue for later sync
		ep.pendingSync = append(ep.pendingSync, points...)
	}
}

func (ep *EdgeProcessor) storeLocal(points []VirtualGridPoint) {
	// Store in local SQLite cache
	// Implementation omitted for brevity
	log.Printf("Stored %d points to local cache", len(points))
}

func (ep *EdgeProcessor) storeCloud(points []VirtualGridPoint) error {
	// Batch insert to PostgreSQL
	// Implementation omitted for brevity
	log.Printf("Stored %d points to cloud database", len(points))
	return nil
}

// Sync pending data to cloud when connection restored
func (ep *EdgeProcessor) syncToCloud() {
	if !ep.isOnline || ep.cloudDB == nil {
		// Check if connection restored
		err := ep.cloudDB.Ping()
		if err == nil {
			ep.isOnline = true
			log.Println("Cloud connection restored")
		} else {
			return
		}
	}
	
	if len(ep.pendingSync) > 0 {
		log.Printf("Syncing %d pending records to cloud...", len(ep.pendingSync))
		err := ep.storeCloud(ep.pendingSync)
		if err == nil {
			ep.pendingSync = make([]VirtualGridPoint, 0)
			log.Println("Sync complete")
		}
	}
}

func main() {
	config := EdgeConfig{
		FieldID:         "field_001",
		GridResolution:  20.0,
		IDWPower:        2.0,
		SearchRadius:    100.0,
		MinSensors:      3,
		DatabaseURL:     "postgresql://user:pass@cloud-db:5432/farmsense",
		LocalCacheDB:    "/data/local_cache.db",
		SyncInterval:    300,  // 5 minutes
		ComputeInterval: 900,  // 15 minutes (active mode)
	}
	
	deviceID := "edge_rpi4_001"
	
	processor, err := NewEdgeProcessor(config, deviceID)
	if err != nil {
		log.Fatalf("Failed to initialize processor: %v", err)
	}
	
	log.Println("FarmSense Edge Processor starting...")
	processor.Run()
}
