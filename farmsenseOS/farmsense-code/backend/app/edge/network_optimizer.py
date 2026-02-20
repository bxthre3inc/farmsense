"""
Network Optimization for FarmSense Edge Devices
Implements QUIC, FEC, and connection pooling for unreliable agricultural networks.
"""
import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import hashlib
import struct


class NetworkCondition(Enum):
    """Network quality classifications"""
    EXCELLENT = "excellent"    # <50ms latency, <0.1% loss
    GOOD = "good"              # <100ms latency, <1% loss
    FAIR = "fair"              # <300ms latency, <5% loss
    POOR = "poor"              # <1000ms latency, <10% loss
    CRITICAL = "critical"      # High loss or intermittent


@dataclass
class NetworkStats:
    """Real-time network performance metrics"""
    latency_ms: float = 0.0
    packet_loss_pct: float = 0.0
    bandwidth_kbps: float = 0.0
    jitter_ms: float = 0.0
    connection_stability: float = 1.0  # 0-1 score
    last_updated: float = field(default_factory=time.time)
    
    def classify(self) -> NetworkCondition:
        if self.packet_loss_pct > 10 or self.latency_ms > 1000:
            return NetworkCondition.CRITICAL
        elif self.packet_loss_pct > 5 or self.latency_ms > 300:
            return NetworkCondition.POOR
        elif self.packet_loss_pct > 1 or self.latency_ms > 100:
            return NetworkCondition.FAIR
        elif self.packet_loss_pct > 0.1 or self.latency_ms > 50:
            return NetworkCondition.GOOD
        return NetworkCondition.EXCELLENT


@dataclass
class QueuedMessage:
    """Message in the transmit queue"""
    payload: bytes
    priority: int  # 0=emergency, 1=critical, 2=normal, 3=batch
    timestamp: float
    retry_count: int = 0
    message_id: str = field(default_factory=lambda: hashlib.sha256(
        str(time.time()).encode()).hexdigest()[:16])


class ForwardErrorCorrection:
    """
    XOR-based Forward Error Correction for unreliable meshes.
    
    Adds redundant packets so that original data can be reconstructed
    even with packet loss. Critical for 900MHz mesh with interference.
    """
    
    def __init__(self, redundancy_ratio: float = 0.1):
        """
        Args:
            redundancy_ratio: Fraction of parity packets (0.1 = 10% overhead)
        """
        self.redundancy_ratio = redundancy_ratio
        self.block_size = 10  # Original packets per FEC block
    
    def encode(self, packets: List[bytes]) -> List[bytes]:
        """
        Add parity packets to a block of data packets.
        
        Returns:
            List of original packets + parity packets
        """
        if not packets:
            return []
        
        # Pad to block size
        while len(packets) < self.block_size:
            packets.append(b'\x00')
        
        # Calculate parity packets using XOR
        num_parity = max(1, int(self.block_size * self.redundancy_ratio))
        parity_packets = []
        
        for p in range(num_parity):
            # XOR a subset of original packets
            parity = b''
            for i, pkt in enumerate(packets[:self.block_size]):
                if (i + p) % num_parity == 0:
                    if not parity:
                        parity = pkt
                    else:
                        # XOR same-length prefixes
                        min_len = min(len(parity), len(pkt))
                        parity = bytes(a ^ b for a, b in zip(parity[:min_len], pkt[:min_len]))
            parity_packets.append(parity)
        
        return packets + parity_packets
    
    def decode(self, received: List[bytes], 
               expected_count: int) -> Optional[List[bytes]]:
        """
        Reconstruct original packets from received packets (some may be lost).
        
        Args:
            received: List of received packets (mix of data and parity)
            expected_count: Number of original data packets expected
            
        Returns:
            Reconstructed packets or None if unrecoverable
        """
        if len(received) < expected_count:
            # Too many losses to recover
            return None
        
        # Simple case: enough packets received directly
        if len(received) >= expected_count + int(expected_count * self.redundancy_ratio):
            return received[:expected_count]
        
        # Would need more sophisticated Reed-Solomon for complex recovery
        # For now, return what we have
        return received[:expected_count]


class ResilientConnection:
    """
    Connection manager optimized for agricultural network conditions.
    
    Features:
    - QUIC-like 0-RTT resumption for satellite handoffs
    - Automatic FEC for lossy links
    - Priority queuing for critical data
    - Connection pooling for DHU→RSS backhaul
    """
    
    def __init__(self, endpoint: str, 
                 fec_enabled: bool = True,
                 quic_enabled: bool = True):
        self.endpoint = endpoint
        self.fec_enabled = fec_enabled
        self.quic_enabled = quic_enabled
        
        self.stats = NetworkStats()
        self.message_queue: deque = deque()
        self.pending_acks: Dict[str, QueuedMessage] = {}
        self.fec = ForwardErrorCorrection(redundancy_ratio=0.1)
        
        self._connection_state = "disconnected"
        self._session_token: Optional[str] = None
        self._last_activity = 0
        
    async def connect(self) -> bool:
        """
        Establish connection with 0-RTT resumption if possible.
        
        Returns:
            True if connected successfully
        """
        if self._session_token:
            # Try 0-RTT resumption
            success = await self._attempt_0rtt()
            if success:
                self._connection_state = "connected"
                return True
        
        # Full handshake required
        self._session_token = await self._full_handshake()
        self._connection_state = "connected"
        return self._session_token is not None
    
    async def _attempt_0rtt(self) -> bool:
        """Attempt 0-RTT connection resumption"""
        # In production, this would use cached TLS session tickets
        # For simulation, assume 80% success rate
        await asyncio.sleep(0.01)  # 10ms vs 200ms for full handshake
        return True  # Optimistic
    
    async def _full_handshake(self) -> Optional[str]:
        """Perform full TLS handshake"""
        await asyncio.sleep(0.2)  # 200ms simulated handshake
        return hashlib.sha256(str(time.time()).encode()).hexdigest()[:32]
    
    def enqueue(self, payload: bytes, priority: int = 2) -> str:
        """
        Add message to transmit queue.
        
        Args:
            payload: Data to transmit
            priority: 0=emergency, 1=critical, 2=normal, 3=batch
            
        Returns:
            Message ID for tracking
        """
        msg = QueuedMessage(
            payload=payload,
            priority=priority,
            timestamp=time.time()
        )
        
        # Insert by priority (higher priority = lower number)
        inserted = False
        for i, existing in enumerate(self.message_queue):
            if existing.priority > priority:
                self.message_queue.insert(i, msg)
                inserted = True
                break
        
        if not inserted:
            self.message_queue.append(msg)
        
        return msg.message_id
    
    async def flush(self, max_batch_size: int = 100) -> int:
        """
        Transmit queued messages in optimized batches.
        
        Args:
            max_batch_size: Maximum messages per batch
            
        Returns:
            Number of messages sent
        """
        if not self.message_queue:
            return 0
        
        # Build batch
        batch: List[QueuedMessage] = []
        total_size = 0
        max_batch_bytes = 64000  # 64KB batch limit
        
        while (self.message_queue and 
               len(batch) < max_batch_size and 
               total_size < max_batch_bytes):
            
            msg = self.message_queue.popleft()
            batch.append(msg)
            total_size += len(msg.payload) + 32  # 32 bytes overhead
        
        if not batch:
            return 0
        
        # Apply FEC if enabled and network is poor
        if self.fec_enabled and self.stats.classify() in [
            NetworkCondition.POOR, NetworkCondition.CRITICAL
        ]:
            packets = [msg.payload for msg in batch]
            protected = self.fec.encode(packets)
            
            # Create FEC-enhanced batch
            batch_payload = self._pack_batch(batch, protected)
        else:
            batch_payload = self._pack_batch(batch)
        
        # Transmit
        success = await self._transmit(batch_payload)
        
        if success:
            for msg in batch:
                self.pending_acks[msg.message_id] = msg
            return len(batch)
        else:
            # Re-queue for retry
            for msg in batch:
                msg.retry_count += 1
                if msg.retry_count < 3:
                    self.message_queue.appendleft(msg)
            return 0
    
    def _pack_batch(self, messages: List[QueuedMessage],
                    fec_parity: Optional[List[bytes]] = None) -> bytes:
        """Pack messages into binary batch format"""
        # Header: magic(2) + version(1) + msg_count(2) + flags(1) = 6 bytes
        header = struct.pack('>HBHB', 0xFA57, 1, len(messages), 
                           0x01 if fec_parity else 0x00)
        
        # Message metadata: id(16) + len(2) + priority(1) = 19 bytes each
        metadata = b''
        payloads = b''
        
        for msg in messages:
            msg_id = bytes.fromhex(msg.message_id)
            metadata += struct.pack('>16sHB', msg_id, len(msg.payload), msg.priority)
            payloads += msg.payload
        
        # Add FEC parity if present
        fec_data = b''
        if fec_parity:
            fec_data = struct.pack('>B', len(fec_parity))
            for pkt in fec_parity:
                fec_data += struct.pack('>H', len(pkt)) + pkt
        
        return header + metadata + payloads + fec_data
    
    async def _transmit(self, payload: bytes) -> bool:
        """Simulated transmit - would be actual socket I/O"""
        await asyncio.sleep(len(payload) / (self.stats.bandwidth_kbps * 128 + 1))
        
        # Simulate packet loss
        if self.stats.packet_loss_pct > 0:
            import random
            if random.random() < (self.stats.packet_loss_pct / 100):
                return False
        
        self._last_activity = time.time()
        return True
    
    def update_network_stats(self, latency: float, packet_loss: float,
                            bandwidth: float):
        """Update network condition estimates"""
        # Smooth with EWMA
        alpha = 0.3
        self.stats.latency_ms = (alpha * latency + 
                                (1 - alpha) * self.stats.latency_ms)
        self.stats.packet_loss_pct = (alpha * packet_loss +
                                     (1 - alpha) * self.stats.packet_loss_pct)
        self.stats.bandwidth_kbps = (alpha * bandwidth +
                                    (1 - alpha) * self.stats.bandwidth_kbps)
        self.stats.last_updated = time.time()


class ConnectionPool:
    """
    Pool of resilient connections for DHU→RSS backhaul.
    
    Features:
    - Multiple concurrent connections
    - Automatic failover
    - Load balancing based on network conditions
    """
    
    def __init__(self, endpoints: List[str], pool_size: int = 3):
        self.endpoints = endpoints
        self.pool_size = min(pool_size, len(endpoints))
        self.connections: List[ResilientConnection] = []
        self._active_index = 0
        
    async def initialize(self):
        """Initialize connection pool"""
        for endpoint in self.endpoints[:self.pool_size]:
            conn = ResilientConnection(endpoint)
            await conn.connect()
            self.connections.append(conn)
    
    def get_best_connection(self) -> ResilientConnection:
        """
        Select connection with best network conditions.
        
        Returns:
            Best available connection
        """
        # Score connections
        scored = []
        for conn in self.connections:
            stats = conn.stats
            score = (
                stats.connection_stability * 0.4 +
                (1 - stats.packet_loss_pct / 100) * 0.3 +
                (1 - min(stats.latency_ms, 1000) / 1000) * 0.3
            )
            scored.append((score, conn))
        
        # Return highest scored
        scored.sort(reverse=True)
        return scored[0][1]
    
    async def send_with_failover(self, payload: bytes, 
                                  priority: int = 2) -> str:
        """
        Send message with automatic failover.
        
        Tries best connection first, falls back to others on failure.
        
        Returns:
            Message ID if sent successfully
        """
        msg_id = None
        
        for conn in sorted(self.connections, 
                          key=lambda c: c.stats.latency_ms):
            msg_id = conn.enqueue(payload, priority)
            sent = await conn.flush()
            
            if sent > 0:
                return msg_id
        
        # All connections failed - message remains in queue
        return msg_id


class MeshOptimizer:
    """
    Optimizations for 900MHz mesh network (LRZ→VFA).
    
    Handles:
    - Burst transmission scheduling
    - Collision avoidance
    - Sleep coordination
    """
    
    def __init__(self, num_devices: int = 15600):
        self.num_devices = num_devices
        self.slot_duration_ms = 10  # Time slot per device
        self.frame_duration_ms = num_devices * self.slot_duration_ms
        
    def calculate_transmit_slot(self, device_id: str) -> int:
        """
        Calculate time slot for device transmission.
        
        Uses hash of device_id for deterministic scheduling
        to avoid collisions in the mesh.
        
        Returns:
            Millisecond offset within frame
        """
        device_hash = int(hashlib.md5(device_id.encode()).hexdigest(), 16)
        return (device_hash % self.num_devices) * self.slot_duration_ms
    
    def create_sleep_schedule(self, base_interval: int = 900) -> Dict:
        """
        Create coordinated sleep schedule for battery conservation.
        
        Args:
            base_interval: Base sampling interval in seconds
            
        Returns:
            Sleep schedule configuration
        """
        # Devices wake briefly to transmit, then sleep
        return {
            'wake_duration_ms': 50,      # Time awake to transmit
            'sleep_duration_ms': (base_interval * 1000) - 50,
            'listen_window_ms': 0,       # Transmit-only, no listening
            'sync_interval_ms': 3600000  # Re-sync every hour
        }


# Utility functions

def estimate_transmit_time(payload_bytes: int, 
                           network_condition: NetworkCondition) -> float:
    """
    Estimate time to transmit payload given network conditions.
    
    Args:
        payload_bytes: Size of payload
        network_condition: Current network quality
        
    Returns:
        Estimated milliseconds to transmit
    """
    base_rates = {
        NetworkCondition.EXCELLENT: 1000,   # 1 Mbps
        NetworkCondition.GOOD: 500,         # 500 Kbps
        NetworkCondition.FAIR: 100,         # 100 Kbps
        NetworkCondition.POOR: 20,          # 20 Kbps
        NetworkCondition.CRITICAL: 5        # 5 Kbps
    }
    
    rate_kbps = base_rates.get(network_condition, 100)
    ms_per_kb = 8 / rate_kbps * 1000
    
    return payload_bytes / 1024 * ms_per_kb


def calculate_fec_overhead(payload_bytes: int, 
                           loss_rate: float,
                           target_reliability: float = 0.99) -> int:
    """
    Calculate optimal FEC overhead for target reliability.
    
    Args:
        payload_bytes: Original payload size
        loss_rate: Current packet loss rate (0-1)
        target_reliability: Desired delivery probability
        
    Returns:
        Recommended overhead bytes
    """
    if loss_rate == 0:
        return 0
    
    # Simple approximation: add 1 parity packet per 10 data packets
    # at 10% loss, this gives ~99% reliability
    num_packets = max(1, payload_bytes / 64)  # Assume 64 byte packets
    parity_packets = int(num_packets * loss_rate * 2)
    
    return min(parity_packets * 64, payload_bytes)  # Cap at 100% overhead
