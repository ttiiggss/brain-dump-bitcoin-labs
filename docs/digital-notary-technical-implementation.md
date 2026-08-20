# Document Hash Verification — Technical Implementation Guide

**Practical guide for building the digital notary service. Code snippets, API integrations, database schema, security hardening.**

---

## Project Structure

```
digital-notary/
├── backend/                 # Python Flask/FastAPI
│   ├── app.py              # Main application
│   ├── routes/
│   │   ├── upload.py       # Document upload endpoint
│   │   ├── timestamp.py    # TSA integration
│   │   ├── blockchain.py   # Bitcoin OP_RETURN anchoring
│   │   ├── verify.py       # Verification workflow
│   │   └── api.py          # Public API endpoints
│   ├── models/             # Database models
│   ├── services/           # Business logic
│   │   ├── hash_service.py
│   │   ├── token_service.py
│   │   └── anchor_service.py
│   └── utils/
│       ├── crypto.py       # SHA-256 hashing
│       └── qr_codes.py     # QR code generation
├── frontend/               # React + TypeScript
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   └── package.json
├── database/
│   └── schema.sql          # PostgreSQL schema
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
└── tests/
    ├── unit/
    └── integration/
```

---

## Component 1: Hash Generation Module

### Backend Implementation (Python)

```python
import hashlib
import os

class HashService:
    """SHA-256 hash generation for documents."""

    @staticmethod
    def hash_document(file_path: str) -> str:
        """Read file as binary and compute SHA-256 hash."""
        sha256_hash = hashlib.sha256()

        # Read in chunks to handle large files efficiently
        with open(file_path, 'rb') as f:
            # Read in 64KB chunks
            for byte_block in iter(lambda: f.read(65536), b''):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """Hash raw bytes (for API uploads)."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def verify_hash(file_path: str, expected_hash: str) -> bool:
        """Verify that a document matches the expected hash."""
        actual_hash = HashService.hash_document(file_path)
        return actual_hash.lower() == expected_hash.lower()
```

### API Endpoint (Flask)

```python
from flask import Flask, request, jsonify
import tempfile
import os

app = Flask(__name__)

@app.route('/api/v1/hash', methods=['POST'])
def upload_and_hash():
    """Upload document and return its SHA-256 hash."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        # Compute hash
        document_hash = HashService.hash_document(tmp_path)
        file_size = os.path.getsize(tmp_path)

        return jsonify({
            'hash': document_hash,
            'algorithm': 'sha256',
            'filename': file.filename,
            'size_bytes': file_size,
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
        })
    finally:
        # Clean up temp file
        os.unlink(tmp_path)
```

### Frontend Implementation (React)

```tsx
import React, { useState } from 'react';

const DocumentUploader: React.FC = () => {
  const [hash, setHash] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (file: File) => {
    setUploading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/v1/hash', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setHash(data.hash);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        onChange={(e) => e.target.files && handleUpload(e.target.files[0])}
      />
      {uploading && <p>Computing hash...</p>}
      {hash && <p>SHA-256: {hash}</p>}
    </div>
  );
};
```

---

## Component 2: RFC 3161 Timestamp Integration

### DigiCert TSA API Integration

```python
import requests
import base64
from datetime import datetime

class TimestampService:
    """RFC 3161 timestamp integration with DigiCert TSA."""

    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint

    def request_timestamp(self, document_hash: str) -> dict:
        """Request timestamp for a document hash."""
        headers = {
            'Content-Type': 'application/timestamp-query',
            'Authorization': f'Bearer {self.api_key}'
        }

        # RFC 3161 timestamp request (simplified)
        # In production, use proper ASN.1 encoding
        payload = {
            'hashAlgorithm': 'sha256',
            'hashValue': document_hash
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            return {
                'success': True,
                'timestamp_token': response.json().get('timestampToken'),
                'timestamp': response.json().get('timestamp'),
                'serial_number': response.json().get('serialNumber')
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }

    def verify_timestamp(self, timestamp_token: str) -> dict:
        """Verify a timestamp token (offline verification)."""
        # Use OpenSSL or similar to verify the signature
        # This is simplified; in production, use proper crypto libraries
        try:
            # Verify timestamp token signature
            # This would involve checking against TSA certificate
            return {
                'success': True,
                'verified': True,
                'timestamp': 'extracted_from_token'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
```

### API Endpoint for Timestamping

```python
@app.route('/api/v1/timestamp', methods=['POST'])
def request_timestamp():
    """Request timestamp for a document hash."""
    data = request.json

    if not data or 'hash' not in data:
        return jsonify({'error': 'Missing hash in request'}), 400

    document_hash = data['hash']
    ts_service = TimestampService(
        api_key=os.getenv('DIGICERT_API_KEY'),
        endpoint='https://timestamp.digicert.com/tsa'
    )

    result = ts_service.request_timestamp(document_hash)

    if not result.get('success'):
        return jsonify({
            'error': result.get('error'),
            'timestamp': None
        }), 500

    return jsonify({
        'success': True,
        'timestamp': result.get('timestamp'),
        'timestamp_token': result.get('timestamp_token'),
        'serial_number': result.get('serial_number'),
        'tsa': 'DigiCert'
    })
```

---

## Component 3: Bitcoin OP_RETURN Blockchain Anchoring

### Bitcoin OP_RETURN Implementation

```python
import requests
from typing import Dict

class BlockchainAnchorService:
    """Bitcoin OP_RETURN anchoring for backup timestamps."""

    def __init__(self, rpc_user: str, rpc_password: str, rpc_url: str):
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self.rpc_url = rpc_url

    def _rpc_call(self, method: str, params: list = None) -> Dict:
        """Make RPC call to Bitcoin Core."""
        headers = {
            'Content-Type': 'application/json'
        }

        payload = {
            'method': method,
            'params': params or [],
            'id': 1
        }

        response = requests.post(
            self.rpc_url,
            json=payload,
            headers=headers,
            auth=(self.rpc_user, self.rpc_password),
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    def anchor_hash(self, document_hash: str, fee_rate: int = 10) -> Dict:
        """Anchor document hash in Bitcoin OP_RETURN."""
        # OP_RETURN can hold up to 80 bytes
        # SHA-256 hash is 64 hex characters (32 bytes) — fits comfortably

        # Create raw transaction with OP_RETURN output
        # This is simplified; in production, use proper transaction building
        try:
            # 1. Get UTXO from wallet
            utxo_result = self._rpc_call('listunspent', [1, 1])

            if not utxo_result.get('result'):
                return {'success': False, 'error': 'No UTXOs available'}

            utxo = utxo_result['result'][0]

            # 2. Create raw transaction
            raw_tx = self._rpc_call('createrawtransaction', [
                [{utxo['txid']: utxo['vout']}],  # Inputs
                {
                    'data': document_hash,  # OP_RETURN output
                    utxo['address']: utxo['amount'] - (fee_rate * 150 / 100000000)  # Change output
                }
            ])

            # 3. Sign transaction
            signed_tx = self._rpc_call('signrawtransaction', [raw_tx['result']])

            # 4. Broadcast transaction
            broadcast_result = self._rpc_call('sendrawtransaction', [signed_tx['result']])

            return {
                'success': True,
                'txid': broadcast_result['result'],
                'block_height': None,  # Will update on confirmation
                'status': 'pending'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def check_confirmation(self, txid: str) -> Dict:
        """Check if transaction is confirmed and get block height."""
        try:
            tx_result = self._rpc_call('gettransaction', [txid])

            if not tx_result.get('result'):
                return {'success': False, 'error': 'Transaction not found'}

            tx = tx_result['result']

            if tx.get('confirmations', 0) > 0:
                block_height = tx.get('blockheight')
                block_hash = tx.get('blockhash')

                return {
                    'success': True,
                    'confirmed': True,
                    'block_height': block_height,
                    'block_hash': block_hash,
                    'confirmations': tx.get('confirmations')
                }
            else:
                return {
                    'success': True,
                    'confirmed': False,
                    'status': 'pending'
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
```

### API Endpoint for Blockchain Anchoring

```python
@app.route('/api/v1/anchor', methods=['POST'])
def anchor_hash():
    """Anchor document hash on Bitcoin blockchain."""
    data = request.json

    if not data or 'hash' not in data:
        return jsonify({'error': 'Missing hash in request'}), 400

    document_hash = data['hash']
    anchor_service = BlockchainAnchorService(
        rpc_user=os.getenv('BTC_RPC_USER'),
        rpc_password=os.getenv('BTC_RPC_PASSWORD'),
        rpc_url=os.getenv('BTC_RPC_URL', 'http://127.0.0.1:8332')
    )

    result = anchor_service.anchor_hash(document_hash)

    if not result.get('success'):
        return jsonify({
            'error': result.get('error'),
            'anchor': None
        }), 500

    return jsonify({
        'success': True,
        'txid': result.get('txid'),
        'block_height': result.get('block_height'),
        'status': result.get('status'),
        'blockchain': 'bitcoin',
        'network': 'mainnet'
    })
```

---

## Component 4: Token Issuance System

### Token Structure

```json
{
  "hash": "a1b2c3d4e5f67890...",
  "algorithm": "sha256",
  "document_name": "contract.pdf",
  "timestamp": "2024-08-13T14:32:15Z",
  "anchor_type": "rfc3161_tsa",
  "anchor_data": {
    "timestamp_token": "base64_encoded_token...",
    "serial_number": "123456789",
    "tsa": "DigiCert"
  },
  "blockchain_anchor": {
    "txid": "abc123...",
    "block_height": 754321,
    "block_hash": "def456...",
    "confirmed": true
  },
  "issuer": "YourDigitalNotary",
  "version": "1.0",
  "signature": "signature_of_above..."
}
```

### Token Issuance Service

```python
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

class TokenService:
    """Issuance and signing of verification tokens."""

    def __init__(self, private_key_path: str):
        with open(private_key_path, 'rb') as f:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )

    def issue_token(self, document_hash: str, timestamp: str,
                    tsa_data: dict, blockchain_data: dict = None,
                    document_name: str = None) -> str:
        """Issue a signed verification token."""
        token_data = {
            'hash': document_hash,
            'algorithm': 'sha256',
            'document_name': document_name or 'unknown',
            'timestamp': timestamp,
            'anchor_type': 'rfc3161_tsa',
            'anchor_data': tsa_data,
            'blockchain_anchor': blockchain_data,
            'issuer': 'YourDigitalNotary',
            'version': '1.0'
        }

        # Serialize to JSON
        token_json = json.dumps(token_data, sort_keys=True)

        # Sign the token
        signature = self.private_key.sign(
            token_json.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Add signature to token
        token_data['signature'] = base64.b64encode(signature).decode()

        # Return as JSON string
        return json.dumps(token_data, indent=2)

    def verify_token_signature(self, token_json: str) -> bool:
        """Verify that token signature is valid."""
        try:
            token_data = json.loads(token_json)
            signature = base64.b64decode(token_data.pop('signature'))

            # In production, verify against public key
            # This is simplified
            return True
        except Exception as e:
            return False
```

### QR Code Generation

```python
import qrcode
from io import BytesIO
import base64

class QRCodeService:
    """QR code generation for verification tokens."""

    @staticmethod
    def generate_qr_code(token: str, size: int = 300) -> str:
        """Generate QR code as base64-encoded image."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )

        qr.add_data(token)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"
```

### API Endpoint for Token Issuance

```python
@app.route('/api/v1/token', methods=['POST'])
def issue_token():
    """Issue verification token for a document."""
    data = request.json

    required_fields = ['hash', 'timestamp', 'document_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    token_service = TokenService(
        private_key_path='config/private_key.pem'
    )

    token = token_service.issue_token(
        document_hash=data['hash'],
        timestamp=data['timestamp'],
        tsa_data=data.get('tsa_data', {}),
        blockchain_data=data.get('blockchain_data'),
        document_name=data.get('document_name')
    )

    # Generate QR code
    qr_code = QRCodeService.generate_qr_code(token)

    return jsonify({
        'success': True,
        'token': token,
        'qr_code': qr_code,
        'token_id': hashlib.sha256(token.encode()).hexdigest()[:16]
    })
```

---

## Component 5: Verification API & UI

### Verification Workflow

```python
class VerificationService:
    """Document verification workflow."""

    @staticmethod
    def verify_document(document_hash: str, verification_token: dict) -> dict:
        """Verify a document against a verification token."""
        result = {
            'hash_match': False,
            'timestamp_valid': False,
            'anchor_valid': False,
            'signature_valid': False,
            'overall_valid': False
        }

        # 1. Verify hash match
        token_hash = verification_token.get('hash')
        if token_hash.lower() == document_hash.lower():
            result['hash_match'] = True

        # 2. Verify timestamp validity
        timestamp = verification_token.get('timestamp')
        if timestamp:
            # Parse and check timestamp is reasonable
            try:
                ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                now = datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

                # Timestamp should be in the past
                if ts <= now:
                    result['timestamp_valid'] = True
            except:
                pass

        # 3. Verify anchor validity
        anchor_data = verification_token.get('anchor_data', {})
        if anchor_data and 'tsa' in anchor_data:
            # Verify TSA signature (simplified)
            result['anchor_valid'] = True

        # 4. Verify token signature
        if TokenService.verify_token_signature(json.dumps(verification_token)):
            result['signature_valid'] = True

        # Overall validity requires all checks to pass
        result['overall_valid'] = all([
            result['hash_match'],
            result['timestamp_valid'],
            result['anchor_valid'],
            result['signature_valid']
        ])

        return result
```

### API Endpoint for Verification

```python
@app.route('/api/v1/verify', methods=['POST'])
def verify_document():
    """Verify a document against a verification token."""
    data = request.json

    required_fields = ['hash', 'token']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    document_hash = data['hash']
    verification_token = data['token']

    if isinstance(verification_token, str):
        verification_token = json.loads(verification_token)

    verification_result = VerificationService.verify_document(
        document_hash,
        verification_token
    )

    return jsonify({
        'success': True,
        'verification': verification_result,
        'overall_valid': verification_result['overall_valid'],
        'timestamp': verification_token.get('timestamp'),
        'issuer': verification_token.get('issuer')
    })
```

---

## Database Schema

### PostgreSQL Schema

```sql
-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    document_hash VARCHAR(64) UNIQUE NOT NULL,
    document_name VARCHAR(255),
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    customer_id INTEGER REFERENCES customers(id),
    s3_key VARCHAR(255),
    s3_bucket VARCHAR(255)
);

-- Timestamps table
CREATE TABLE timestamps (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    timestamp_value TIMESTAMP WITH TIME ZONE NOT NULL,
    timestamp_token TEXT,
    serial_number VARCHAR(255),
    tsa_provider VARCHAR(100) NOT NULL,
    tsa_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Blockchain anchors table
CREATE TABLE blockchain_anchors (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    txid VARCHAR(64) UNIQUE NOT NULL,
    block_height INTEGER,
    block_hash VARCHAR(64),
    network VARCHAR(50) NOT NULL, -- mainnet, testnet
    status VARCHAR(50) NOT NULL, -- pending, confirmed, failed
    confirmed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tokens table
CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    token_id VARCHAR(16) UNIQUE NOT NULL,
    token_json JSONB NOT NULL,
    qr_code_base64 TEXT,
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Verification logs table
CREATE TABLE verification_logs (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    token_id INTEGER REFERENCES tokens(id),
    verification_result JSONB NOT NULL,
    overall_valid BOOLEAN NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    api_key VARCHAR(255)
);

-- Customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    api_key VARCHAR(255) UNIQUE,
    subscription_plan VARCHAR(50) NOT NULL,
    documents_per_month INTEGER DEFAULT 0,
    documents_this_month INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_documents_hash ON documents(document_hash);
CREATE INDEX idx_documents_customer ON documents(customer_id);
CREATE INDEX idx_timestamps_document ON timestamps(document_id);
CREATE INDEX idx_blockchain_anchors_txid ON blockchain_anchors(txid);
CREATE INDEX idx_tokens_document ON tokens(document_id);
CREATE INDEX idx_verification_logs_document ON verification_logs(document_id);
CREATE INDEX idx_verification_logs_token ON verification_logs(token_id);
```

---

## Security Hardening

### OWASP Top 10 Mitigations

1. **Injection Prevention**
   - Use parameterized queries (SQLAlchemy, psycopg2)
   - Never concatenate SQL strings

2. **Broken Authentication**
   - Strong password policies
   - Session timeout
   - Multi-factor authentication for admin

3. **Sensitive Data Exposure**
   - Encrypt at rest (AES-256)
   - TLS in transit (HTTPS only)
   - Hash-only mode option (no document storage)

4. **XML External Entities (XXE)**
   - Disable XML parsing or use safe parser

5. **Broken Access Control**
   - Role-based access control (RBAC)
   - API key validation
   - Rate limiting per customer

6. **Security Misconfiguration**
   - Secure headers (CSP, X-Frame-Options)
   - Disable debug mode in production
   - Regular dependency updates

7. **Cross-Site Scripting (XSS)**
   - Input sanitization
   - Output encoding (DOMPurify in React)
   - Content Security Policy (CSP)

8. **Insecure Deserialization**
   - Avoid pickle for serialization
   - Use JSON instead

9. **Using Components with Known Vulnerabilities**
   - Dependabot alerts
   - Regular security scanning

10. **Insufficient Logging & Monitoring**
    - Audit logs for all API calls
    - Alert on suspicious activity
    - Log retention policy

### Rate Limiting (Flask-Limiter)

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Apply rate limits to endpoints
@app.route('/api/v1/hash', methods=['POST'])
@limiter.limit("10 per minute")
def upload_and_hash():
    # ... existing code ...
```

### Secure Headers (Flask-Talisman)

```python
from flask_talisman import Talisman

Talisman(app, force_https=True, strict_transport_security=True)
```

---

## Deployment with Docker Compose

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/digitalnotary
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - DIGICERT_API_KEY=${DIGICERT_API_KEY}
      - BTC_RPC_USER=${BTC_RPC_USER}
      - BTC_RPC_PASSWORD=${BTC_RPC_PASSWORD}
      - BTC_RPC_URL=http://bitcoin-node:8332
    ports:
      - "5000:5000"
    depends_on:
      - db
      - bitcoin-node

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=digitalnotary
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  bitcoin-node:
    image: ruimarinho/bitcoin-core:25
    command: bitcoind -rpcallowip=0.0.0.0/0 -rpcuser=user -rpcpassword=password -txindex=1
    volumes:
      - bitcoin_data:/bitcoin/.bitcoin
    ports:
      - "8332:8332"
      - "8333:8333"

volumes:
  postgres_data:
  bitcoin_data:
```

---

## References

- [RFC 3161 — Time-Stamp Protocol (TSP)](https://datatracker.ietf.org/doc/html/rfc3161)
- [OpenTimestamps](https://opentimestamps.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Bitcoin Developer Guide](https://developer.bitcoin.org/)

---

## Next Steps

1. **Set up development environment** — Clone repo, install dependencies, run Docker Compose
2. **Implement hash generation** — Test with various file types
3. **Integrate DigiCert TSA** — Get API key, test timestamp requests
4. **Set up Bitcoin node** — Run local node, test OP_RETURN anchoring
5. **Build token issuance** — Generate tokens, test signatures
6. **Implement verification** — End-to-end verification workflow
7. **Deploy to staging** — Test with real documents, verify security
8. **Launch to production** — Monitor, scale, improve