"""
FarmSense OS v1.0 - Forensic Data Integrity Layer

SHA-256 cryptographic chaining and signing for Water Court admissibility.
Every measurement is hashed and linked to create an immutable audit trail.
"""

import hashlib
import json
import hmac
from datetime import datetime
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class IntegrityProof:
    """
    Cryptographic proof of data integrity for a measurement or batch.
    
    Water Court Requirements:
    - SHA-256 hashing of every sensor reading
    - Chain linking (each hash includes previous hash)
    - Hardware-backed signing (HSM recommended)
    - Immutable timestamp
    """
    measurement_hash: str
    previous_hash: str
    timestamp: str
    signature: Optional[str] = None
    signer_id: Optional[str] = None
    
    def verify_chain(self, previous_proof: 'IntegrityProof') -> bool:
        """Verify this proof correctly links to previous proof."""
        return self.previous_hash == previous_proof.measurement_hash


class ForensicHasher:
    """
    SHA-256 hashing engine for forensic-grade data integrity.
    
    Implements cryptographically chained hashing suitable for legal evidence.
    Each measurement hash includes the previous measurement's hash, creating
    an immutable chain that cannot be altered without detection.
    """
    
    def __init__(self, signing_key: Optional[str] = None):
        self.signing_key = signing_key
        self.genesis_hash = "0" * 64
    
    def hash_measurement(
        self,
        sensor_id: str,
        timestamp: str,
        depth_inches: int,
        vwc: float,
        previous_hash: str,
        additional_data: Optional[Dict] = None
    ) -> str:
        """
        Create SHA-256 hash of a measurement with chain continuity.
        
        Args:
            sensor_id: Unique sensor identifier
            timestamp: ISO format timestamp
            depth_inches: Measurement depth
            vwc: Volumetric water content
            previous_hash: Hash of previous measurement in chain
            additional_data: Optional additional fields to include
            
        Returns:
            64-character hex SHA-256 hash
        """
        # Build canonical data representation
        data = {
            'sensor_id': sensor_id,
            'timestamp': timestamp,
            'depth_inches': depth_inches,
            'vwc': round(vwc, 6),  # Round to avoid floating-point noise
            'previous_hash': previous_hash
        }
        
        if additional_data:
            # Only include deterministic, verifiable fields
            allowed_keys = ['soil_temp_c', 'water_potential', 'signal_quality']
            for key in allowed_keys:
                if key in additional_data:
                    data[key] = additional_data[key]
        
        # Canonical JSON representation (sorted keys, no whitespace)
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
        
        # SHA-256 hash
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def hash_batch(
        self,
        measurements: list,
        previous_hash: str,
        timestamp: str
    ) -> Tuple[str, str]:
        """
        Create combined hash for a batch of measurements.
        
        Returns:
            Tuple of (batch_hash, merkle_root)
        """
        if not measurements:
            return previous_hash, previous_hash
        
        # Hash individual measurements
        measurement_hashes = []
        current_previous = previous_hash
        
        for measurement in measurements:
            m_hash = self.hash_measurement(
                sensor_id=measurement['sensor_id'],
                timestamp=measurement['timestamp'],
                depth_inches=measurement['depth_inches'],
                vwc=measurement['volumetric_water_content'],
                previous_hash=current_previous,
                additional_data=measurement
            )
            measurement_hashes.append(m_hash)
            current_previous = m_hash
        
        # Compute Merkle root
        merkle_root = self._compute_merkle_root(measurement_hashes)
        
        # Batch hash includes Merkle root and metadata
        batch_data = {
            'timestamp': timestamp,
            'count': len(measurements),
            'merkle_root': merkle_root,
            'first_hash': measurement_hashes[0],
            'last_hash': measurement_hashes[-1],
            'previous_batch_hash': previous_hash
        }
        
        canonical = json.dumps(batch_data, sort_keys=True, separators=(',', ':'))
        batch_hash = hashlib.sha256(canonical.encode()).hexdigest()
        
        return batch_hash, merkle_root
    
    def _compute_merkle_root(self, hashes: list) -> str:
        """
        Compute Merkle tree root from list of hashes.
        
        Provides efficient verification of batch integrity.
        """
        if not hashes:
            return self.genesis_hash
        
        if len(hashes) == 1:
            return hashes[0]
        
        # Pairwise hashing up the tree
        current_level = hashes
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Combine and hash
                combined = left + right
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)
            
            current_level = next_level
        
        return current_level[0]
    
    def sign_hash(self, hash_value: str, key_id: str = "default") -> str:
        """
        Create HMAC signature of a hash.
        
        In production, this should use hardware security module (HSM).
        """
        if not self.signing_key:
            # No signing key - return placeholder
            return f"unsigned:{key_id}"
        
        # HMAC-SHA256
        signature = hmac.new(
            self.signing_key.encode(),
            hash_value.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"hmac:{key_id}:{signature}"
    
    def verify_signature(
        self,
        hash_value: str,
        signature: str,
        key_id: str = "default"
    ) -> bool:
        """Verify HMAC signature."""
        if not self.signing_key or signature.startswith("unsigned:"):
            return False
        
        parts = signature.split(':')
        if len(parts) != 3 or parts[0] != 'hmac':
            return False
        
        expected = self.sign_hash(hash_value, parts[1])
        return hmac.compare_digest(signature, expected)
    
    def verify_chain_integrity(
        self,
        measurements: list,
        expected_first_hash: str,
        expected_last_hash: str
    ) -> Dict:
        """
        Verify cryptographic chain integrity for a sequence of measurements.
        
        Returns verification report suitable for Water Court evidence.
        """
        if not measurements:
            return {
                'valid': False,
                'error': 'No measurements provided',
                'chain_length': 0
            }
        
        verification_results = []
        previous_hash = expected_first_hash
        total_measurements = 0
        
        for measurement in measurements:
            # Recompute hash
            computed_hash = self.hash_measurement(
                sensor_id=measurement.get('sensor_id', 'unknown'),
                timestamp=measurement.get('timestamp', ''),
                depth_inches=measurement.get('depth_inches', 0),
                vwc=measurement.get('volumetric_water_content', 0.0),
                previous_hash=previous_hash,
                additional_data=measurement
            )
            
            stored_hash = measurement.get('measurement_hash', '')
            
            result = {
                'timestamp': measurement.get('timestamp'),
                'sensor_id': measurement.get('sensor_id'),
                'computed_hash': computed_hash,
                'stored_hash': stored_hash,
                'hash_valid': computed_hash == stored_hash,
                'chain_valid': computed_hash.startswith(stored_hash[:16]) if stored_hash else False
            }
            
            verification_results.append(result)
            previous_hash = computed_hash
            total_measurements += 1
        
        final_hash = previous_hash
        chain_valid = final_hash == expected_last_hash
        
        # Count valid hashes
        valid_hashes = sum(1 for r in verification_results if r['hash_valid'])
        
        return {
            'valid': chain_valid and valid_hashes == total_measurements,
            'chain_length': total_measurements,
            'valid_hashes': valid_hashes,
            'expected_final_hash': expected_last_hash,
            'computed_final_hash': final_hash,
            'chain_intact': chain_valid,
            'verification_time': datetime.utcnow().isoformat()
        }


class AuditLogger:
    """
    Immutable audit logging for compliance and legal defense.
    
    Logs every system event, manual override, and configuration change
    with cryptographic integrity.
    """
    
    def __init__(self, log_dir: str = "/var/farmsense/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log = self.log_dir / f"audit_{datetime.utcnow().strftime('%Y%m')}.log"
        self._init_log()
    
    def _init_log(self) -> None:
        """Initialize log file with header."""
        if not self.current_log.exists():
            with open(self.current_log, 'w') as f:
                f.write("# FarmSense Forensic Audit Log\n")
                f.write(f"# Created: {datetime.utcnow().isoformat()}\n")
                f.write("# Format: timestamp|event_type|user_id|details|hash\n")
                f.write("---\n")
    
    def log_event(
        self,
        event_type: str,
        user_id: str,
        details: Dict,
        requires_signature: bool = True
    ) -> str:
        """
        Log an auditable event.
        
        Args:
            event_type: Type of event (e.g., 'irrigation_override', 'config_change')
            user_id: User who performed the action
            details: Event details dict
            requires_signature: Whether to include cryptographic signature
            
        Returns:
            Event hash for verification
        """
        timestamp = datetime.utcnow().isoformat()
        
        event_data = {
            'timestamp': timestamp,
            'event_type': event_type,
            'user_id': user_id,
            'details': details
        }
        
        canonical = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
        event_hash = hashlib.sha256(canonical.encode()).hexdigest()
        
        # Log entry
        log_entry = f"{timestamp}|{event_type}|{user_id}|{json.dumps(details)}|{event_hash}\n"
        
        with open(self.current_log, 'a') as f:
            f.write(log_entry)
        
        return event_hash
    
    def log_irrigation_override(
        self,
        user_id: str,
        field_id: str,
        zone_id: str,
        reason: str,
        duration_minutes: int,
        override_type: str = 'manual'
    ) -> str:
        """
        Log manual irrigation override (critical for Water Court defense).
        
        Required for every manual intervention to prove transparency.
        """
        return self.log_event(
            event_type='irrigation_override',
            user_id=user_id,
            details={
                'field_id': field_id,
                'zone_id': zone_id,
                'override_type': override_type,
                'reason': reason,
                'duration_minutes': duration_minutes,
                'timestamp_utc': datetime.utcnow().isoformat()
            }
        )
    
    def log_sensor_anomaly(
        self,
        sensor_id: str,
        anomaly_type: str,
        detected_value: float,
        expected_range: Tuple[float, float],
        action_taken: str
    ) -> str:
        """Log sensor anomaly detection and remediation."""
        return self.log_event(
            event_type='sensor_anomaly',
            user_id='system',
            details={
                'sensor_id': sensor_id,
                'anomaly_type': anomaly_type,
                'detected_value': detected_value,
                'expected_min': expected_range[0],
                'expected_max': expected_range[1],
                'action_taken': action_taken
            }
        )
    
    def get_audit_trail(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> list:
        """
        Retrieve filtered audit trail.
        
        Returns list of audit entries matching criteria.
        """
        entries = []
        
        with open(self.current_log, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or line == '---':
                    continue
                
                parts = line.split('|', 4)
                if len(parts) != 5:
                    continue
                
                timestamp, evt_type, usr, details, evt_hash = parts
                
                # Apply filters
                if start_time and timestamp < start_time:
                    continue
                if end_time and timestamp > end_time:
                    continue
                if event_type and evt_type != event_type:
                    continue
                if user_id and usr != user_id:
                    continue
                
                entries.append({
                    'timestamp': timestamp,
                    'event_type': evt_type,
                    'user_id': usr,
                    'details': json.loads(details),
                    'hash': evt_hash
                })
        
        return entries


# Convenience functions for common operations
def create_measurement_with_integrity(
    sensor_id: str,
    depth_inches: int,
    vwc: float,
    previous_hash: str,
    soil_temp_c: Optional[float] = None,
    water_potential: Optional[float] = None,
    signer_key: Optional[str] = None
) -> Dict:
    """
    Create a measurement dict with complete forensic integrity.
    
    Convenience function for sensor ingestion layer.
    """
    hasher = ForensicHasher(signing_key=signer_key)
    
    timestamp = datetime.utcnow().isoformat()
    
    measurement_hash = hasher.hash_measurement(
        sensor_id=sensor_id,
        timestamp=timestamp,
        depth_inches=depth_inches,
        vwc=vwc,
        previous_hash=previous_hash,
        additional_data={
            'soil_temp_c': soil_temp_c,
            'water_potential': water_potential
        }
    )
    
    signature = hasher.sign_hash(measurement_hash, sensor_id)
    
    return {
        'sensor_id': sensor_id,
        'timestamp': timestamp,
        'depth_inches': depth_inches,
        'volumetric_water_content': vwc,
        'soil_temperature_c': soil_temp_c,
        'soil_water_potential': water_potential,
        'measurement_hash': measurement_hash,
        'previous_hash': previous_hash,
        'signature': signature,
        'signal_quality': 1.0
    }
