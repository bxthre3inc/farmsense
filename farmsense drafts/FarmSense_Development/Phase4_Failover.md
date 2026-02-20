# PHASE 4: FAILOVER & REDUNDANCY (Weeks 11-12)

## 4.1 Live Cloud Mirror

**Architecture:**
- Self-hosted cloud instance
- Real-time sync from Jetson via NATS
- Continuous data replication
- Identical software stack

**Failover Trigger:**
- Heartbeat timeout (3 missed = 45 seconds)
- Automatic DNS cutover
- Cloud takes processing control
- <30 second activation time

## 4.2 Cold Spare Workflow

**State:**
- Physical Jetson Nano on-site
- Powered off, preloaded with software
- Same signing keys pre-configured
- Ready for immediate activation

**Activation Procedure:**
1. Detect cloud-only operation
2. Physical swap: Replace failed Jetson
3. Power on cold spare
4. Automatic state sync from cloud
5. Resume edge processing (<30 min total)

## 4.3 Data Integrity During Failover

**Guarantees:**
- No data loss: Cloud maintains full state
- No duplicate processing: Sequence numbers
- Audit continuity: Timestamped handoffs
- Cryptographic chain: Unbroken signing
