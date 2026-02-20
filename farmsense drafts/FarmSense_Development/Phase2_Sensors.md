# PHASE 2: SENSOR INFRASTRUCTURE (Weeks 4-6)

## 2.1 Sensor Hardware Specifications

### Horizontal Blanket Sensor
- Shell: 3/16" 316 stainless steel, hermetic seal
- Technology: TDR (Time Domain Reflectometry)
- Accuracy: ±2% VWC
- Depths: 12" (surface), 18" (saturation)
- Cable: 100' armored, UV-resistant
- Deployment: Drive-tip, no excavation
- Lifespan: 20+ years

### Master Vertical Nail
- Shell: 3/16" 316 stainless steel
- Medium: 42" active, 5 depths (18"-42")
- Large: 60" active, 7 depths (18"-60")
- Compliance gate for deep percolation detection
- Cable: 100' armored, UV-resistant
- Deployment: Drive-tip with verification
- Lifespan: 20+ years

## 2.2 Sensor Firmware (Fresh Build)

**Requirements:**
- Ultra-low power operation
- LoRaWAN Class A
- 15-minute transmission intervals
- 48-hour local caching
- Ed25519 cryptographic signing

**Implementation:**
- Language: Rust (embedded-hal)
- MCU: STM32L4
- LoRa: SX1262 custom driver
- Security: Hardware-accelerated signing

## 2.3 Communication Protocol

**LoRa Physical:**
- Frequency: 915 MHz
- Bandwidth: 125 kHz
- Spreading Factor: SF9
- Coding Rate: 4/5

**Application Protocol:**
- Protocol Buffers
- Fields: sensor_id, timestamp, vwc[], temp[], signature, hash
