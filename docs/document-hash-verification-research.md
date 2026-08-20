# Document Hash Verification — Digital Notary Business

**Goal:** A service for signatures and sensitive documents backed by SHA-256 hash verification. Prove document authenticity, detect tampering, timestamp records.

---

## The Core Concept

### What It Is

A **Digital Notary Service** that:

1. **Documents are uploaded** (PDFs, images, Word docs, scanned papers)
2. **SHA-256 hash is computed** from the document bytes
3. **Hash is timestamped** (when was this document first seen?)
4. **Hash is anchored** (blockchain, notary ledger, or trusted timestamp authority)
5. **Verification token is issued** — a proof of authenticity that anyone can verify

### How Verification Works

**Signer uploads document:**
```
Document (PDF, image, etc.)
    ↓
SHA-256(document_bytes) = abc123...
    ↓
Timestamp: 2024-08-13 14:32:15 UTC
    ↓
Anchor: Block 754321 (Bitcoin OP_RETURN) or Notary Ledger
    ↓
Token: abc123... (hash + timestamp + anchor)
```

**Verifier checks authenticity:**
```
Document (suspect version)
    ↓
SHA-256(document_bytes) = xyz789...
    ↓
Compare to token hash:
    - If match: Document is authentic and unchanged
    - If mismatch: Document was tampered with, or this is a different document
```

### Why SHA-256?

| Property | Value | Relevance |
|----------|-------|-----------|
| **One-way** | Cannot reverse hash to original document | Secure — attackers can't forge original |
| **Deterministic** | Same input always produces same output | Reliable verification |
| **Collision-resistant** | Extremely unlikely two documents produce same hash | Authenticity guarantee |
| **Fast** | Computable in milliseconds | Scales for many documents |
| **Industry standard** | Bitcoin, TLS, Git, Merkle trees all use it | Battle-tested, trusted |

---

## Technical Implementation

### Core Components

#### 1. Document Hash Generation

```python
import hashlib

def hash_document(file_path):
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    return hashlib.sha256(file_bytes).hexdigest()

# Example: hash_document('contract.pdf') → 'a1b2c3...'
```

**Why read as binary?** Ensure consistent hashing across systems. Text files with different line endings (CRLF vs LF) would otherwise produce different hashes.

#### 2. Timestamping

Two approaches:

##### Option A: Trusted Timestamp Authority (TSA)
- **What:** RFC 3161 timestamp tokens from a trusted authority
- **Pros:** Widely recognized, legally accepted in many jurisdictions
- **Cons:** Requires trusting a third party, paid service
- **Examples:** DigiCert, GlobalSign, Entrust

**Process:**
```
1. Compute SHA-256 hash
2. Send hash to TSA via HTTP
3. TSA returns signed timestamp token (TST)
4. Token contains: hash + timestamp + TSA signature
5. Store token for verification later
```

**Cost:** $0.10-0.50 per document for basic services

##### Option B: Blockchain Anchoring
- **What:** Write hash to a blockchain (Bitcoin, Ethereum, Arweave, Sia)
- **Pros:** Decentralized, immutable, verifiable by anyone
- **Cons:** Higher cost, slower confirmation, more complex

**Bitcoin OP_RETURN Approach:**
```
1. Compute SHA-256 hash
2. Send microtransaction with hash in OP_RETURN field
3. Wait for block confirmation (10-60 min)
4. Block height + timestamp = proof of existence
5. Verification: anyone can check blockchain for that hash
```

**Cost:** $0.05-0.20 per document (dust transaction fees)

**Arweave/Ethereum Approach:**
```
1. Compute SHA-256 hash
2. Store hash on Arweave (permanent storage) or Ethereum (contract)
3. Transaction ID = anchor
4. Verification: query blockchain/arweave for hash
```

**Cost:** $0.10-0.50 per document (network fees)

#### 3. Token Issuance

After hashing + timestamping + anchoring, issue a **verification token**:

**Token Structure (JSON):**
```json
{
  "hash": "a1b2c3d4e5f6...",
  "algorithm": "sha256",
  "document_name": "contract.pdf",
  "timestamp": "2024-08-13T14:32:15Z",
  "anchor_type": "bitcoin_op_return",
  "anchor_data": {
    "txid": "abc123...",
    "block_height": 754321,
    "block_timestamp": "2024-08-13T14:32:20Z"
  },
  "issuer": "YourDigitalNotary",
  "signature": "signature_of_above"
}
```

**Token Delivery:**
- QR code (for print verification)
- JSON file (digital)
- Verifiable credential (DID/VC standard)

#### 4. Verification Workflow

**For verifiers (clients, lawyers, auditors):**

```
1. Obtain suspect document + verification token
2. Hash suspect document: SHA-256(document) = xyz789...
3. Read token hash: a1b2c3...
4. Compare:
   - If a1b2c3 == xyz789: Document is authentic
   - If mismatch: Document was tampered with
5. Verify anchor: Check blockchain/TSA for timestamp validity
6. Verify signature: Confirm token was issued by trusted notary
```

---

## Technical Stack

### Minimal Viable Product (MVP)

| Component | Technology | Why |
|-----------|------------|-----|
| **Backend** | Python (Flask/FastAPI) | Easy SHA-256, good libraries |
| **Database** | PostgreSQL | Store hashes, timestamps, tokens |
| **Frontend** | React + Material-UI | Document upload, token generation |
| **Timestamping** | DigiCert TSA (RFC 3161) | Widely recognized, legal acceptance |
| **Backup Anchoring** | Bitcoin OP_RETURN (optional) | Decentralized proof |
| **File Storage** | AWS S3 / DigitalOcean Spaces | Scalable, cheap |
| **Authentication** | Auth0 or Supabase | OAuth2 for user login |

### Alternative: Open-Source Self-Hosted

| Component | Technology | Why |
|-----------|------------|-----|
| **Backend** | Node.js (Express) | JavaScript ecosystem, async/await |
| **Database** | MongoDB | Flexible schema for documents/tokens |
| **Frontend** | Next.js | Full-stack React, fast development |
| **Timestamping** | OpenTimestamps | Free, Bitcoin-anchored timestamps |
| **File Storage** | MinIO (S3-compatible, self-hosted) | Privacy, control |
| **Authentication** | Keycloak or Authentik | Open-source identity |

---

## Use Cases

### 1. Legal Contracts

**Problem:** Contracts get disputed, one party claims "this isn't the original."

**Solution:**
- Both parties upload contract to your notary service
- Hash is timestamped and anchored
- Verification token issued to both parties
- If contract is disputed, hash the disputed version and compare to token

**Benefits:**
- Non-repudiation — "I signed this exact document on this exact date"
- Tamper detection — any change produces different hash
- Legal weight — timestamps are admissible as evidence in many jurisdictions

### 2. Non-Disclosure Agreements (NDAs)

**Problem:** NDAs are violated, but proving the original existed is difficult.

**Solution:**
- NDA is hashed and timestamped upon signing
- Token issued to both parties
- If NDA terms are disputed, verify against token

**Benefits:**
- Proof of existence — "This NDA existed on this date"
- Tamper detection — altered NDAs fail verification
- Chain of custody — track who verified and when

### 3. Wills and Trusts

**Problem:** Wills are contested, authenticity questioned.

**Solution:**
- Will is hashed and timestamped by attorney/notary
- Token stored securely (maybe with key derivation)
- Upon verification, hash current will against token

**Benefits:**
- Reduced disputes — authenticity is provable
- Peace of mind — will can't be secretly altered

### 4. Government Documents (Passports, IDs, Certificates)

**Problem:** Forged documents are hard to detect without original.

**Solution:**
- Government agencies hash official documents and issue public verification tokens
- Anyone can verify a document by hashing and comparing to public token

**Benefits:**
- Instant verification — no need to contact agency
- Reduced fraud — forgeries fail hash check

### 5. Software Licenses

**Problem:** Pirated licenses claim authenticity.

**Solution:**
- Vendor hashes license files and anchors to blockchain
- Software hashes installed license and compares to anchor

**Benefits:**
- Instant validation — software checks license authenticity
- No central server required — blockchain anchor works offline

### 6. Academic Credentials (Diplomas, Certificates)

**Problem:** Fake diplomas and certificates.

**Solution:**
- Institution hashes certificates and issues public verification tokens
- Employers verify by hashing candidate's certificate and checking token

**Benefits:**
- Instant verification — no need to call institution
- Reduced fraud — forgeries fail hash check

---

## Legal Framework

### Where Is Hash-Based Proof Accepted?

| Jurisdiction | Hash Proof Acceptance | Notes |
|-------------|----------------------|-------|
| **USA** | Generally **yes** | E-SIGN Act, UETA accept electronic signatures; timestamps are admissible as evidence |
| **EU** | Generally **yes** | eIDAS Regulation recognizes timestamps and advanced electronic signatures |
| **UK** | Generally **yes** | Electronic Communications Act 2000, GDPR-compliant timestamps |
| **Australia** | Generally **yes** | Electronic Transactions Act 1999, Digital signatures accepted |
| **Canada** | Generally **yes** | Electronic Documents and Acts, Digital signatures recognized |

### Key Legal Concepts

**Non-repudiation:**
- The ability to prove that a party performed an action (signed a document) and cannot deny it
- Hash + timestamp + signature = non-repudiation

**Admissibility as Evidence:**
- Timestamped hashes are admissible as evidence in many jurisdictions
- Requires:
  - Trusted timestamp authority (TSA) or blockchain anchoring
  - Proper chain of custody (who had access to the token)
  - Expert testimony explaining hash verification (if needed)

**Digital Signature Laws:**

| Law | Jurisdiction | Key Provisions |
|-----|-------------|----------------|
| E-SIGN Act | USA | Electronic signatures have same legal weight as wet signatures |
| UETA | USA (state-level) | Uniform Electronic Transactions Act, similar to E-SIGN |
| eIDAS Regulation | EU | Sets standards for electronic signatures and timestamps |
| Electronic Transactions Act | Australia | Recognizes digital signatures and timestamps |
| Electronic Documents and Acts | Canada | Electronic signatures are valid |

### Mitigation: Use Recognized TSAs or Blockchains

To strengthen legal standing:

1. **Use a recognized TSA** — DigiCert, GlobalSign, Entrust
   - Their timestamps are widely accepted in courts
   - They provide audit trails

2. **Use Bitcoin blockchain** — Widely recognized as immutable
   - Block timestamps are publicly verifiable
   - Academic research supports blockchain timestamps as evidence

3. **Obtain notarization** — Combine digital hash with physical notarization
   - Notary witnesses document signing
   - Notary can also sign the hash verification token

---

## Revenue Model

### Pricing Models

| Service | Pricing | Notes |
|----------|---------|-------|
| **Per-document timestamp** | $0.50-2.00 | Basic TSA timestamp |
| **Blockchain anchoring** | $1.00-5.00 | Bitcoin OP_RETURN or Arweave |
| **Full notary package** | $5.00-20.00 | Hash + timestamp + anchor + token + certificate |
| **Bulk pricing** | Discount for 100+ docs | 20-40% off per document |
| **Subscription** | $20-50/month | 50-200 docs/month included |

### Revenue Calculations

#### Scenario 1: Small (10 customers, 5 docs/month each)

| Metric | Value |
|--------|-------|
| Documents/month | 50 |
| Avg price/doc | $5 (full package) |
| Monthly revenue | $250 |
| Annual revenue | $3,000 |

#### Scenario 2: Medium (50 customers, 10 docs/month each)

| Metric | Value |
|--------|-------|
| Documents/month | 500 |
| Avg price/doc | $3 (discounted bulk) |
| Monthly revenue | $1,500 |
| Annual revenue | $18,000 |

#### Scenario 3: Large (200 customers, 20 docs/month each)

| Metric | Value |
|--------|-------|
| Documents/month | 4,000 |
| Avg price/doc | $2 (subscription pricing) |
| Monthly revenue | $8,000 |
| Annual revenue | $96,000 |

### Cost Structure

| Cost Item | Monthly Cost | Notes |
|-----------|--------------|-------|
| **TSA service** | $0.10-0.50 per doc | $40-200 (400 docs) |
| **Blockchain fees** | $0.05-0.20 per doc | $20-80 (400 docs) |
| **Hosting** | $20-100 | Cloud hosting, database |
| **Storage** | $10-30 | AWS S3/DO Spaces (400 docs) |
| **Development** | $500-2,000 | Initial build, ongoing maintenance |
| **Legal consultation** | $200-500 | Initial legal review |
| **Support** | $100-300 | Customer support time |
| **Total Monthly** | $870-3,210 | For medium scale (400 docs/month) |

### Breakeven

At medium scale (400 docs/month, $1,500 revenue, $870-3,210 costs):

- **Low end:** Breakeven at ~300 docs/month
- **High end:** Breakeven at ~800 docs/month

**Tip:** Offer blockchain anchoring as a premium add-on (+$2-3/doc) — higher margin.

---

## Scalability

### What Limits Scale?

| Limit | Impact | Mitigation |
|-------|--------|------------|
| **Document size** | Large files take longer to hash | Chunked hashing, background jobs |
| **Storage** | Many documents = high storage cost | Object storage (S3), archive old docs |
| **Timestamp latency** | TSA/blockchain confirmation time | Async processing, provide provisional token |
| **Verification load** | Many verifications = server load | CDN for tokens, database caching |
| **Legal disputes** | Complex cases require expert testimony | Have legal partner, FAQ for common disputes |

### Expansion Path

1. **Start small (50-100 docs/month)** — Validate demand, work out kinks
2. **Add blockchain anchoring** — Premium service, higher margin
3. **Integrate with existing tools** — Browser extensions for PDF hashing, mobile apps for on-the-go verification
4. **Target specific industries** — Legal firms, real estate, government, academia
5. **Build partnerships** — With law firms, notaries, government agencies

---

## Risks & Mitigation

### Major Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Legal challenges** | Medium | Lawsuits over document authenticity | Use recognized TSAs, blockchain anchoring, legal review |
| **Hash collision attacks** | Extremely low | Forge authentic-looking documents | SHA-256 is collision-resistant, regular audits |
| **Data breaches** | Low-Medium | Exposed document hashes, privacy concerns | Encrypt at rest, minimal data retention, GDPR compliance |
| **TSA or blockchain downtime** | Low | Cannot timestamp/anchor | Multiple TSAs, multiple blockchains as backup |
| **Competitive pressure** | Medium | Larger players enter market | Focus on niche (e.g., legal contracts), better UX |
| **Regulatory changes** | Low-Medium | New laws affecting digital notarization | Stay informed, adapt, legal review |

### Mitigation Checklist

- [ ] **Use recognized TSAs** — DigiCert, GlobalSign, Entrust
- [ ] **Add blockchain anchoring** — Bitcoin OP_RETURN or Arweave for redundancy
- [ ] **Encrypt at rest** — AES-256 for stored documents/tokens
- [ ] **Minimal data retention** — Store only hash + timestamp, not full document (optional)
- [ ] **GDPR/privacy compliance** — Clear privacy policy, data deletion options
- [ ] **Regular audits** — Test hash collisions, verify timestamps
- [ ] **Legal partnership** — Have lawyer review processes, provide expert testimony
- [ ] **Disaster recovery** — Backup database, redundancy for TSAs/blockchains

---

## Alternatives

### Existing Solutions

| Service | Pros | Cons |
|---------|------|------|
| **DocuSign** | Industry standard, integrated workflows | Expensive, closed-source, vendor lock-in |
| **Adobe Sign** | PDF-native, widely accepted | Proprietary, no blockchain anchoring |
| **OpenTimestamps** | Free, Bitcoin-anchored | No UI, self-hosted, technical |
| **OriginStamp** | Blockchain-anchored, multiple chains | Limited features, paid |
| **Factom** | Enterprise, blockchain-backed | Expensive, not consumer-facing |

### Competitive Positioning

**Your advantage:**
- **Flexibility** — Offer both TSA and blockchain options
- **Privacy-focused** — Optional document storage (hash-only mode)
- **Niche specialization** — Focus on legal contracts, NDAs, wills
- **Developer API** — Easy integration for other tools

---

## Summary

### Feasibility: **High**

### Critical Success Factors

1. **Legal foundation** — Recognized TSAs, blockchain anchoring, legal review
2. **Technical competence** — SHA-256 hashing, timestamp protocols, blockchain integration
3. **Market demand** — Legal firms, real estate, government, academia need this
4. **Pricing** — Must be competitive with existing solutions
5. **Trust** — Recognized TSAs, blockchain anchoring, transparency

### Recommended Path

1. **Legal review** — Confirm hash-based timestamps are admissible in your jurisdiction — This week
2. **Choose timestamp provider** — DigiCert (TSA) + OpenTimestamps (blockchain backup) — Next week
3. **Build MVP** — Simple web app: upload → hash → timestamp → token — 2-3 weeks
4. **Beta testing** — 10-20 users, free, gather feedback — 1-2 months
5. **Launch** — Paid service, focus on legal contracts/NDAs — Month 4
6. **Scale** — Add blockchain anchoring, mobile apps, integrations — Ongoing

---

## References

- [RFC 3161 — Time-Stamp Protocol (TSP)](https://datatracker.ietf.org/doc/html/rfc3161)
- [DigiCert Timestamping](https://www.digicert.com/secure-documents/digital-signatures/timestamping)
- [OpenTimestamps (Bitcoin-anchored timestamps)](https://opentimestamps.org/)
- [eIDAS Regulation (EU)](https://digital-strategy.ec.europa.eu/en/policies/trust-services-and-eidentification/)
- [E-SIGN Act (USA)](https://www.gpo.gov/fdsys/pkg/PLAW-106publ299/html/PLAW-106publ299.htm)
- [UETA (USA state-level)](https://uniformlaws.org/committees/community/home?search=UETA)
- [Digital Signature Laws by Country](https://docusign.com/au/docusign-resource-center/ask/expert/what-is-a-digital-signature)

---

## Next Steps

1. **Legal review** — Consult telecom/digital signature lawyer in your jurisdiction — This week
2. **Choose TSA provider** — DigiCert, GlobalSign, or Entrust — Next week
3. **Set up OpenTimestamps** — Free Bitcoin-anchored timestamps as backup — Next week
4. **Build MVP** — Document upload + hash generation + timestamp + token — 2-3 weeks
5. **Beta testing** — 10-20 users, free, gather feedback — 1-2 months
6. **Launch** — Paid service, target legal firms, real estate, government — Month 4
7. **Scale** — Blockchain anchoring, mobile apps, industry-specific features — Ongoing