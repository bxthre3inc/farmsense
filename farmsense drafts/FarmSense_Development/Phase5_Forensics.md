# PHASE 5: FORENSIC SECURITY (Weeks 13-14)

## 5.1 Cryptographic Chain

**Per Reading:**
- SHA-256 hash of raw data
- Ed25519 signature (hardware module)
- Timestamp (GPS-synchronized)
- Sensor ID and location

**Storage:**
- Local: 24 months retention
- Cloud: Mirrored backup
- Immutable: Append-only logs

## 5.2 Audit Trail

**Logged Events:**
- Every sensor reading
- Every VRI actuation
- Every manual override
- Every system state change

**Format:**
- Structured JSON
- Cryptographic hash chain
- User attribution
- Geographic tagging

## 5.3 Water Court Compliance

**Requirements:**
- Prove data integrity (hashing/signing)
- Prove no manipulation (immutable logs)
- Prove physical ground truth (sensors)
- Prove automated compliance (no manual)

**Deliverables:**
- Immutable audit reports
- Cryptographic verification tools
- Expert testimony documentation
- CSU validation partnership
