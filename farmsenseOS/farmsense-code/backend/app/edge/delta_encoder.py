"""
Delta Encoding for Sensor Data
Reduces transmission size by encoding changes rather than absolute values.
Optimized for FarmSense hardware constraints.
"""
import struct
import time
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum


class CompressionLevel(Enum):
    """Compression levels based on network conditions"""
    NONE = 0       # Full precision, no delta
    LIGHT = 1      # 15-minute intervals, small deltas
    AGGRESSIVE = 2 # 60-minute intervals, batched deltas
    HIBERNATE = 3  # 6-hour intervals, max compression


@dataclass
class SensorState:
    """Tracks last known state for delta calculation"""
    sequence: int
    timestamp: float
    moisture_vwc: float
    battery_mv: int
    temperature_c: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            'sequence': self.sequence,
            'timestamp': self.timestamp,
            'moisture_vwc': self.moisture_vwc,
            'battery_mv': self.battery_mv,
            'temperature_c': self.temperature_c
        }


class DeltaEncoder:
    """
    Encodes sensor readings as deltas from previous values.
    
    Binary format (7-15 bytes depending on fields):
    - sequence_delta: 2 bytes (varint, wraps at 65535)
    - timestamp_delta: 2 bytes (seconds since last, max 18 hours)
    - moisture_delta: 2 bytes (signed, x10000 precision)
    - battery_delta: 1 byte (signed, mV change)
    - temperature_delta: 2 bytes (optional, signed x100)
    - flags: 1 byte (indicates which fields present)
    """
    
    def __init__(self, moisture_precision: int = 10000):
        self.moisture_precision = moisture_precision
        self._device_states: Dict[str, SensorState] = {}
    
    def encode(self, device_id: str, reading: Dict, 
               level: CompressionLevel = CompressionLevel.LIGHT) -> bytes:
        """
        Encode a sensor reading as delta from previous.
        
        Args:
            device_id: Unique device identifier
            reading: Current sensor reading dict
            level: Compression level based on network conditions
            
        Returns:
            Binary encoded delta (7-15 bytes vs 200+ bytes JSON)
        """
        current = SensorState(
            sequence=reading.get('sequence', 0),
            timestamp=reading.get('timestamp', time.time()),
            moisture_vwc=reading.get('moisture_vwc', 0.0),
            battery_mv=reading.get('battery_mv', 3300),
            temperature_c=reading.get('temperature_c')
        )
        
        previous = self._device_states.get(device_id)
        
        if previous is None or level == CompressionLevel.NONE:
            # First reading or no compression - send full
            encoded = self._encode_full(current)
        else:
            encoded = self._encode_delta(previous, current, level)
        
        # Update state
        self._device_states[device_id] = current
        return encoded
    
    def _encode_full(self, state: SensorState) -> bytes:
        """Encode full state (15 bytes + variable device_id)"""
        # flags: bit 0=timestamp, 1=moisture, 2=battery, 3=temperature
        flags = 0x0F  # All fields present
        
        payload = struct.pack('>BHHHh',  # 7 bytes fixed
            flags,
            state.sequence % 65535,
            int((state.timestamp % 65536) * 10),  # deciseconds
            int(state.moisture_vwc * self.moisture_precision) & 0xFFFF,
            max(-128, min(127, state.battery_mv - 3300))  # delta from 3300mV baseline
        )
        
        if state.temperature_c is not None:
            temp_packed = int(state.temperature_c * 100)
            payload += struct.pack('>h', temp_packed)
        
        return payload
    
    def _encode_delta(self, prev: SensorState, curr: SensorState,
                      level: CompressionLevel) -> bytes:
        """Encode as delta from previous state"""
        
        seq_delta = (curr.sequence - prev.sequence) % 65535
        time_delta = int(curr.timestamp - prev.timestamp)
        moisture_delta = int((curr.moisture_vwc - prev.moisture_vwc) * self.moisture_precision)
        battery_delta = curr.battery_mv - prev.battery_mv
        
        # Build flags byte
        flags = 0
        
        # Sequence always included
        flags |= 0x01
        
        # Include timestamp if significant change
        if time_delta > 255 or level == CompressionLevel.NONE:
            flags |= 0x02
            time_bytes = struct.pack('>H', time_delta)
        else:
            time_bytes = struct.pack('>B', time_delta)
        
        # Include moisture if changed beyond threshold
        moisture_threshold = self._get_moisture_threshold(level)
        if abs(curr.moisture_vwc - prev.moisture_vwc) > moisture_threshold:
            flags |= 0x04
            moisture_bytes = struct.pack('>h', moisture_delta)
        else:
            moisture_bytes = b''
        
        # Include battery if changed
        if abs(battery_delta) > 10:  # 10mV threshold
            flags |= 0x08
            battery_bytes = struct.pack('>b', max(-128, min(127, battery_delta)))
        else:
            battery_bytes = b''
        
        # Include temperature if present and changed
        temp_bytes = b''
        if curr.temperature_c is not None and prev.temperature_c is not None:
            if abs(curr.temperature_c - prev.temperature_c) > 0.5:
                flags |= 0x10
                temp_delta = int((curr.temperature_c - prev.temperature_c) * 100)
                temp_bytes = struct.pack('>h', temp_delta)
        
        # Pack everything
        header = struct.pack('>B', flags)
        seq_bytes = struct.pack('>H', seq_delta)
        
        return header + seq_bytes + time_bytes + moisture_bytes + battery_bytes + temp_bytes
    
    def _get_moisture_threshold(self, level: CompressionLevel) -> float:
        """Get moisture change threshold based on compression level"""
        thresholds = {
            CompressionLevel.NONE: 0.0,
            CompressionLevel.LIGHT: 0.001,
            CompressionLevel.AGGRESSIVE: 0.005,
            CompressionLevel.HIBERNATE: 0.01
        }
        return thresholds.get(level, 0.001)
    
    def decode(self, device_id: str, data: bytes) -> Optional[Dict]:
        """
        Decode delta-encoded data back to full reading.
        
        Args:
            device_id: Device identifier for state lookup
            data: Binary encoded data
            
        Returns:
            Decoded reading dict or None if state unknown
        """
        previous = self._device_states.get(device_id)
        if previous is None:
            return None  # Cannot decode without baseline
        
        return self._decode_delta(previous, data)
    
    def _decode_delta(self, prev: SensorState, data: bytes) -> Dict:
        """Decode delta data using previous state"""
        flags = data[0]
        offset = 1
        
        # Sequence (always present)
        seq_delta = struct.unpack('>H', data[offset:offset+2])[0]
        sequence = (prev.sequence + seq_delta) % 65535
        offset += 2
        
        # Timestamp
        if flags & 0x02:
            time_delta = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2
        else:
            time_delta = data[offset]
            offset += 1
        timestamp = prev.timestamp + time_delta
        
        # Moisture
        if flags & 0x04:
            moisture_delta = struct.unpack('>h', data[offset:offset+2])[0]
            moisture_vwc = prev.moisture_vwc + (moisture_delta / self.moisture_precision)
            offset += 2
        else:
            moisture_vwc = prev.moisture_vwc
        
        # Battery
        if flags & 0x08:
            battery_delta = struct.unpack('>b', data[offset:offset+1])[0]
            battery_mv = prev.battery_mv + battery_delta
            offset += 1
        else:
            battery_mv = prev.battery_mv
        
        # Temperature
        temperature_c = prev.temperature_c
        if flags & 0x10 and offset + 2 <= len(data):
            temp_delta = struct.unpack('>h', data[offset:offset+2])[0]
            temperature_c = prev.temperature_c + (temp_delta / 100) if prev.temperature_c else None
        
        return {
            'device_id': device_id,
            'sequence': sequence,
            'timestamp': timestamp,
            'moisture_vwc': round(moisture_vwc, 4),
            'battery_mv': battery_mv,
            'temperature_c': round(temperature_c, 2) if temperature_c else None
        }
    
    def get_compression_ratio(self, device_id: str, 
                             sample_json_size: int = 200) -> float:
        """
        Calculate compression ratio for a device's recent history.
        
        Returns:
            Ratio of original size to compressed size (higher is better)
        """
        # This would track actual compression in production
        # For now, return estimated ratio based on typical patterns
        return sample_json_size / 8.0  # ~25:1 compression


class BatchDeltaEncoder:
    """
    Encodes batches of readings with shared metadata.
    Optimized for VFA→DHU transmission.
    """
    
    def __init__(self):
        self.encoder = DeltaEncoder()
    
    def encode_batch(self, device_id: str, readings: List[Dict],
                     level: CompressionLevel = CompressionLevel.LIGHT) -> bytes:
        """
        Encode a batch of readings with shared header.
        
        Format:
        - Header (12 bytes): device_id_hash(4) + base_timestamp(4) + count(2) + flags(2)
        - Body: Delta-encoded readings
        """
        if not readings:
            return b''
        
        # Sort by timestamp
        readings = sorted(readings, key=lambda r: r.get('timestamp', 0))
        
        # Header
        device_hash = hash(device_id) % 0xFFFFFFFF
        base_timestamp = int(readings[0].get('timestamp', time.time()))
        count = len(readings)
        
        header = struct.pack('>I I H H', device_hash, base_timestamp, count, level.value)
        
        # Body - encode each reading
        body = b''
        for reading in readings:
            encoded = self.encoder.encode(device_id, reading, level)
            # Prepend size for framing
            body += struct.pack('>B', len(encoded)) + encoded
        
        return header + body
    
    def decode_batch(self, data: bytes) -> Tuple[str, List[Dict]]:
        """
        Decode a batch of readings.
        
        Returns:
            Tuple of (device_id_hash, list of readings)
        """
        if len(data) < 12:
            return None, []
        
        device_hash, base_timestamp, count, level = struct.unpack('>I I H H', data[:12])
        
        readings = []
        offset = 12
        
        for _ in range(count):
            if offset >= len(data):
                break
            
            size = data[offset]
            offset += 1
            
            encoded = data[offset:offset+size]
            offset += size
            
            # Decode - device_id would be looked up from hash in production
            reading = self.encoder.decode(str(device_hash), encoded)
            if reading:
                reading['timestamp'] = base_timestamp + (reading.get('timestamp', 0) % 65536)
                readings.append(reading)
        
        return str(device_hash), readings


# Convenience functions for API usage
def encode_sensor_reading(device_id: str, reading: Dict, 
                          level: str = "light") -> bytes:
    """Single reading encoding (for VFA edge processing)"""
    encoder = DeltaEncoder()
    compression = CompressionLevel[level.upper()]
    return encoder.encode(device_id, reading, compression)


def decode_sensor_reading(device_id: str, data: bytes) -> Optional[Dict]:
    """Single reading decoding (for DHU/RSS ingestion)"""
    encoder = DeltaEncoder()
    return encoder.decode(device_id, data)
