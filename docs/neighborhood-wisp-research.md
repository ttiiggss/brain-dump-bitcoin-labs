# Neighborhood Internet Sharing — WISP (Wireless Internet Service Provider) Research

**Goal:** Rent out your internet connection to a small neighborhood community. What you need to know: hardware, legal/regulatory, technical implementation, pricing, scalability, risks.

---

## What Is a Neighborhood WISP?

A **WISP (Wireless Internet Service Provider)** is a localized ISP that uses wireless technology to deliver internet access to a defined area. In this case, you'd be sharing your existing high-speed residential/business internet connection with nearby neighbors via wireless links.

### The Basic Concept
1. **You have:** 1-2 Gbps fiber connection to your house
2. **Neighbors want:** Faster/cheaper internet than current ISP
3. **Solution:** Point-to-point or mesh wireless links to distribute your bandwidth
4. **Model:** Charge neighbors monthly for access, cover your costs, profit margin

---

## Legal & Regulatory Considerations

### The Big Question: Is This Legal?

**Short Answer:** **Depends on your jurisdiction and ISP's Terms of Service (ToS).**

| Jurisdiction | Legality | Notes |
|-------------|----------|-------|
| **USA** | Generally **legal** with caveats | Reselling residential internet typically violates ISP ToS. Check your ISP's agreement. Some explicitly forbid "sharing" or "reselling" without a business account. |
| **Australia** | Generally **legal** | ACCC hasn't explicitly banned it, but ISP ToS may prohibit it. Check with your ISP. |
| **UK** | Generally **legal** | Ofcom allows it, but ISP ToS may restrict. Many ISPs have "business use" clauses. |
| **Canada** | Generally **legal** | CRTC allows it, ISP ToS varies. Check for "residential use only" clauses. |
| **EU** | Generally **legal** | EU regulations support competition, but national laws vary. ISP ToS is key. |

### ToS Red Flags to Check For
Look for clauses like:
- "Service is for **residential use only**"
- "**Not for resale** or sharing"
- "**Commercial use** prohibited without business account"
- "Subscriber shall **not** provide service to third parties"
- "**Network sharing** prohibited"

### ISP Tiers and ToS Variance
| ISP Type | ToS on Sharing | Risk Level |
|----------|----------------|------------|
| **Residential** | Usually prohibits sharing | 🔴 High — may violate ToS |
| **Business** | Usually allows reselling | 🟢 Low — designed for this |
| **Mixed** | Varies by plan | 🟡 Medium — check specific plan |

### Mitigation Strategies
1. **Upgrade to a business account** — This explicitly allows reselling and often comes with:
   - Static IPs
   - Better SLA (uptime guarantees)
   - Higher bandwidth caps or unlimited
   - Support for commercial use

2. **Check for "community ISPs"** — Some ISPs (especially local cooperatives) actively encourage neighborhood sharing

3. **Contact your ISP directly** — Ask: "I want to share my connection with neighbors — is there a business plan that allows this?" They may offer a solution.

4. **Use your ISP's authorized reseller program** — Some ISPs have formal partner programs for reselling

---

## Hardware Requirements

### Your Connection (The Source)
- **Minimum:** 500 Mbps down / 100 Mbps up
- **Recommended:** 1 Gbps down / 500 Mbps up (fiber)
- **Ideal:** 2 Gbps symmetric (for 10+ households)

### Wireless Distribution Options

#### Option 1: Point-to-Point (PtP) Links — Best for Direct Neighbors
| Hardware | Range | Bandwidth | Approx Cost |
|----------|-------|-----------|-------------|
| Ubiquiti NanoStation 5AC Loco | 5-10 km | 450 Mbps | $100-150 |
| Ubiquiti airMAX AC | 10-15 km | 450 Mbps | $200-300 |
| MikroTik Wireless Wire | 100 m | 1 Gbps | $50-80 |
| Cambium Networks | 10-20 km | 500 Mbps | $250-400 |

**How it works:** Install a small antenna on your roof, point it at neighbor's house. They install a receiver. Line-of-sight required.

**Pros:** High bandwidth, low latency, simple setup
**Cons:** Line-of-sight required, limited to direct neighbors (not good for scattered houses)

#### Option 2: Mesh Network — Best for Scattered Neighborhood
| Hardware | Range | Bandwidth | Approx Cost |
|----------|-------|-----------|-------------|
| GL.iNet Beryl (Wi-Fi 6) | 50-100 m | 1 Gbps | $60-80 |
| OpenWrt-compatible router | 50-100 m | 600 Mbps | $40-100 |
| Ubiquiti UniFi Mesh | 50-100 m | 600 Mbps | $150-200 |
| TP-Link Deco Mesh | 50-100 m | 1 Gbps | $200-300 |

**How it works:** Nodes hop from house to house, extending coverage. Each node acts as a repeater.

**Pros:** Good coverage, no strict line-of-sight required
**Cons:** Bandwidth degrades with each hop, more complex setup

#### Option 3: Point-to-Multi-Point (PtMP) — Best for Many Nearby Houses
| Hardware | Range | Bandwidth | Approx Cost |
|----------|-------|-----------|-------------|
| Ubiquiti airMAX Sector | 120° | 400 Mbps | $300-500 |
| Mimosa B5c | 120° | 500 Mbps | $400-600 |
| Cambium Force 300 | 90° | 300 Mbps | $350-450 |

**How it works:** One high-gain sector antenna on your roof serves multiple neighbors simultaneously.

**Pros:** Efficient for many nearby houses (5-20)
**Cons:** Requires elevated installation, alignment critical

---

## Technical Implementation

### Network Architecture

```
Your Main Router (ISP Connection)
    │
    ├─→ VLAN 10 (Your LAN) — Your devices only
    │
    ├─→ VLAN 20 (WISP Network) — Neighbor access
    │   ├─→ AP 1 (Neighbor A)
    │   ├─→ AP 2 (Neighbor B)
    │   └─→ AP 3 (Neighbor C)
    │
    └─→ VLAN 30 (Management) — Router/AP management access only
```

### Key Components

1. **VLANs (Virtual LANs)**
   - Separate your traffic from neighbor traffic
   - Prevent neighbors from accessing your devices
   - Enable QoS (quality of service) per VLAN

2. **QoS (Quality of Service)**
   - Ensure your traffic gets priority
   - Cap neighbor bandwidth to prevent abuse
   - Typical settings: Your VLAN = 70% bandwidth, Neighbors = 30%

3. **Firewall Rules**
   - Block inter-VLAN communication (neighbors can't see each other's devices)
   - Allow only necessary ports (80, 443, 53 for basic internet)
   - Consider blocking P2P to prevent abuse

4. **Authentication**
   - RADIUS server for centralized authentication (Scalable)
   - Simple WPA2-Enterprise (for small scale)
   - Or pre-shared keys (simplest, but less secure)

### Recommended Hardware Stack

| Component | Recommendation | Approx Cost |
|-----------|----------------|-------------|
| **Main Router** | Ubiquiti EdgeRouter 4 / MikroTik CCR1009 | $200-400 |
| **Access Points (WISP)** | Ubiquiti NanoStation 5AC Loco (PtP) or GL.iNet Beryl (mesh) | $60-150 per node |
| **Switch** | PoE switch for AP power | $50-150 |
| **Mounting** | Roof mounts, cables, lightning arrestors | $50-100 per node |
| **Management** | UniFi Controller or MikroTik RouterOS | Free or $150 |

---

## Pricing Model

### Calculating Your Costs

| Cost Item | Monthly Cost | Notes |
|-----------|--------------|-------|
| **ISP Connection** | $80-150 | Residential (risk) or business (allowed) |
| **Electricity** | $10-30 | Routers/APs running 24/7 |
| **Maintenance** | $20-50 | Time to troubleshoot + equipment amortization |
| **Support** | $10-30 | Time to help neighbors |
| **Total Monthly** | $120-260 | Excluding initial hardware purchase |

### Pricing Scenarios

#### Scenario 1: Small (3-5 neighbors)
- **Your costs:** $120-200/month
- **Pricing:** $40-60/neighbor/month
- **Revenue:** $120-300/month (3-5 neighbors)
- **Breakeven:** 3-4 neighbors
- **Profit margin:** 0-30%

#### Scenario 2: Medium (6-10 neighbors)
- **Your costs:** $180-260/month
- **Pricing:** $35-50/neighbor/month
- **Revenue:** $210-500/month (6-10 neighbors)
- **Breakeven:** 5-6 neighbors
- **Profit margin:** 15-50%

#### Scenario 3: Large (11-20 neighbors)
- **Your costs:** $250-400/month (may need business account)
- **Pricing:** $25-40/neighbor/month
- **Revenue:** $275-800/month (11-20 neighbors)
- **Breakeven:** 8-10 neighbors
- **Profit margin:** 25-70%

### Competitive Pricing

Compare to local ISPs:
- If local ISP charges $70-100/month for 100 Mbps
- You offer 100-200 Mbps for $40-60/month
- **Value proposition:** Faster, cheaper, local support

---

## Scalability

### What Limits Scale?

| Limit | Impact | Mitigation |
|-------|--------|------------|
| **Bandwidth** | Too many neighbors → congestion | Upgrade ISP plan, cap per-user bandwidth |
| **Number of APs** | More nodes → more management | Use UniFi or similar centralized management |
| **Line-of-sight** | Obstructions → weak signal | Use mesh or strategic AP placement |
| **Legal** | ISP ToS violation | Upgrade to business account |
| **Support overhead** | Too many neighbors → time sink | Limit initial scale, automate where possible |

### Expansion Path

1. **Start small (3-5 neighbors)** — Test the waters, work out kinks
2. **Add more nodes** — Expand to 10-15 neighbors if initial is successful
3. **Upgrade equipment** — Better APs, PtMP sector antenna for density
4. **Formalize** — If demand is high, consider:
   - Registering as a small ISP
   - Getting a business internet account
   - Offering SLAs (uptime guarantees)

---

## Risks & Mitigation

### Major Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **ISP ToS Violation** | Medium-High | Service termination | Upgrade to business account, check ToS first |
| **Legal Action from ISP** | Low-Medium | Fines, legal costs | Consult local telecom lawyer, use business account |
| **Neighbor Abuse (torrenting, illegal content)** | Medium | Your IP implicated | QoS caps, block P2P, acceptable use policy |
| **Network Congestion** | Medium | Poor customer experience | Bandwidth monitoring, per-user caps |
| **Equipment Failure** | Low-Medium | Service outage | Redundant routers, spare APs on hand |
| **Physical Damage (weather, theft)** | Low | Service outage | Weatherproof enclosures, secure mounts |
| **Privacy/Security Issues** | Medium | Data breach | VLANs, firewall rules, no access to your LAN |

### Mitigation Checklist

- [ ] **Review ISP ToS** — Explicitly check for sharing/reselling clauses
- [ ] **Upgrade to business account** — If allowed, this eliminates most legal risk
- [ ] **VLAN separation** — Prevent neighbors from accessing your devices
- [ ] **QoS bandwidth caps** — Prevent any one neighbor from monopolizing bandwidth
- [ ] **Firewall rules** — Block inter-neighbor communication, restrict ports
- [ ] **Acceptable Use Policy** — Document what's allowed/prohibited (no illegal content, etc.)
- [ ] **Monitoring** — Track bandwidth usage per node, detect abuse early
- [ ] **Redundancy** — Have backup router/AP on hand
- [ ] **Legal review** — If scaling beyond 5-10 neighbors, consult a telecom lawyer

---

## Community Considerations

### Why Do This in the First Place?

**Benefits for you:**
- Cover your internet costs
- Build community
- Learn networking skills
- Potential side income

**Benefits for neighbors:**
- Faster/cheaper internet
- Local support (you're their ISP)
- Community feeling

### How to Pitch to Neighbors

**Elevator pitch:**
> "I've got a 1 Gbps fiber connection. If a few of us split it, we can all get 100-200 Mbps for $40/month instead of paying the big ISP $80 for 100 Mbps. Plus, if something goes wrong, I'm right next door to fix it."

**Key selling points:**
- Faster than current ISP
- Cheaper than current ISP
- Local support (you're their ISP)
- No contracts, month-to-month

### Managing Expectations

**Be upfront about:**
- No 24/7 support (you're not a giant ISP)
- Occasional outages (hardware failures, ISP issues)
- Acceptable use (no illegal content, no abuse)
- What you charge, what they get

---

## Alternatives

### If WISP Feels Risky or Complex

| Alternative | Pros | Cons |
|-------------|------|------|
| **Use a formal reseller program** | ISP-approved, legal, SLA | Lower margins, less control |
| **Collaborative Wi-Fi (shared network)** | Simple, informal | Security risks, less control |
| **Community ISP co-op** | Community-owned, democratic | Requires multiple people to organize |
| **Do nothing** | No risk, no overhead | Missed opportunity, neighbors on expensive plans |

---

## Summary

### Feasibility: **Medium-High** (with business account) / **Low-Medium** (with residential ToS)

### Critical Success Factors

1. **Legal foundation** — Business account or explicit ToS allowance
2. **Hardware investment** — $500-1,000 initial for 3-5 nodes
3. **Technical competence** — Networking, VLANs, QoS, firewalls
4. **Community buy-in** — Need 3-5 initial neighbors to make it viable
5. **Pricing** — Must beat local ISP on price/performance

### Recommended Path

1. **Check your ISP's ToS** — Look for sharing/reselling clauses
2. **Contact your ISP** — Ask about business plans for reselling
3. **Survey neighbors** — Who's interested? What are they paying now?
4. **Do the math** — Costs, pricing, breakeven point
5. **Start small** — 3-5 neighbors, PtP or simple mesh
6. **Scale up** — Only if initial is successful

---

## References

- [Ubiquiti WISP Solutions](https://www.ui.com/wireless)
- [MikroTik RouterOS Documentation](https://wiki.mikrotik.com/wiki/Manual:TOC)
- [Community Broadband Networks (US FCC)](https://www.fcc.gov/general/community-broadband)
- [WISP Tech Support Forum](https://wispforums.com/)
- [OpenWRT Documentation](https://openwrt.org/)
- [UniFi Controller](https://ui.com/download/unifi)

---

## Next Steps

1. **Review ISP ToS** — Today
2. **Call ISP** — Ask about business reseller programs — This week
3. **Survey 5-10 neighbors** — Find interested parties — Next week
4. **If green light:** Buy 3-5 PtP units (Ubiquiti NanoStation or similar) — ~$300-600
5. **Set up test network** — 2-3 neighbors first — 1-2 weeks
6. **Evaluate** — Costs, bandwidth, customer satisfaction — Ongoing
7. **Scale or pivot** — Based on results — After 1-2 months