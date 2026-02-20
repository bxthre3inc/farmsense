# PHASE 3: EDGE COMPUTE PLATFORM (Weeks 7-10)

## 3.1 Jetson Nano Services

### Data Ingestion Service (Rust)
- LoRa gateway receiver
- Protocol buffer parsing
- Cryptographic verification
- TimescaleDB insertion

### Bayesian Engine (Python + CuPy)
- Recursive state estimation
- Soil texture adaptation
- Uncertainty quantification
- GPU-accelerated matrices

### Regression Kriging Service (Python + CuPy)
- 1-meter virtual grid generation
- Satellite trend integration
- Hard constraint enforcement
- <5 second target

### Actuation Controller (Rust)
- VRI decision engine
- Modbus TCP/RTU
- Fail-safe defaults
- Audit logging

### Sync & Failover Manager (Rust)
- Real-time cloud replication
- Health monitoring
- Automatic cloud activation
- Cold spare coordination

## 3.2 Bayesian Filter

**State Vector per Grid Cell:**
- VWC at 8 depths (12"-60")
- Soil texture (sand, silt, clay)
- Saturated hydraulic conductivity

**Process:**
1. Prediction: Richard's equation + ET
2. Observation: Sensor residuals
3. Update: EKF with soil adaptation
4. Learning: Reverse-engineer texture from drainage

## 3.3 Regression Kriging

**Algorithm:**
1. Compute satellite trend surface
2. Calculate sensor residuals
3. GPU kriging interpolation
4. Add trend + residuals
5. Enforce hard constraints at sensors

**Soil Variability:**
- Initial: NRCS SSURGO downscaled
- Evolution: Bayesian learning
- Goal: Match observed drainage patterns
